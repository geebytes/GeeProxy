'''
@Author: qinzhonghe96@163.com
@Date: 2020-03-01 02:10:32
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-10 02:09:29
@Description: 数据处理
'''

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import asyncio
from GeeProxy.utils.redis_cli import client
from GeeProxy.utils.logger import pipeline_logger
from GeeProxy.validators.validators import ProxyValidator
from GeeProxy.client.client import AvailableProxy
from GeeProxy.utils.tools import get_vaildator_task
from GeeProxy.settings import ITEM_VAILDATE_SET


class GeeProxyNoVaildatePipe(object):
    def process_item(self, item, spider):
        # print("processing item now.....")
        if not item or not item["url"]:
            return item
        item["available"] = 0
        client.hmset(item["url"], dict(item))
        client.sadd(ITEM_VAILDATE_SET, item["url"])
        return item


class GeeproxyPipeline(object):
    '''
    代理可用性校验
    '''
    def __init__(self):
        # pass
        self.loop = asyncio.get_event_loop()
        asyncio.set_event_loop(self.loop)

    def process_item(self, item, spider):
        if self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        if not item or not item["available"]:
            return item
        result = self.loop.run_until_complete(self.check_item(item["url"]))
        for r in result:
            if r.available:
                pipeline_logger.info("Add proxy {} to cache.".format(
                    item["url"]))
                self.loop.run_until_complete(AvailableProxy.add_proxy(r, item))
        return item

    @staticmethod
    async def check_item(proxy: str) -> list:
        result = []
        tasks = get_vaildator_task(proxy)
        done = await asyncio.gather(*tasks)
        for d in done:
            check_result = d
            if check_result.available:
                result.append(check_result)
        return result

    def open_spider(self, spider):
        # pass
        if self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def close_spider(self, spider):
        self.loop.close()
        # pass


class ProxyAnonymousPipeline(object):
    '''
    代理可用性校验
    '''
    def __init__(self):
        # pass
        self.loop = asyncio.get_event_loop()
        asyncio.set_event_loop(self.loop)

    def process_item(self, item, spider):
        if self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        if not item:
            return item
        item["available"] = 0
        if not AvailableProxy.proxy_exist(item["url"]):
            pipeline_logger.info("Checking proxy {} anonymous.".format(
                item["url"]))
            try:
                result = self.loop.run_until_complete(
                    ProxyValidator.check_anonymous(item["url"]))
                item["anonymous"] = int(result)
                item["available"] = 1
            except Exception as e:
                pipeline_logger.error(
                    "While check proxy {} anonymous have an error {}.".format(
                        item["url"], str(e)))
                item["available"] = 0
        return item

    def open_spider(self, spider):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop = asyncio.get_event_loop()

    def close_spider(self, spider):
        self.loop.close()
        # pass
