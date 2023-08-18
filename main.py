from thyroid.logging import logger
from thyroid.utils.exception import customException
import sys
logger.info("Welcome to custom logs!")

try:
    x = 10/0
except Exception as e:
    raise customException(e,sys) 