"""
@Author: qinzhonghe96@163.com
@Date: 2020-03-02 18:17:27
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-10 21:55:52
@Description:

调度器,正式执行任务前,调度函数会创建大小为5的进程池,
这些进程分别执行定时数据抓取、定时校验、及数据处理等任务。

"""

import os
import asyncio
import click
import datetime
import multiprocessing as mp
from GeeProxy.api.api import run_app
from GeeProxy.crawls.crawl import crawl_runner
from GeeProxy.utils.tools import check_api_server
from GeeProxy.utils.logger import scheduler_logger
from GeeProxy.spiders.master import input_start_urls
from GeeProxy.validators.vaildate_pub import vaildate_pub
from apscheduler.schedulers.blocking import BlockingScheduler
from GeeProxy.validators.validate_tasks import subscribe_validator
from GeeProxy.settings import PROXY_VALIDATE_TIME, PROXY_UPDATE_TIME
from GeeProxy.validators.items_vaildate import item_vaildator_runner


def run_crawl(master):
    """
    运行爬虫程序
    """

    if not check_api_server():
        scheduler_logger.error("API SERVER ERROR")
        os._exit(0)
    if master:
        input_start_urls()
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    asyncio.get_event_loop()
    q = mp.Queue()
    crawl_runner(q)


def run_item_vaildate():
    """
    数据项可用性及匿名性校验

    """

    item_vaildator_runner()


def run_validate_pub():
    """
    待校验代理入队列

    """

    vaildate_pub()


def run_validate_subscribe():
    """
    监听代理校验任务

    """

    subscribe_validator()


def run_cronjob(master: bool, crawl: bool, vaildator: bool):
    """
    执行数据抓取及校验定时任务

    :param master: 是否是主节点
    :param crawl: 是否运行爬虫
    :param vaildator: 是否运行校验器

    """

    sched = BlockingScheduler()
    if vaildator and master:
        sched.add_job(run_validate_pub,
                      'interval',
                      seconds=PROXY_VALIDATE_TIME)
    if crawl:
        sched.add_job(run_crawl,
                      args=[master],
                      trigger='interval',
                      seconds=PROXY_UPDATE_TIME,
                      next_run_time=datetime.datetime.now(),  # 立刻执行
                      max_instances=5)
    try:
        if sched.get_jobs():
            sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass


@click.command()
@click.option(
    "--master/--slave",
    default=False,
    help="Set master node and '--vaildator' must be add.",
)
@click.option("--crawl/--no-crawl", default=True, help="Do you run a crawler?")
@click.option(
    "--vaildator/--no-vaildator",
    default=True,
    help="Do you run a proxy vailator? \
          If it is used as a message queue publisher, \
          be sure to add the '--master' parameter.",
)
@click.option(
    "--app/--no-app",
    default=True,
    help="Start API Server",
)
def scheduleder(master, crawl, vaildator, app):
    """
    主调度器
    """
    master = os.environ.get("MASTER", "") if os.environ.get("MASTER", "") else master
    crawl = os.environ.get("CRAWL", "") if os.environ.get("CRAWL", "") else crawl
    vaildator = os.environ.get("VAILDATOR", "") if os.environ.get("VAILDATOR", "") else vaildator
    app = os.environ.get("APP", "") if os.environ.get("APP", "") else app
    scheduler_logger.info("Master value is {},crawl value is {},"
                          "vaildator value is {}".format(master, crawl, vaildator))
    pool = mp.Pool(5)
    if not master:
        pool.apply_async(run_validate_subscribe)
    if app:
        pool.apply_async(run_app)
    pool.apply_async(run_cronjob, (master, crawl, vaildator))
    pool.apply_async(run_item_vaildate)
    pool.close()
    pool.join()


if __name__ == "__main__":
    scheduleder()
