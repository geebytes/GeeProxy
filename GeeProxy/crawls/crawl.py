'''
@Author: John
@Date: 2020-03-01 17:13:49
@LastEditors: John
@LastEditTime: 2020-03-03 21:27:55
@Description: 爬虫启动脚本
'''

from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from GeeProxy.spiders.common import BaseSpider
from GeeProxy.spiders.rules import CRAWL_RULES
from GeeProxy.utils.logger import crawler_logger


def crawl_runner():
    crawler_logger.debug("启动爬虫")
    process = CrawlerProcess(get_project_settings())
    for crawl in CRAWL_RULES:
        process.crawl(BaseSpider, **crawl)
    process.start()

# crawl_run()
