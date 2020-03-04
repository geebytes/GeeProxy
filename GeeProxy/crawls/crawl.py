'''
@Author: John
@Date: 2020-03-01 17:13:49
@LastEditors: John
@LastEditTime: 2020-03-04 16:32:20
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
    # runner = CrawlerRunner(get_project_settings())
    # for crawl in CRAWL_RULES:
    #     runner.crawl(BaseSpider, **crawl)
    # d = runner.join()
    # d.addBoth(lambda _: reactor.stop())
    # reactor.run()  # the script will block here until all crawling jobs are finished
    process = CrawlerProcess(get_project_settings())
    for crawl in CRAWL_RULES:
        process.crawl(BaseSpider, **crawl)
    process.start()

# crawl_run()
