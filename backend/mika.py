"""Mika Timing client for Hamburg Marathon 2026 live tracking."""

import math

import httpx

URL = "https://hamburg.r.mikatiming.de/2026/index.php"
EVENT = "HML_HCHSK2IQ885"
EVENT_MAIN_GROUP = "custom.meeting.marathon"

RUNNERS = [
    {"name": "Tobi", "bib": "13538", "id": "HCHSK2IQ3A6CDF", "color": "#f1c40f"},
    {"name": "Kevin", "bib": "13533", "id": "HCHSK2IQ3A63EE", "color": "#3498db"},
    {"name": "Jonas", "bib": "13532", "id": "HCHSK2IQ3A95A9", "color": "#e74c3c"},
    {"name": "Alex", "bib": "13536", "id": "HCHSK2IQ3A6380", "color": "#2ecc71"},
]


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
    headers = {
        "Cookie": f"results_favorites={cookie}",
        "Referer": "https://hamburg.r.mikatiming.de/2026/?pid=tracking",
        "User-Agent": "Mozilla/5.0",
    }
    r = httpx.post(URL, params=params, data=data, headers=headers, timeout=30.0)
    r.raise_for_status()
    return r.json()


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
    # Binary search would be nicer but linear is fine for 246 points.
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


_STATE_TO_STATUS = {
    "not_started": "not_started",
    "started": "running",
    "finished": "finished",
    "stopped": "stopped",
}


def _normalize_runner(
    row: dict,
    config: dict,
    route: list[tuple[float, float]],
    cum: list[float],
) -> dict:
    pos = row.get("position_data") or {}
    state = pos.get("state") or "unknown"
    km = pos.get("pos_km") or 0
    coord = coordinate_at_km(route, cum, float(km)) if route else None
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
        "name": config["name"],
        "bib": row.get("start_no") or config["bib"],
        "color": config["color"],
        "fullName": row.get("__fullname"),
        "status": _STATE_TO_STATUS.get(state, state),
        "km": float(km) if km is not None else 0.0,
        "speedKmh": pos.get("speed_kmh"),
        "source": pos.get("source"),
        "lastChange": pos.get("daytime_last_change"),
        "validUntilKm": pos.get("valid_until_km"),
        "coordinate": list(coord) if coord else None,
        "splits": splits,
    }


def build_live_payload(payload: dict) -> dict:
    containers = payload.get("containers", [])
    mp = next((c for c in containers if c.get("type") == "map"), None)
    fav = next((c for c in containers if c.get("type") == "favorites"), None)

    route: list[tuple[float, float]] = []
    if mp:
        tracks = mp.get("data", {}).get("tracks", {})
        track = tracks.get("m") or next(iter(tracks.values()), None)
        if track and track.get("points_encoded"):
            route = decode_polyline(track["points_encoded"])
    cum = cumulative_km(route) if route else []

    by_id = {r["id"]: r for r in RUNNERS}
    rows = (fav.get("data", {}).get("rows", []) if fav else []) or []
    runners = []
    for row in rows:
        cfg = by_id.get(row.get("id"))
        if not cfg:
            continue
        runners.append(_normalize_runner(row, cfg, route, cum))

    # Preserve our display order (Tobi, Kevin, Jonas, Alex), even if mika reorders.
    order = {r["id"]: i for i, r in enumerate(RUNNERS)}
    runners.sort(key=lambda r: order.get(r["id"], 999))

    return {
        "lastUpdate": payload.get("lastUpdateTs"),
        "route": [list(p) for p in route],
        "runners": runners,
    }


def get_live() -> dict:
    raw = fetch_tracking([r["id"] for r in RUNNERS])
    return build_live_payload(raw)
