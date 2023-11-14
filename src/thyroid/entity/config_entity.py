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

@dataclass(frozen=True)
class DataTransformationConfig:
    validation_dir: Path
    root_dir: Path
    encoding_dir: Path
    data_dir: Path
    categorical_columns: list
    numerical_columns: list
    drop_columns: list
    categorical_columns_to_convert: list
    merged_file: str
    threshold: float
    z_threshold: int
    encoder_file: str
    data_file: str

@dataclass(frozen=True)
class ClusteringConfig:
    clustered_dir: Path
    cluster_model_dir: Path
    plot_dir: Path
    cluster_plot: str
    clustering_file: str
    cluster_model: str
