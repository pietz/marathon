"""Mika Timing client for Hamburg Marathon 2026 live tracking."""

import concurrent.futures
from datetime import datetime, timezone
import math

import httpx

BASE = "https://hamburg.r.mikatiming.de/2026"
URL = f"{BASE}/index.php"
EVENT = "HML_HCHSK2IQ885"
EVENT_MAIN_GROUP = "custom.meeting.marathon"

# Used to (a) seed the favorites cookie when fetching just the route and
# (b) keep /api/live behavior unchanged.
RUNNERS = [
    {"name": "Tobi", "bib": "13538", "id": "HCHSK2IQ3A6CDF", "color": "#f1c40f"},
    {"name": "Kevin", "bib": "13533", "id": "HCHSK2IQ3A63EE", "color": "#3498db"},
    {"name": "Jonas", "bib": "13532", "id": "HCHSK2IQ3A95A9", "color": "#e74c3c"},
    {"name": "Alex", "bib": "13536", "id": "HCHSK2IQ3A6380", "color": "#2ecc71"},
]

_HEADERS = {
    "Referer": f"{BASE}/?pid=tracking",
    "User-Agent": "Mozilla/5.0",
}


# ---------- raw mika calls ----------


def fetch_tracking(runner_ids: list[str]) -> dict:
    cookie = "|".join(runner_ids)
    params = {"content": "ajax2", "func": "getLeaderboard", "onpage": "tracking"}
    data = {
        "func": "getLeaderboard",
        "options[lang]": "EN_CAP",
        "options[pid]": "tracking",
        "options[option_bar][event_main_group]": EVENT_MAIN_GROUP,
        "options[option_bar][event]": EVENT,
    }
    headers = {**_HEADERS, "Cookie": f"results_favorites={cookie}"}
    r = httpx.post(URL, params=params, data=data, headers=headers, timeout=30.0)
    r.raise_for_status()
    return r.json()


def fetch_search(query: str) -> list[dict]:
    data = {
        "content": "ajax2",
        "func": "getSearchResult",
        "options[string]": query,
        "options[pid]": "quicksearch",
        "options[option_bar][event_main_group]": EVENT_MAIN_GROUP,
        "options[option_bar][event]": EVENT,
        "options[event]": "",
        "onpage": "tracking",
    }
    r = httpx.post(URL, data=data, headers=_HEADERS, timeout=20.0)
    r.raise_for_status()
    payload = r.json()
    return payload if isinstance(payload, list) else []


# ---------- polyline + km projection ----------


def decode_polyline(s: str, precision: int = 5) -> list[tuple[float, float]]:
    """Google encoded-polyline algorithm, precision-5."""
    coords: list[tuple[float, float]] = []
    index = lat = lng = 0
    factor = 10**precision
    while index < len(s):
        for axis in (0, 1):
            shift = 0
            result = 0
            while True:
                b = ord(s[index]) - 63
                index += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            delta = ~(result >> 1) if (result & 1) else (result >> 1)
            if axis == 0:
                lat += delta
            else:
                lng += delta
        coords.append((lat / factor, lng / factor))
    return coords


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    R = 6371.0088
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    dlat = la2 - la1
    dlon = lo2 - lo1
    h = math.sin(dlat / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def cumulative_km(route: list[tuple[float, float]]) -> list[float]:
    out = [0.0]
    for i in range(1, len(route)):
        out.append(out[-1] + _haversine_km(route[i - 1], route[i]))
    return out


def coordinate_at_km(
    route: list[tuple[float, float]],
    cum: list[float],
    km: float,
) -> tuple[float, float] | None:
    if not route:
        return None
    if km <= 0:
        return route[0]
    if km >= cum[-1]:
        return route[-1]
    for i in range(1, len(cum)):
        if cum[i] >= km:
            seg = cum[i] - cum[i - 1]
            if seg <= 0:
                return route[i]
            t = (km - cum[i - 1]) / seg
            lat = route[i - 1][0] + t * (route[i][0] - route[i - 1][0])
            lng = route[i - 1][1] + t * (route[i][1] - route[i - 1][1])
            return (lat, lng)
    return route[-1]


# ---------- response parsing ----------


_STATE_TO_STATUS = {
    "not_started": "not_started",
    "started": "running",
    "finished": "finished",
    "stopped": "stopped",
}


def _strip_titles(s: str) -> str:
    """Drop leading academic/honorific tokens like 'Dr.', 'Prof.', 'Dipl.-Ing.'."""
    parts = s.strip().split()
    while len(parts) > 1 and parts[0].endswith("."):
        parts = parts[1:]
    return " ".join(parts)


def _split_full_name(full: str | None) -> tuple[str, str]:
    """('Dr. Jonas Fleckner') -> ('Jonas', 'Fleckner'). First non-title word is given name."""
    if not full:
        return "", ""
    cleaned = _strip_titles(full)
    parts = cleaned.split(" ", 1)
    return (parts[0], parts[1] if len(parts) > 1 else "")


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _project_position_km(pos: dict, state: str) -> float:
    km = float(pos.get("pos_km") or 0)
    if state != "started" or pos.get("source") != "estimated_chip":
        return km

    speed_kmh = pos.get("speed_kmh")
    last_change = _parse_datetime(pos.get("datetime_last_change"))
    valid_until = pos.get("valid_until_km")
    if not speed_kmh or not last_change or valid_until is None:
        return km

    now = datetime.now(last_change.tzinfo or timezone.utc)
    elapsed_hours = max(0.0, (now - last_change).total_seconds() / 3600)
    projected = km + float(speed_kmh) * elapsed_hours
    return min(max(km, projected), float(valid_until))


def parse_route(payload: dict) -> list[tuple[float, float]]:
    containers = payload.get("containers", [])
    mp = next((c for c in containers if c.get("type") == "map"), None)
    if not mp:
        return []
    tracks = mp.get("data", {}).get("tracks", {})
    track = tracks.get("m") or next(iter(tracks.values()), None)
    if not track or not track.get("points_encoded"):
        return []
    return decode_polyline(track["points_encoded"])


def parse_runner_rows(payload: dict) -> list[dict]:
    containers = payload.get("containers", [])
    fav = next((c for c in containers if c.get("type") == "favorites"), None)
    if not fav:
        return []
    return fav.get("data", {}).get("rows", []) or []


def project_runner(
    row: dict,
    route: list[tuple[float, float]],
    cum: list[float],
) -> dict:
    pos = row.get("position_data") or {}
    state = pos.get("state") or "unknown"
    km = _project_position_km(pos, state)
    coord = coordinate_at_km(route, cum, km) if route else None
    full = row.get("__fullname")
    first, last = _split_full_name(full)
    splits = [
        {
            "name": s.get("name"),
            "km": s.get("km"),
            "time": s.get("time"),
            "kmh": s.get("kmh") if s.get("kmh") not in ("-", "") else None,
        }
        for s in (row.get("splits") or [])
        if s.get("time") and s.get("time") != "-"
    ]
    return {
        "id": row.get("id"),
        "bib": row.get("start_no"),
        "fullName": full,
        "firstName": first,
        "lastName": last or row.get("name"),
        "club": row.get("club"),
        "sex": row.get("sex"),
        "status": _STATE_TO_STATUS.get(state, state),
        "km": km,
        "speedKmh": pos.get("speed_kmh"),
        "source": pos.get("source"),
        "lastChange": pos.get("daytime_last_change"),
        "validUntilKm": pos.get("valid_until_km"),
        "coordinate": list(coord) if coord else None,
        "splits": splits,
    }


# ---------- public API used by FastAPI endpoints ----------


def get_route() -> list[list[float]]:
    """Fetch only the marathon polyline. Uses our four anchor IDs as the
    favorites cookie since mika requires at least one to populate the map."""
    raw = fetch_tracking([r["id"] for r in RUNNERS])
    return [list(p) for p in parse_route(raw)]


def get_runners(ids: list[str]) -> dict:
    raw = fetch_tracking(ids)
    route = parse_route(raw)
    cum = cumulative_km(route) if route else []
    rows = parse_runner_rows(raw)
    by_id = {row.get("id"): row for row in rows}
    runners = [project_runner(by_id[i], route, cum) for i in ids if i in by_id]
    return {"lastUpdate": raw.get("lastUpdateTs"), "runners": runners}


# Bib → internal mika ID. mika IDs are stable for the event so we cache
# forever (in-memory; resets on process restart).
_bib_id_cache: dict[str, str] = {r["bib"]: r["id"] for r in RUNNERS}


def _resolve_one_bib(bib: str) -> str | None:
    raw = fetch_search(bib)
    for item in raw:
        if str(item.get("start_no")) == str(bib):
            return item.get("id")
    return None


def resolve_bibs(bibs: list[str]) -> dict[str, str]:
    """Return {bib: mika_id} for the bibs we could resolve. Bibs we
    can't find (typo, wrong event) are silently omitted."""
    unresolved = [b for b in bibs if b not in _bib_id_cache]
    if unresolved:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, len(unresolved))) as ex:
            future_to_bib = {ex.submit(_resolve_one_bib, b): b for b in unresolved}
            for fut in concurrent.futures.as_completed(future_to_bib):
                bib = future_to_bib[fut]
                try:
                    rid = fut.result()
                    if rid:
                        _bib_id_cache[bib] = rid
                except Exception:
                    pass
    return {b: _bib_id_cache[b] for b in bibs if b in _bib_id_cache}


def search(query: str) -> list[dict]:
    raw = fetch_search(query)
    out = []
    for item in raw:
        full = item.get("value") or ""
        last, _, first = full.partition(", ")
        first = _strip_titles(first)
        out.append({
            "id": item.get("id"),
            "bib": item.get("start_no"),
            "fullName": f"{first} {last}".strip() if first else full,
            "firstName": first or "",
            "lastName": last or "",
            "club": item.get("club"),
            "sex": (item.get("class") or "").upper() or None,
        })
    return out


# ---------- legacy /api/live (unchanged behavior) ----------


def _normalize_runner(
    row: dict,
    config: dict,
    route: list[tuple[float, float]],
    cum: list[float],
) -> dict:
    base = project_runner(row, route, cum)
    return {
        **base,
        "name": config["name"],
        "color": config["color"],
        "bib": base["bib"] or config["bib"],
    }


def get_live() -> dict:
    raw = fetch_tracking([r["id"] for r in RUNNERS])
    route = parse_route(raw)
    cum = cumulative_km(route) if route else []
    rows = parse_runner_rows(raw)
    by_id = {r["id"]: r for r in RUNNERS}
    runners = []
    for row in rows:
        cfg = by_id.get(row.get("id"))
        if not cfg:
            continue
        runners.append(_normalize_runner(row, cfg, route, cum))
    order = {r["id"]: i for i, r in enumerate(RUNNERS)}
    runners.sort(key=lambda r: order.get(r["id"], 999))
    return {
        "lastUpdate": raw.get("lastUpdateTs"),
        "route": [list(p) for p in route],
        "runners": runners,
    }
