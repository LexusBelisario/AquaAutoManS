import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

class CustomLogger:
    @staticmethod
    def setup_logger(app):
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        app_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=1024 * 1024,
            backupCount=10
        )
        app_handler.setFormatter(formatter)
        app_handler.setLevel(logging.INFO)

        error_handler = RotatingFileHandler(
            'logs/error.log',
            maxBytes=1024 * 1024,
            backupCount=10
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)

        app.logger.addHandler(app_handler)
        app.logger.addHandler(error_handler)
        app.logger.setLevel(logging.INFO)

        app.logger.info(f'Application startup at {datetime.now()}')

    @staticmethod
    def log_info(app, message):
        app.logger.info(message)

    @staticmethod
    def log_error(app, message):
        app.logger.error(message)

    @staticmethod
    def log_warning(app, message):
        app.logger.warning(message)

    @staticmethod
    def log_debug(app, message):
        app.logger.debug(message)