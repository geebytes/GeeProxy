'''
@Author: John
@Date: 2020-03-01 17:13:49
@LastEditors: John
@LastEditTime: 2020-03-10 10:40:20
@Description: 爬虫启动脚本
'''
import asyncio
from scrapy.utils.reactor import install_reactor
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from twisted.internet import asyncioreactor
from scrapy.utils.project import get_project_settings
from GeeProxy.spiders.common import BaseSpider
from GeeProxy.spiders.rules import COMMON_CRAWL_RULES
from GeeProxy.utils.logger import crawler_logger
from twisted.internet import defer, reactor
from multiprocessing import Process, Queue

# asyncioreactor.install(asyncio.get_event_loop())

# install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

# @defer.inlineCallbacks
def crawl_runner(q: Queue):
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
        q.join_thread()
    except Exception as e:
        q.put(e)

    # q = Queue()
    # p = Process(target=f, args=(q,))
    # p.start()
    # result = q.get()
    # p.join()
#
# if result is not None:
#     raise result
# d = runner.join()
# d.addBoth(lambda _: reactor.stop())
# reactor.run()
# process = CrawlerProcess(get_project_settings())
# for crawl in COMMON_CRAWL_RULES:
#     # spider = BaseSpider()
#     process.crawl(BaseSpider, **crawl)
# process.start()
# scheduler.add_job(process.start,
#                   'interval',
#                   args=(True,),
#                   seconds=PROXY_UPDATE_TIME,
#                   next_run_time=datetime.datetime.now())
# return process
