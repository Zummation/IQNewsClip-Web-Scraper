import logging
from logging.handlers import TimedRotatingFileHandler


my_logger = None

def create_rotating_log():
    global my_logger

    if my_logger is not None:
        return my_logger

    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(
        'weekly-log.log',
        when="d",
        interval=7,
        backupCount=1,
        encoding='utf-8-sig'
    )
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)    
    logger.addHandler(handler)
    my_logger = logger
    return logger