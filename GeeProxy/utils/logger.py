'''
@Author: John
@Date: 2020-03-01 17:57:02
@LastEditors: John
@LastEditTime: 2020-03-04 13:43:34
@Description: This module provides log handle module
'''

import os
import json
import logging.config
from GeeProxy.settings import LOG_PATH
import multiprocessing
from logging.handlers import RotatingFileHandler


class SafeRotatingFileHandler(RotatingFileHandler):
    """
    多进程下 RotatingFileHandler 会出现问题
    """

    _rollover_lock = multiprocessing.Lock()

    def emit(self, record):
        """
        Emit a record.
        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        try:
            if self.shouldRollover(record):
                with self._rollover_lock:
                    if self.shouldRollover(record):
                        self.doRollover()
            logging.FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def shouldRollover(self, record):
        if self._should_rollover():
            # if some other process already did the rollover we might
            # checked log.1, so we reopen the stream and check again on
            # the right log file
            if self.stream:
                self.stream.close()
                self.stream = self._open()

            return self._should_rollover()

        return 0

    def _should_rollover(self):
        if self.maxBytes > 0:
            self.stream.seek(0, 2)
            if self.stream.tell() >= self.maxBytes:
                return True

        return False
    
config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "scrapy": {
            "format": "%(filename)s-%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "scrapy",
            "stream": "ext://sys.stdout"
        },
        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            # "class": "GeeProxy.utils.logger.SafeRotatingFileHandler",
            "level": "INFO",
            "formatter": "scrapy",
            "filename": LOG_PATH + "/info.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "cralwer_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            # "class": "GeeProxy.utils.logger.SafeRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "scrapy",
            "filename": LOG_PATH + "/cralwer.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "proxy_validator_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            # "class": "GeeProxy.utils.logger.SafeRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "scrapy",
            "filename": LOG_PATH + "/proxy_validator.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "middlewares_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            # "class": "GeeProxy.utils.logger.SafeRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "scrapy",
            "filename": LOG_PATH + "/middlewares.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "pipeline_logger_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            # "class": "GeeProxy.utils.logger.SafeRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "scrapy",
            "filename": LOG_PATH + "/pipeline_logger.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "scheduler_logger_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            # "class": "GeeProxy.utils.logger.SafeRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "scrapy",
            "filename": LOG_PATH + "/scheduler_logger.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "client_logger_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            # "class": "GeeProxy.utils.logger.SafeRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "scrapy",
            "filename": LOG_PATH + "/client.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            # "class": "GeeProxy.utils.logger.SafeRotatingFileHandler",
            "level": "ERROR",
            "formatter": "scrapy",
            "filename": LOG_PATH + "/errors.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        }
    },
    "loggers": {
        "spider": {
            "level": "ERROR",
            "handlers": [
                "console"
            ],
            "propagate": "no"
        },
        "cralwer": {
            "level": "INFO",
            "handlers": [
                "cralwer_handler"
            ],
            "propagate": "no"
        },
        "proxy_validator": {
            "level": "INFO",
            "handlers": [
                "proxy_validator_handler"
            ],
            "propagate": "no"
        },
        "middlewares": {
            "level": "INFO",
            "handlers": [
                "middlewares_handler"
            ],
            "propagate": "no"
        },
        "pipeline_logger": {
            "level": "INFO",
            "handlers": [
                "pipeline_logger_handler"
            ],
            "propagate": "no"
        },
        "scheduler_logger": {
            "level": "INFO",
            "handlers": [
                "scheduler_logger_handler"
            ],
            "propagate": "no"
        },
        "client_logger": {
            "level": "INFO",
            "handlers": [
                "client_logger_handler"
            ],
            "propagate": "no"
        },
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console",
            "info_file_handler",
            "error_file_handler"
        ]
    }
}

def setup_logging():
    """Setup logging configuration from json 
    """
    logging.config.dictConfig(config)


path = os.path.abspath(os.path.dirname(__file__)) + "/logging.json"
setup_logging()

crawler_logger = logging.getLogger('cralwer')
proxy_validator = logging.getLogger('proxy_validator')
middlewares_logger = logging.getLogger('middlewares')
pipeline_logger = logging.getLogger('pipeline_logger')
scheduler_logger = logging.getLogger('scheduler_logger')
available_validator = logging.getLogger('available_validator')
client_logger = logging.getLogger('client_logger')


        

