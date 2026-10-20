from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelinePaths:
    project_root: Path

    @property
    def raw_dir(self) -> Path:
        return self.project_root / "data" / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.project_root / "data" / "processed"

    @property
    def outputs_dir(self) -> Path:
        return self.project_root / "outputs"

    @property
    def ems_raw(self) -> Path:
        return self.raw_dir / "ems_events.csv"

    @property
    def era5_raw(self) -> Path:
        return self.raw_dir / "era5_daily.csv"

    @property
    def ems_clean(self) -> Path:
        return self.processed_dir / "ems_events_clean.csv"

    @property
    def era5_clean(self) -> Path:
        return self.processed_dir / "era5_daily_clean.csv"

    @property
    def joined_clean(self) -> Path:
        return self.processed_dir / "joined_event_daily.csv"

    @property
    def quality_report(self) -> Path:
        return self.outputs_dir / "quality_report.json"
