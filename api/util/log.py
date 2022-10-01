import sys
import logging
from typing import Optional

fileHandler = logging.FileHandler("logfile.log")
streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
logger: Optional[logging.Logger] = None


def configure(app_logger: logging.Logger):
    global logger
    logger = app_logger
    streamHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)
    logger.setLevel('INFO')
