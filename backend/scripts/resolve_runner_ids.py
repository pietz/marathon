# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///
"""Resolve mika internal runner IDs from bib numbers for Hamburg Marathon 2026."""

import json

import httpx

URL = "https://hamburg.r.mikatiming.de/2026/index.php"

RUNNERS = [
    {"name": "Tobi", "bib": "13538"},
    {"name": "Kevin", "bib": "13533"},
    {"name": "Jonas", "bib": "13532"},
    {"name": "Alex", "bib": "13536"},
]


def search(bib: str) -> dict:
    data = {
        "content": "ajax2",
        "func": "getSearchResult",
        "options[string]": bib,
        "options[pid]": "quicksearch",
        "options[option_bar][event_main_group]": "custom.meeting.marathon",
        "options[option_bar][event]": "HML_HCHSK2IQ885",
        "options[event]": "",
        "onpage": "tracking",
    }
    r = httpx.post(URL, data=data, timeout=20.0)
    r.raise_for_status()
    return r.json()


def main() -> None:
    for runner in RUNNERS:
        print(f"\n=== {runner['name']} (bib {runner['bib']}) ===")
        try:
            result = search(runner["bib"])
            print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
        except Exception as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
