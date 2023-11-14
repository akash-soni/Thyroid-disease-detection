from thyroid.config.configuration import ConfigurationManager
from thyroid.components.data_transformation import DataTransformation
from thyroid.logging import logger


STAGE_NAME = "DATA_TRANSFORMATION_STAGE"


class DataTransformationTrainingPipeline:
    def __init__(self):
        pass

    def main(self):

        config = ConfigurationManager()
        data_transformation_config = config.get_data_transformation_config()
        data_transformation = DataTransformation(config=data_transformation_config)
        data = data_transformation.case_normalization()
        data = data_transformation.handle_missing_values(data)
        no_outlier_data = data_transformation.outlier_removal(data)
        resampled_data = data_transformation.imbalance_handling(no_outlier_data)
        data = data_transformation.labelencoding_and_save(resampled_data)
        data_transformation.get_clustered_data(data)

if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = DataTransformationTrainingPipeline()
        obj.main()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e