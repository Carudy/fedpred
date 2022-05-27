from loguru import logger

from .path import *

logger.add(LOG_PATH, format="{time} {level} {message}", level="INFO")
