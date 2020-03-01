'''
@Author: John
@Date: 2020-03-01 17:13:49
@LastEditors: John
@LastEditTime: 2020-03-01 19:49:22
@Description: 
'''
'''
@Author: John
@Date: 2020-03-01 17:13:49
@LastEditors: John
@LastEditTime: 2020-03-01 17:31:21
@Description: 
'''

from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from GeeProxy.spiders.common import BaseSpider
from GeeProxy.spiders.rules import CRAWL_RULES
from GeeProxy.utils.logger import crawler_logger

if __name__ == "__main__":
    crawler_logger.error("testddddddddddddddd")
    process = CrawlerProcess(get_project_settings())
    process.crawl(BaseSpider, **CRAWL_RULES[2])
    process.crawl(BaseSpider, **CRAWL_RULES[1])
    process.crawl(BaseSpider, **CRAWL_RULES[0])
    process.start()
