import logging
import os
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from . import mika
from .logging_config import request_id_var, setup_logging

setup_logging()
logger = logging.getLogger("marathon")

app = FastAPI(title="Marathon API")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        token = request_id_var.set(rid)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "unhandled error",
                extra={"method": request.method, "path": request.url.path},
            )
            request_id_var.reset(token)
            raise
        ms = (time.perf_counter() - start) * 1000
        # Skip the noisy SvelteKit static-asset chatter from access logs.
        if not request.url.path.startswith("/_app/"):
            extra = {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(ms),
            }
            log = (
                logger.error
                if response.status_code >= 500
                else logger.warning
                if response.status_code >= 400
                else logger.info
            )
            log(f"{request.method} {request.url.path} {response.status_code}", extra=extra)
        request_id_var.reset(token)
        response.headers["x-request-id"] = rid
        return response


app.add_middleware(LoggingMiddleware)

STATIC_DIR = Path(__file__).resolve().parent.parent / "build"

LIVE_CACHE_TTL = 12.0
ROUTE_CACHE_TTL = 6 * 3600.0
SEARCH_CACHE_TTL = 60.0
RUNNERS_CACHE_TTL = 12.0
MAX_IDS = 12

_live_cache: dict = {"ts": 0.0, "data": None}
_route_cache: dict = {"ts": 0.0, "data": None}
_search_cache: dict[str, tuple[float, list]] = {}
_runners_cache: dict[tuple[str, ...], tuple[float, dict]] = {}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/live")
def live():
    now = time.monotonic()
    if _live_cache["data"] and now - _live_cache["ts"] < LIVE_CACHE_TTL:
        return _live_cache["data"]
    try:
        data = mika.get_live()
    except Exception as e:
        if _live_cache["data"]:
            return _live_cache["data"]
        raise HTTPException(status_code=502, detail=f"mika fetch failed: {e}") from e
    _live_cache["ts"] = now
    _live_cache["data"] = data
    return data


@app.get("/api/route")
def route():
    now = time.monotonic()
    if _route_cache["data"] and now - _route_cache["ts"] < ROUTE_CACHE_TTL:
        return {"route": _route_cache["data"]}
    try:
        data = mika.get_route()
    except Exception as e:
        if _route_cache["data"]:
            return {"route": _route_cache["data"]}
        raise HTTPException(status_code=502, detail=f"mika fetch failed: {e}") from e
    _route_cache["ts"] = now
    _route_cache["data"] = data
    return {"route": data}


@app.get("/api/search")
def search(q: str = Query(min_length=2, max_length=64)):
    key = q.strip().lower()
    if not key:
        return {"results": []}
    now = time.monotonic()
    cached = _search_cache.get(key)
    if cached and now - cached[0] < SEARCH_CACHE_TTL:
        return {"results": cached[1]}
    try:
        results = mika.search(key)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"mika search failed: {e}") from e
    _search_cache[key] = (now, results)
    if len(_search_cache) > 200:
        oldest = sorted(_search_cache.items(), key=lambda kv: kv[1][0])[:50]
        for k, _ in oldest:
            _search_cache.pop(k, None)
    return {"results": results}


@app.get("/api/runners")
def runners(bibs: str = Query(min_length=1, max_length=256)):
    bib_list = [s.strip() for s in bibs.split(",") if s.strip()]
    if not bib_list:
        raise HTTPException(status_code=400, detail="no bibs provided")
    if len(bib_list) > MAX_IDS:
        raise HTTPException(status_code=400, detail=f"too many bibs (max {MAX_IDS})")

    # Resolve bibs -> internal mika IDs (cached forever per process).
    bib_to_id = mika.resolve_bibs(bib_list)
    if not bib_to_id:
        return {"lastUpdate": None, "runners": []}

    ids = list(bib_to_id.values())
    key = tuple(sorted(set(ids)))
    now = time.monotonic()
    cached = _runners_cache.get(key)
    if cached and now - cached[0] < RUNNERS_CACHE_TTL:
        data = cached[1]
    else:
        try:
            data = mika.get_runners(list(key))
        except Exception as e:
            if cached:
                data = cached[1]
            else:
                raise HTTPException(status_code=502, detail=f"mika fetch failed: {e}") from e
        _runners_cache[key] = (now, data)
        if len(_runners_cache) > 500:
            oldest = sorted(_runners_cache.items(), key=lambda kv: kv[1][0])[:100]
            for k, _ in oldest:
                _runners_cache.pop(k, None)

    by_bib = {r["bib"]: r for r in data["runners"] if r.get("bib")}
    # Preserve client-provided bib order; drop unresolved bibs silently.
    return {
        "lastUpdate": data["lastUpdate"],
        "runners": [by_bib[b] for b in bib_list if b in by_bib],
    }


# Serve SvelteKit static build as catch-all (must be last)
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
