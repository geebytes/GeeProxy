'''
@Author: John
@Date: 2020-03-02 11:20:45
@LastEditors: John
@LastEditTime: 2020-03-04 20:36:40
@Description: 扩展
'''

from scrapy import signals
from scrapy.exceptions import NotConfigured
from .utils.logger import crawler_logger
from .utils.redis_cli import client


class SpiderOpenCloseHandler(object):
    def __init__(self, item_count):
        self.item_count = item_count
        self.items_scraped = 0

    @classmethod
    def from_crawler(cls, crawler):
        # first check if the extension should be enabled and raise
        # NotConfigured otherwise
        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured

        # get the number of items from settings
        item_count = crawler.settings.getint('MYEXT_ITEMCOUNT', 1000)

        # instantiate the extension object
        ext = cls(item_count)

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_opened,
                                signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed,
                                signal=signals.spider_closed)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

        # return the extension object
        return ext

    def spider_opened(self, spider):
        crawler_logger.info("opened spider %s", spider.name)

    def spider_closed(self, spider):
        crawler_logger.info("closed spider %s", spider.name)
        client.connection_pool.disconnect()

    def item_scraped(self, item, spider):
        self.items_scraped += 1
        if self.items_scraped % self.item_count == 0:
            crawler_logger.info("scraped %d items", self.items_scraped)
