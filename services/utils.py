import logging

FORMAT = "%(asctime)-15s %(log_lvl)-4s: %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(10)

def _log(type, msg):
    if type == "error":
        logger.error(msg, extra={"log_lvl": "Error"})
    elif type == "warning":
        logger.warning(msg, extra={"log_lvl": "Warning"})
    elif type == "debug":
        logger.debug(msg, extra={"log_lvl": "Debug"})
    elif type == "critical":
        logger.critical(msg, extra={"log_lvl": "Critical"})
    elif type == "exception":
        logger.exception(msg, extra={"log_lvl": "Exception"})
    elif type == "info":
        logger.info(msg, extra={"log_lvl": "Info"})
