from thyroid.constants import *
from thyroid.utils.common import read_yaml, create_directories
from thyroid.entity.config_entity import (DataIngestionConfig, DataValidationConfig,DataTransformationConfig, ClusteringConfig)
from pathlib import Path
import os

class ConfigurationManager:
    def __init__(
        self,
        config_filepath = CONFIG_FILE_PATH,
        params_filepath = PARAMS_FILE_PATH):

        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)

        create_directories([self.config.artifacts_root])


    # ingestion configuration
    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directories([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=config.root_dir,
            source_URL=config.source_URL,
            local_data_file=config.local_data_file,
            unzip_dir=config.unzip_dir 
        )

        return data_ingestion_config

    # validation configuration
    def get_data_validation_config(self) -> DataValidationConfig:
        config = self.config.data_validation

        create_directories([config.root_dir])

        data_validation_config = DataValidationConfig(
            ingestion_dir=config.ingestion_dir,
            root_dir=config.root_dir,
            ALL_REQUIRED_FILES=config.ALL_REQUIRED_FILES,
            columns=config.columns,
            ann_columns=config.ann_columns
        )

        return data_validation_config
    
    # Transformation configuration
    def get_data_transformation_config(self) -> DataTransformationConfig:
        config = self.config.data_transformation
        params = self.params.transformations

        create_directories([config.root_dir,config.encoding_dir,config.data_dir ])

        data_transformation_config = DataTransformationConfig(
            validation_dir=config.validation_dir,
            root_dir=config.root_dir,
            encoding_dir=config.encoding_dir,
            data_dir=config.data_dir,
            categorical_columns=config.categorical_columns,
            numerical_columns=config.numerical_columns,
            drop_columns=config.drop_columns,
            categorical_columns_to_convert=config.categorical_columns_to_convert,
            merged_file=params.merged_file,
            threshold=params.threshold,
            z_threshold=params.z_threshold,
            encoder_file=params.encoder_file,
            data_file=params.data_file
        )

        return data_transformation_config
    
    # clustering configuration
    def get_data_clustering_config(self) -> ClusteringConfig:
        config = self.config.data_transformation
        params = self.params.transformations

        create_directories([config.clustered_dir, config.cluster_model_dir, config.plot_dir])

        data_clustering_config = ClusteringConfig(
            clustered_dir=config.clustered_dir,
            cluster_model_dir=config.cluster_model_dir,
            plot_dir=config.plot_dir,
            cluster_plot=params.cluster_plot,
            clustering_file=params.clustering_file,
            cluster_model=params.cluster_model
        
        )

        return data_clustering_config