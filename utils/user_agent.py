'''
@Author: John
@Date: 2019-08-31 16:28:27
@LastEditors: John
@LastEditTime: 2020-03-01 13:01:25
@Description: 
'''
"""
This module provides fake ua for all spiders.
"""

__all__ = ['UserAgent']

import logging
import fake_useragent
import random
import fake_useragent
FIRST_NUM = random.randint(55, 62)
THIRD_NUM = random.randint(0, 3200)
FOURTH_NUM = random.randint(0, 140)


""" User agent helper class. Allows to get random user agents.
"""


class UserAgent(object):
    ua = None

    """ Returns a random user agent (if database is available),
        otherwise a default one.
        TODO include default user agent table
    """
    @classmethod
    def random(cls):
        if cls.ua is None:
            logger = logging.getLogger(__name__)
            logger.info('Initializing UserAgent using fake_useragent...')
            try:
                cls.ua = fake_useragent.UserAgent()
                # you may replace this by .load()
                cls.ua.load_cached()
            except:
                logger.error(
                    'Error initializing UserAgent using fake_useragent.')
                logger.info('Falling back to default User-Agent.')
                cls.ua = False
                return UserAgent.random()
        elif cls.ua is not False:
            return cls.ua.random()
        else:
            # specify a default user agent
            return 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
