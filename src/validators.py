from datetime import date, datetime
from typing import Dict, Iterable, List, Tuple


def parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def null_count(rows: Iterable[Dict[str, str]], columns: List[str]) -> Dict[str, int]:
    counts = {column: 0 for column in columns}
    for row in rows:
        for column in columns:
            if row.get(column, "").strip() == "":
                counts[column] += 1
    return counts


def deduplicate_rows(rows: List[Dict[str, str]], key_columns: List[str]) -> Tuple[List[Dict[str, str]], int]:
    seen = set()
    unique_rows: List[Dict[str, str]] = []
    duplicates = 0
    for row in rows:
        key = tuple(row.get(column, "") for column in key_columns)
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        unique_rows.append(row)
    return unique_rows, duplicates


def validate_ems_rows(rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[str]]:
    errors: List[str] = []
    clean_rows: List[Dict[str, str]] = []
    required_columns = [
        "event_id",
        "activation_code",
        "event_name",
        "country",
        "start_date",
        "end_date",
        "hazard_type",
        "source_url",
    ]
    for index, row in enumerate(rows, start=2):
        if any(row.get(column, "").strip() == "" for column in required_columns):
            errors.append(f"EMS row {index}: missing required value.")
            continue

        try:
            start_date = parse_iso_date(row["start_date"])
            end_date = parse_iso_date(row["end_date"])
            if start_date > end_date:
                errors.append(f"EMS row {index}: start_date > end_date.")
                continue
        except ValueError:
            errors.append(f"EMS row {index}: invalid date format.")
            continue

        clean_rows.append(row)

    return clean_rows, errors


def validate_era5_rows(rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[str]]:
    errors: List[str] = []
    clean_rows: List[Dict[str, str]] = []
    required_columns = [
        "event_id",
        "date",
        "precip_mm",
        "t2m_mean_c",
        "soil_moisture_m3m3",
        "grid_id",
        "lat",
        "lon",
    ]

    for index, row in enumerate(rows, start=2):
        if any(row.get(column, "").strip() == "" for column in required_columns):
            errors.append(f"ERA5 row {index}: missing required value.")
            continue

        try:
            parse_iso_date(row["date"])
            precip = float(row["precip_mm"])
            temp = float(row["t2m_mean_c"])
            soil = float(row["soil_moisture_m3m3"])
            lat = float(row["lat"])
            lon = float(row["lon"])
        except ValueError:
            errors.append(f"ERA5 row {index}: invalid numeric/date value.")
            continue

        if precip < 0 or precip > 1000:
            errors.append(f"ERA5 row {index}: precip_mm out of range.")
            continue
        if temp < -80 or temp > 60:
            errors.append(f"ERA5 row {index}: t2m_mean_c out of range.")
            continue
        if soil < 0 or soil > 1:
            errors.append(f"ERA5 row {index}: soil_moisture_m3m3 out of range.")
            continue
        if lat < -90 or lat > 90 or lon < -180 or lon > 180:
            errors.append(f"ERA5 row {index}: invalid coordinates.")
            continue

        clean_rows.append(row)

    return clean_rows, errors
