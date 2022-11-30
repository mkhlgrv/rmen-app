from dotenv import load_dotenv
load_dotenv()
import logging.handlers
import os
logger = logging.getLogger(__name__)
handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", ".log"))
formatter = logging.Formatter('%(asctime)s: %(message)s')
handler.setFormatter(formatter)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))
logger.addHandler(handler)
logger = logging.LoggerAdapter(logger, extra = {})