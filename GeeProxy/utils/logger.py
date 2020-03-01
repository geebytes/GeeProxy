'''
@Author: John
@Date: 2020-03-01 17:57:02
@LastEditors: John
@LastEditTime: 2020-03-02 00:04:20
@Description: This module provides log handle module
'''

import os
import json
import logging.config
from GeeProxy.settings import LOG_PATH



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
            "level": "INFO",
            "formatter": "scrapy",
            "filename": LOG_PATH + "/info.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
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
        }
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
    # path = default_path
    # value = os.getenv(env_key, None)
    # if value:
    #     path = value
#   #   print(path)
#   #   if os.path.exists(path):
#   #       with open(path, 'rt') as f:
#   #           config = json.load(f)
    #     logging.config.dictConfig(config)
    # else:
    #     logging.basicConfig(level=default_level)


path = os.path.abspath(os.path.dirname(__file__)) + "/logging.json"
setup_logging()

crawler_logger = logging.getLogger('cralwer')
proxy_validator = logging.getLogger('ProxyValidator')
middlewares_logger = logging.getLogger('middlewares')


        

