"""
@Author: qinzhonghe96@163.com
@Date: 2020-03-01 17:13:49
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-10 13:42:02
@Description: 爬虫启动脚本
"""
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from GeeProxy.spiders.common import BaseSpider
from GeeProxy.spiders.rules import COMMON_CRAWL_RULES
from twisted.internet import reactor
from multiprocessing import Queue


def crawl_runner(q: Queue):
    """
    执行爬虫

    :param q: 一个队列对象，防止爬虫无法重启
    :return:
    """
    try:
        runner = CrawlerRunner(get_project_settings())
        for crawl in COMMON_CRAWL_RULES:
            runner.crawl(BaseSpider, **crawl)
        d = runner.join()
        d.addBoth(lambda _: reactor.stop())
        reactor.run(installSignalHandlers=0)
        q.put(None)
        q.get()
        q.close()
    except Exception as e:
        q.put(e)