'''
@Author: John
@Date: 2020-03-02 18:17:27
@LastEditors: John
@LastEditTime: 2020-03-04 16:53:35
@Description: 调度器
'''

import os
import asyncio
import click
import signal
import datetime
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.twisted import TwistedScheduler
from GeeProxy.validators.validate_tasks import subscribe_validator
from GeeProxy.validators.vaildate_pub import vaildate_pub
from GeeProxy.crawls.crawl import crawl_runner
from GeeProxy.settings import PROXY_VALIDATE_TIME, PROXY_UPDATE_TIME
from GeeProxy.utils.logger import scheduler_logger
from GeeProxy.utils.DaemonProcessPool import DaemonProcessPool



def run_crawl():
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    process = multiprocessing.Process(target=crawl_runner)
    process.daemon = True
    process.start()


def run_validate_pub(is_master=False, crawl=True, vaildator=True):
    scheduler_logger.info("Starting runs validate.")
    process = multiprocessing.Process(target=vaildate_pub)
    process.daemon = True
    process.start()


def run_validate_subscribe():
    scheduler_logger.info("Starting runs validate.")
    process = multiprocessing.Process(target=subscribe_validator)
    process.daemon = True
    process.start()
    
    
@click.command()
@click.option("--master", default=0, help="是否是主节点", type=int)
@click.option("--crawl", default=1, help="仅启动爬虫程序", type=int)
@click.option("--vaildator", default=1, help="仅启动校验程序", type=int)
def scheduleder(master, crawl, vaildator):
    sched = BlockingScheduler()
    if master:
        scheduler_logger.info("This node running as the master role")
        run_validate_subscribe()
    else:
        scheduler_logger.info("This node running as the slave role")
        sched.add_job(run_validate_pub, 'interval', seconds=PROXY_VALIDATE_TIME)
    sched.add_job(run_crawl,trigger='interval', seconds=PROXY_UPDATE_TIME,
                  next_run_time=datetime.datetime.now())
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    
scheduleder()
