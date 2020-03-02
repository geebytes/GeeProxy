'''
@Author: John
@Date: 2020-03-01 02:10:32
@LastEditors: John
@LastEditTime: 2020-03-02 19:56:22
@Description: 
'''
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import asyncio
from GeeProxy.validators.validators import ProxyValidator
from GeeProxy.utils.redis_cli import client
from GeeProxy.settings import VAILDATORS
from GeeProxy.utils.logger import pipeline_logger
class GeeproxyPipeline(object):
    '''
    代理可用性校验
    '''
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        asyncio.set_event_loop(self.loop)
    def process_item(self, item, spider):
        if self.loop.is_closed():
           self.loop = asyncio.new_event_loop()
           asyncio.set_event_loop(self.loop)
        result = self.loop.run_until_complete(self.check_item(item["url"]))
        for k in result:
            timestamp = int(round(time.time() * 1000))
            # key,例如:http:www.xiladaili.com
            client.zadd(k, {item["url"]:timestamp})
            pipeline_logger.info(
                "Cache proxy '{}' to '{}'".format(item["url"],k))
        return item
    
    @staticmethod
    async def check_item(proxy):
        result = []
        tasks = []
        for k, v in VAILDATORS.items():
            vaildator = ProxyValidator()
            # 开始校验
            tasks.append(vaildator.check_proxy(proxy=proxy, dst=v, cache_key=k))
        done, _ = await asyncio.wait(tasks)
        for d in done:
            vaild, cache_key, proxy = d.result()
            if vaild:
                result.append(cache_key)
        return result
    
    def open_spider(self, spider):
        if self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def close_spider(self, spider):
        # pass
        self.loop.close()
