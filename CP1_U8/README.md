# CP1 U8 - Pachet complet de predare (Moodle + GitHub)

Acest folder este pregatit pentru tema CP1 la U8 si contine:

1. Cod Python pentru ingestie, validare si join intre **Copernicus EMS** si **ERA5-Land**.
2. Date brute reale generate automat:
   - activari reale din API-ul public Copernicus EMS;
   - serii meteo din modelul `era5_land` (temperatura + umiditate sol) si precipitatii din `era5_seamless` (Open-Meteo archive API).
3. Artefacte finale pentru incarcare:
   - `CP1_U8_prezentare.pptx`
   - `datacard_U8.md`
   - `soa_table_U8.md`
   - fisiere procesate + raport calitate.

## Structura proiect

```text
CP1_U8/
  run_cp1.py
  generate_cp1_ppt.py
  fetch_ems_events.py
  fetch_era5_land.py
  src/
    config.py
    loaders.py
    validators.py
    pipeline.py
  tests/
    test_pipeline.py
  data/
    raw/
      ems_events.csv
      era5_daily.csv
      sources_manifest.json
    processed/
  outputs/
    quality_report.json
  moodle_submission/
  datacard_U8.md
  soa_table_U8.md
```

## Rulare end-to-end

Din folderul `CP1_U8`:

```bash
python fetch_ems_events.py
python fetch_era5_land.py
python run_cp1.py
python generate_cp1_ppt.py
```

## Fisiere rezultate

- `data/raw/ems_events.csv` - evenimente flood reale (EMS)
- `data/raw/era5_daily.csv` - indicatori zilnici meteo (era5_land)
- `data/processed/ems_events_clean.csv`
- `data/processed/era5_daily_clean.csv`
- `data/processed/joined_event_daily.csv`
- `outputs/quality_report.json`
- `CP1_U8_prezentare.pptx`

## Teste

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Surse oficiale

- Copernicus EMS activations: https://mapping.emergency.copernicus.eu/activations/
- EMS public API: https://rapidmapping.emergency.copernicus.eu/backend/dashboard-api/public-activations-info/
- ERA5-Land dataset page: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land
- ERA5-Land DOI: https://doi.org/10.24381/cds.e2161bac
