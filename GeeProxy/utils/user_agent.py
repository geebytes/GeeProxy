'''
@Author: qinzhonghe96@163.com
@Date: 2019-08-31 16:28:27
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-02 23:26:57
@Description: This module provides fake ua for all spiders.
'''
"""
This module provides fake ua for all spiders.
"""

__all__ = ['UserAgent']

import logging
import fake_useragent
import random
FIRST_NUM = random.randint(55, 62)
THIRD_NUM = random.randint(0, 3200)
FOURTH_NUM = random.randint(0, 140)

logger = logging.getLogger(__name__)


class UserAgent(object):
    ua = None

    """
    返回一个随机的ua
    """
    @classmethod
    def random(cls):
        if cls.ua is None:
            logger.info('Initializing UserAgent using fake_useragent...')
            try:
                cls.ua = fake_useragent.UserAgent(verify_ssl=False)
                cls.ua.load()
            except:
                logger.error(
                    'Error initializing UserAgent using fake_useragent.')
                logger.debug('Falling back to default User-Agent.')
                cls.ua = False
                return UserAgent.random()
        elif cls.ua is not False:
            return cls.ua.random
        else:
            return 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 ' \
                   '(KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
