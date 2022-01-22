import logging.config

from logger.logging_config import config

logging.config.dictConfig(config)
logger = logging.getLogger('app_logger')