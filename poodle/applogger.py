import logging

def get_logger(logger_name, log_level):

    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if log_level.lower() == 'info':
        logger.setLevel(logging.INFO)
    elif log_level.lower() == 'debug':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    return logger
