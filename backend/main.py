import os
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

import mika

app = FastAPI(title="Marathon API")

STATIC_DIR = Path(__file__).resolve().parent.parent / "build"

LIVE_CACHE_TTL = 12.0
_live_cache: dict = {"ts": 0.0, "data": None}


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


# Serve SvelteKit static build as catch-all (must be last)
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
