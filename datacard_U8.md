# Data Card - U8 (Inundatii in Europa)

## S1 - Copernicus EMS Rapid Mapping (activari reale)

| Camp | Valoare |
|---|---|
| Sursa | Copernicus Emergency Management Service - Rapid Mapping |
| URL principal | https://mapping.emergency.copernicus.eu/activations/ |
| API public folosit | https://rapidmapping.emergency.copernicus.eu/backend/dashboard-api/public-activations-info/ |
| Unitate de observatie | 1 activare/eveniment |
| Cheie | `event_id` (`activation_code`) |
| Campuri folosite | `event_id`, `activation_code`, `event_name`, `country`, `start_date`, `end_date`, `hazard_type`, `event_lat`, `event_lon` |
| Acoperire | Activari publice EMS; in proiect sunt filtrate activari Flood din Europa |
| Licenta / terms | Conform termenilor Copernicus EMS: https://mapping.emergency.copernicus.eu/terms-and-conditions/ |

## S2 - ERA5-Land (serii meteo pentru ferestrele evenimentelor)

| Camp | Valoare |
|---|---|
| Dataset de referinta | ERA5-Land reanalysis (plus precipitatiile furnizate de ruta `era5_seamless` in Open-Meteo pentru completarea variabilei de ploaie) |
| Pagina oficiala | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land |
| DOI oficial | https://doi.org/10.24381/cds.e2161bac |
| Unitate de observatie in fisierul CP1 | 1 eveniment x 1 zi x 1 punct spatial |
| Campuri folosite | `event_id`, `date`, `precip_mm`, `t2m_mean_c`, `soil_moisture_m3m3`, `lat`, `lon`, `grid_id` |
| Variabile meteo incluse | precipitatiile (era5_seamless), temperatura la 2m si umiditate sol (era5_land) |
| Acoperire temporala in proiect | pentru fiecare eveniment: intervalul `start_date` - `end_date` |

## Cheie comuna si aliniere

- **Cheie de join:** `event_id`
- **Regula temporala:** randurile meteo sunt pastrate doar daca `date` este in intervalul evenimentului.
- **Output principal:** `data/processed/joined_event_daily.csv`

## Pipeline si validari

1. Validare coloane obligatorii.
2. Validare date ISO (`YYYY-MM-DD`) si intervale.
3. Validare numeric/range (`precip_mm`, `t2m_mean_c`, `soil_moisture_m3m3`, `lat`, `lon`).
4. Deduplicare (`event_id` pentru EMS; `event_id+date+grid_id` pentru ERA5).
5. Raport final in `outputs/quality_report.json`.

## Reproducibilitate

- Script EMS: `fetch_ems_events.py`
- Script ERA5-Land: `fetch_era5_land.py`
- Pipeline curatare/join: `run_cp1.py`
- Generare prezentare: `generate_cp1_ppt.py`
