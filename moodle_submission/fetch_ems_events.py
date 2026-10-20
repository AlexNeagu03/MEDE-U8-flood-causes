import csv
import json
import re
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "ems_events.csv"
META_FILE = ROOT / "outputs" / "ems_fetch_metadata.json"
API_URL = "https://rapidmapping.emergency.copernicus.eu/backend/dashboard-api/public-activations-info/"


def parse_point_wkt(value: str) -> Tuple[float, float]:
    match = re.match(r"POINT\s*\(([-\d.]+)\s+([-\d.]+)\)", value or "")
    if not match:
        raise ValueError(f"Invalid POINT WKT: {value}")
    lon = float(match.group(1))
    lat = float(match.group(2))
    return lat, lon


def date_from_iso(value: str) -> str:
    return value[:10]


EUROPE_COUNTRIES = {
    "albania",
    "andorra",
    "armenia",
    "austria",
    "azerbaijan",
    "belarus",
    "belgium",
    "bosnia and herzegovina",
    "bulgaria",
    "croatia",
    "cyprus",
    "czechia",
    "denmark",
    "estonia",
    "finland",
    "france",
    "georgia",
    "germany",
    "greece",
    "hungary",
    "iceland",
    "ireland",
    "italy",
    "kosovo",
    "latvia",
    "liechtenstein",
    "lithuania",
    "luxembourg",
    "malta",
    "moldova",
    "monaco",
    "montenegro",
    "netherlands",
    "north macedonia",
    "norway",
    "poland",
    "portugal",
    "romania",
    "san marino",
    "serbia",
    "slovakia",
    "slovenia",
    "spain",
    "sweden",
    "switzerland",
    "turkiye",
    "turkey",
    "ukraine",
    "united kingdom",
    "vatican city",
}


def is_europe_event(item: Dict[str, object]) -> bool:
    countries = item.get("countries", [])
    if not isinstance(countries, list):
        return False
    for country in countries:
        if str(country).strip().lower() in EUROPE_COUNTRIES:
            return True
    return False


def is_flood_event(item: Dict[str, object]) -> bool:
    category = str(item.get("category", "")).strip().lower()
    sub_category = str(item.get("subCategory", "")).strip().lower()
    return category == "flood" or "flood" in sub_category


def fetch_page(limit: int, offset: int) -> Dict[str, object]:
    params = urllib.parse.urlencode({"limit": limit, "offset": offset})
    with urllib.request.urlopen(f"{API_URL}?{params}") as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def fetch_events(max_events: int = 20, max_event_date: str = "2024-12-31") -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    offset = 0
    limit = 100
    max_date_obj = date.fromisoformat(max_event_date)
    while len(rows) < max_events:
        payload = fetch_page(limit=limit, offset=offset)
        results = payload.get("results", [])
        if not isinstance(results, list) or not results:
            break

        for item in results:
            if not isinstance(item, dict):
                continue
            if not is_europe_event(item) or not is_flood_event(item):
                continue
            if "code" not in item or "name" not in item or "eventTime" not in item or "centroid" not in item:
                continue

            try:
                lat, lon = parse_point_wkt(str(item["centroid"]))
            except ValueError:
                continue

            event_date = date_from_iso(str(item["eventTime"]))
            if date.fromisoformat(event_date) > max_date_obj:
                continue
            activation = str(item.get("activationTime", item["eventTime"]))
            activation_date = date_from_iso(activation)
            start_date = min(event_date, activation_date)
            end_date = max(event_date, activation_date)
            if start_date == end_date:
                end_date = start_date

            countries = item.get("countries", [])
            if isinstance(countries, list):
                country = ", ".join(str(c).strip() for c in countries if str(c).strip())
            else:
                country = str(countries).strip()

            code = str(item["code"]).strip()
            name = str(item["name"]).strip()
            category = str(item.get("category", "Flood")).strip()
            sub_category = str(item.get("subCategory", "")).strip()
            hazard_type = f"{category} | {sub_category}" if sub_category else category

            rows.append(
                {
                    "event_id": code,
                    "activation_code": code,
                    "event_name": name,
                    "country": country,
                    "region": "N/A",
                    "start_date": start_date,
                    "end_date": end_date,
                    "hazard_type": hazard_type,
                    "source_url": f"https://mapping.emergency.copernicus.eu/activation/{code}",
                    "event_lat": f"{lat:.6f}",
                    "event_lon": f"{lon:.6f}",
                }
            )
            if len(rows) >= max_events:
                break

        offset += limit

    if not rows:
        raise RuntimeError("No flood events fetched from Copernicus EMS API.")
    return rows


def write_csv(path: Path, rows: Iterable[Dict[str, str]]) -> None:
    fieldnames = [
        "event_id",
        "activation_code",
        "event_name",
        "country",
        "region",
        "start_date",
        "end_date",
        "hazard_type",
        "source_url",
        "event_lat",
        "event_lon",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_metadata(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": date.today().isoformat(),
        "source_api": API_URL,
        "events_written": len(rows),
        "notes": "Only European flood activations from Copernicus EMS Rapid Mapping public API.",
    }
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def main() -> None:
    events = fetch_events(max_events=20, max_event_date="2024-12-31")
    write_csv(OUTPUT_FILE, events)
    write_metadata(META_FILE, events)
    print(f"Saved {len(events)} EMS events to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
