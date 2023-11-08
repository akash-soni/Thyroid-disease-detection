from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataIngestionConfig:
    root_dir: Path
    source_URL: str
    local_data_file: Path
    unzip_dir: Path

@dataclass(frozen=True)
class DataValidationConfig:
    ingestion_dir: Path
    root_dir: Path
    ALL_REQUIRED_FILES: list
    columns: list
    ann_columns: list