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
# sklearn verbose level
log_level = logger.getEffectiveLevel()//10
if log_level >= 3:
    sklearn_verbose:int = 0
elif log_level == 2:
    sklearn_verbose = 1
elif log_level == 1:
    sklearn_verbose = 2
elif log_level == 0:
    sklearn_verbose = 3