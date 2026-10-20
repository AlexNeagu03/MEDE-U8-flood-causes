import csv
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
EMS_FILE = RAW_DIR / "ems_events.csv"
ERA5_FILE = RAW_DIR / "era5_daily.csv"
META_FILE = ROOT / "outputs" / "era5_fetch_metadata.json"


def read_ems_events(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing EMS file: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]


def build_url(lat: float, lon: float, start_date: str, end_date: str, hourly_vars: str, model: str) -> str:
    params = {
        "latitude": f"{lat:.6f}",
        "longitude": f"{lon:.6f}",
        "start_date": start_date,
        "end_date": end_date,
        "hourly": hourly_vars,
        "models": model,
        "timezone": "UTC",
    }
    return "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)


def fetch_hourly_series(url: str) -> Dict[str, object]:
    with urllib.request.urlopen(url) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    hourly = data.get("hourly", {})
    if not isinstance(hourly, dict) or "time" not in hourly:
        raise RuntimeError(f"Invalid response from Open-Meteo: {url}")
    return data


def merge_hourly_series(
    land_hourly: Dict[str, object],
    precip_hourly: Dict[str, object],
) -> Dict[str, object]:
    land_time = land_hourly.get("time", [])
    precip_time = precip_hourly.get("time", [])
    if not (isinstance(land_time, list) and isinstance(precip_time, list)):
        raise RuntimeError("Invalid hourly time arrays.")
    if land_time != precip_time:
        raise RuntimeError("Hourly timestamps mismatch between ERA5-Land and precipitation source.")

    merged = {
        "time": land_time,
        "temperature_2m": land_hourly.get("temperature_2m", []),
        "soil_moisture_0_to_7cm": land_hourly.get("soil_moisture_0_to_7cm", []),
        "precipitation": precip_hourly.get("precipitation", []),
    }
    return merged


def daily_aggregate(hourly: Dict[str, object]) -> List[Dict[str, Optional[float]]]:
    time_values = hourly.get("time", [])
    precip_values = hourly.get("precipitation", [])
    temp_values = hourly.get("temperature_2m", [])
    soil_values = hourly.get("soil_moisture_0_to_7cm", [])
    if not (isinstance(time_values, list) and isinstance(precip_values, list) and isinstance(temp_values, list) and isinstance(soil_values, list)):
        raise RuntimeError("Hourly series have invalid format.")
    if not (len(time_values) == len(precip_values) == len(temp_values) == len(soil_values)):
        raise RuntimeError("Hourly series lengths are inconsistent.")

    buckets: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: {"precip": [], "temp": [], "soil": []})
    for timestamp, precip, temp, soil in zip(time_values, precip_values, temp_values, soil_values):
        day = str(timestamp)[:10]
        if precip is not None:
            buckets[day]["precip"].append(float(precip))
        if temp is not None:
            buckets[day]["temp"].append(float(temp))
        if soil is not None:
            buckets[day]["soil"].append(float(soil))

    daily_rows: List[Dict[str, Optional[float]]] = []
    for day in sorted(buckets.keys()):
        precip_sum = sum(buckets[day]["precip"]) if buckets[day]["precip"] else None
        temp_mean = sum(buckets[day]["temp"]) / len(buckets[day]["temp"]) if buckets[day]["temp"] else None
        soil_mean = sum(buckets[day]["soil"]) / len(buckets[day]["soil"]) if buckets[day]["soil"] else None
        daily_rows.append(
            {
                "date": day,
                "precip_mm": precip_sum,
                "t2m_mean_c": temp_mean,
                "soil_moisture_m3m3": soil_mean,
            }
        )
    return daily_rows


def build_era5_rows(events: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], int]:
    rows: List[Dict[str, str]] = []
    skipped_events = 0
    for event in events:
        event_id = event.get("event_id", "").strip()
        start_date = event.get("start_date", "").strip()
        end_date = event.get("end_date", "").strip()
        lat_raw = event.get("event_lat", "").strip()
        lon_raw = event.get("event_lon", "").strip()
        if not (event_id and start_date and end_date and lat_raw and lon_raw):
            skipped_events += 1
            continue

        lat = float(lat_raw)
        lon = float(lon_raw)
        land_url = build_url(
            lat=lat,
            lon=lon,
            start_date=start_date,
            end_date=end_date,
            hourly_vars="temperature_2m,soil_moisture_0_to_7cm",
            model="era5_land",
        )
        precip_url = build_url(
            lat=lat,
            lon=lon,
            start_date=start_date,
            end_date=end_date,
            hourly_vars="precipitation",
            model="era5_seamless",
        )
        land_payload = fetch_hourly_series(land_url)
        precip_payload = fetch_hourly_series(precip_url)
        hourly = merge_hourly_series(
            land_payload["hourly"] if isinstance(land_payload.get("hourly"), dict) else {},
            precip_payload["hourly"] if isinstance(precip_payload.get("hourly"), dict) else {},
        )
        daily = daily_aggregate(hourly if isinstance(hourly, dict) else {})
        grid_id = f"{lat:.3f}_{lon:.3f}"
        for day_row in daily:
            if day_row["precip_mm"] is None or day_row["t2m_mean_c"] is None or day_row["soil_moisture_m3m3"] is None:
                continue
            rows.append(
                {
                    "event_id": event_id,
                    "date": day_row["date"],
                    "precip_mm": f"{day_row['precip_mm']:.3f}",
                    "t2m_mean_c": f"{day_row['t2m_mean_c']:.3f}",
                    "soil_moisture_m3m3": f"{day_row['soil_moisture_m3m3']:.4f}",
                    "grid_id": grid_id,
                    "lat": f"{lat:.6f}",
                    "lon": f"{lon:.6f}",
                }
            )
    return rows, skipped_events


def write_csv(path: Path, rows: Iterable[Dict[str, str]]) -> None:
    fieldnames = [
        "event_id",
        "date",
        "precip_mm",
        "t2m_mean_c",
        "soil_moisture_m3m3",
        "grid_id",
        "lat",
        "lon",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_metadata(path: Path, rows: List[Dict[str, str]], events_count: int, skipped_events: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "Open-Meteo archive API",
        "variables_source": {
            "temperature_2m": "era5_land",
            "soil_moisture_0_to_7cm": "era5_land",
            "precipitation": "era5_seamless",
        },
        "events_input": events_count,
        "events_skipped": skipped_events,
        "rows_written": len(rows),
        "era5_land_dataset_reference": "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land",
    }
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def main() -> None:
    events = read_ems_events(EMS_FILE)
    rows, skipped_events = build_era5_rows(events)
    if not rows:
        raise RuntimeError("No ERA5-Land daily rows generated.")
    write_csv(ERA5_FILE, rows)
    write_metadata(META_FILE, rows, len(events), skipped_events)
    print(f"Saved {len(rows)} ERA5-Land daily rows to {ERA5_FILE}")


if __name__ == "__main__":
    main()
