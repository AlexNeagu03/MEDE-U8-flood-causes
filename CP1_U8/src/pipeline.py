import json
from pathlib import Path
from typing import Dict, List, Tuple

from src.config import PipelinePaths
from src.loaders import read_csv, write_csv
from src.validators import (
    deduplicate_rows,
    null_count,
    parse_iso_date,
    validate_ems_rows,
    validate_era5_rows,
)


def filter_era5_inside_event_windows(
    era5_rows: List[Dict[str, str]],
    ems_rows: List[Dict[str, str]],
) -> Tuple[List[Dict[str, str]], int]:
    events = {}
    for row in ems_rows:
        events[row["event_id"]] = (
            parse_iso_date(row["start_date"]),
            parse_iso_date(row["end_date"]),
        )

    filtered: List[Dict[str, str]] = []
    removed = 0
    for row in era5_rows:
        event_id = row["event_id"]
        if event_id not in events:
            removed += 1
            continue
        event_start, event_end = events[event_id]
        day = parse_iso_date(row["date"])
        if day < event_start or day > event_end:
            removed += 1
            continue
        filtered.append(row)

    return filtered, removed


def join_event_metadata(
    era5_rows: List[Dict[str, str]],
    ems_rows: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    event_lookup = {row["event_id"]: row for row in ems_rows}
    joined = []
    for row in era5_rows:
        event = event_lookup[row["event_id"]]
        joined.append(
            {
                "event_id": row["event_id"],
                "activation_code": event["activation_code"],
                "event_name": event["event_name"],
                "country": event["country"],
                "hazard_type": event["hazard_type"],
                "date": row["date"],
                "grid_id": row["grid_id"],
                "lat": row["lat"],
                "lon": row["lon"],
                "precip_mm": row["precip_mm"],
                "t2m_mean_c": row["t2m_mean_c"],
                "soil_moisture_m3m3": row["soil_moisture_m3m3"],
            }
        )
    return joined


def run_pipeline(project_root: Path) -> Path:
    paths = PipelinePaths(project_root=project_root)
    paths.processed_dir.mkdir(parents=True, exist_ok=True)
    paths.outputs_dir.mkdir(parents=True, exist_ok=True)

    ems_raw = read_csv(paths.ems_raw)
    era5_raw = read_csv(paths.era5_raw)

    ems_valid, ems_errors = validate_ems_rows(ems_raw)
    era5_valid, era5_errors = validate_era5_rows(era5_raw)

    ems_unique, ems_duplicates = deduplicate_rows(ems_valid, ["event_id"])
    era5_unique, era5_duplicates = deduplicate_rows(era5_valid, ["event_id", "date", "grid_id"])

    era5_windowed, era5_removed_outside_windows = filter_era5_inside_event_windows(era5_unique, ems_unique)

    joined = join_event_metadata(era5_windowed, ems_unique)

    ems_fields = list(ems_unique[0].keys()) if ems_unique else [
        "event_id",
        "activation_code",
        "event_name",
        "country",
        "region",
        "start_date",
        "end_date",
        "hazard_type",
        "source_url",
    ]
    era5_fields = list(era5_windowed[0].keys()) if era5_windowed else [
        "event_id",
        "date",
        "precip_mm",
        "t2m_mean_c",
        "soil_moisture_m3m3",
        "grid_id",
        "lat",
        "lon",
    ]
    joined_fields = list(joined[0].keys()) if joined else [
        "event_id",
        "activation_code",
        "event_name",
        "country",
        "hazard_type",
        "date",
        "grid_id",
        "lat",
        "lon",
        "precip_mm",
        "t2m_mean_c",
        "soil_moisture_m3m3",
    ]

    write_csv(paths.ems_clean, ems_unique, ems_fields)
    write_csv(paths.era5_clean, era5_windowed, era5_fields)
    write_csv(paths.joined_clean, joined, joined_fields)

    ems_nulls = null_count(ems_unique, ems_fields)
    era5_nulls = null_count(era5_windowed, era5_fields)
    joined_nulls = null_count(joined, joined_fields)

    report = {
        "input_rows": {"ems_events": len(ems_raw), "era5_daily": len(era5_raw)},
        "valid_rows": {"ems_events": len(ems_valid), "era5_daily": len(era5_valid)},
        "duplicates_removed": {"ems_events": ems_duplicates, "era5_daily": era5_duplicates},
        "window_filter": {"era5_removed_outside_event_window": era5_removed_outside_windows},
        "final_rows": {
            "ems_events_clean": len(ems_unique),
            "era5_daily_clean": len(era5_windowed),
            "joined_event_daily": len(joined),
        },
        "null_counts": {"ems_events": ems_nulls, "era5_daily": era5_nulls, "joined": joined_nulls},
        "validation_errors": {"ems_events": ems_errors, "era5_daily": era5_errors},
    }

    with paths.quality_report.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    return paths.quality_report
