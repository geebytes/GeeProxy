"""
@Author: John
@Date: 2020-03-09 14:57:26
@LastEditors: John
@LastEditTime: 2020-03-10 01:27:37
@Description: 起始URLS送入队列
"""
from GeeProxy.utils.redis_cli import client
from GeeProxy.spiders.rules import COMMON_CRAWL_RULES


def input_start_urls():
    pipe = client.pipeline()
    for rule in COMMON_CRAWL_RULES:
        llen = client.llen(rule["redis_key"])
        if not llen:
            key = rule["redis_key"]
            urls = rule["start_urls"]
            pipe.lpush(key, *urls)
    pipe.execute()
