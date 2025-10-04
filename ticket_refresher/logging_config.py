import os
import logging
import colorlog

def setup_logger(log_file="app.log", use_color=True):
    """ Configura o logger para registrar logs no console e em arquivo.
    Se use_color=True, os logs no console terão cores. """
    os.makedirs('logs', exist_ok=True)
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()
    logger.propagate = False

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    if use_color:
        color_formatter = colorlog.ColoredFormatter(
            "%(asctime)s - %(log_color)s%(levelname)s - %(message)s",
            datefmt='%d/%m/%Y %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )
        console_handler.setFormatter(color_formatter)
    else:
        plain_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S'
        )
        console_handler.setFormatter(plain_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = setup_logger('logs/app.log', use_color=True)
