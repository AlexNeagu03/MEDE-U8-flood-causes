import json
import tempfile
import unittest
from pathlib import Path

from src.pipeline import run_pipeline


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestCP1Pipeline(unittest.TestCase):
    def test_pipeline_outputs_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_text(
                root / "data" / "raw" / "ems_events.csv",
                (
                    "event_id,activation_code,event_name,country,region,start_date,end_date,hazard_type,source_url\n"
                    "E001,EMSR001,Flood A,RO,Galati,2024-05-01,2024-05-03,Flood,https://example.com/a\n"
                    "E002,EMSR002,Flood B,RO,Braila,2024-06-10,2024-06-11,Flood,https://example.com/b\n"
                ),
            )
            write_text(
                root / "data" / "raw" / "era5_daily.csv",
                (
                    "event_id,date,precip_mm,t2m_mean_c,soil_moisture_m3m3,grid_id,lat,lon\n"
                    "E001,2024-05-01,25.4,18.2,0.42,G1,45.4,27.9\n"
                    "E001,2024-05-04,12.0,17.0,0.40,G1,45.4,27.9\n"
                    "E002,2024-06-10,8.0,22.0,0.31,G2,45.2,27.7\n"
                ),
            )

            report_path = run_pipeline(project_root=root)
            report = json.loads(report_path.read_text(encoding="utf-8"))

            self.assertEqual(report["input_rows"]["ems_events"], 2)
            self.assertEqual(report["input_rows"]["era5_daily"], 3)
            self.assertEqual(report["window_filter"]["era5_removed_outside_event_window"], 1)
            self.assertEqual(report["final_rows"]["joined_event_daily"], 2)
            self.assertTrue((root / "data" / "processed" / "joined_event_daily.csv").exists())


if __name__ == "__main__":
    unittest.main()
