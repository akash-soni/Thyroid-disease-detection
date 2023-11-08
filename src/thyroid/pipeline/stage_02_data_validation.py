from thyroid.config.configuration import ConfigurationManager
from thyroid.components.data_validation import DataValidation
from thyroid.logging import logger


STAGE_NAME = "DATA_VALIDATION_STAGE"


class DataValidationTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        data_validation_config = config.get_data_validation_config()
        data_validation = DataValidation(config=data_validation_config)
        data_validation.remove_extrafiles()
        # processing all data files
        data_validation.combine_all_data_files()
        # processing thyroid0378 file
        data_validation.validate_thyroid0378_file()
        # validating hypothyroid
        data_validation.validate_hypothyroid_file()
        # validating sick-euthyroid
        data_validation.validate_euthyroid_file()
        # validating ann data
        data_validation.validate_ann_file()
        # merge data
        data_validation.merge_data()


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = DataValidationTrainingPipeline()
        obj.main()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e