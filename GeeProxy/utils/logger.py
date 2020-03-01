'''
@Author: John
@Date: 2020-03-01 17:57:02
@LastEditors: John
@LastEditTime: 2020-03-01 18:36:57
@Description: 
'''

import os
import json
import logging.config


def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration from json 
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    print(path)
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


path = os.path.abspath(os.path.dirname(__file__)) + "/logging.json"
setup_logging(default_path=path)

crawler_logger = logging.getLogger('cralwer')
proxy_validator = logging.getLogger('ProxyValidator')

        

