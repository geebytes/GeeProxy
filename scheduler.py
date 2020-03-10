'''
@Author: John
@Date: 2020-03-02 18:17:27
@LastEditors: John
@LastEditTime: 2020-03-10 11:04:31
@Description: 调度器
'''

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

# def exit_process(process):
#     """退出子进程"""
#     @wraps
#     def wrapper(*args, **kwargs):
#         pass


def run_crawl(master):
    '''
        运行爬虫程序
    '''
    scheduler_logger.info("Starting runs spiders process with PID {}.".format(
        os.getpid()))
    if not check_api_server():
        scheduler_logger.error("API SERVER ERROR")
        os._exit(0)
    if master:
        input_start_urls()
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    q = mp.Queue()
    crawl_runner(q)


def run_item_vaildate():
    item_vaildator_runner()


def run_validate_pub():
    '''
        待校验代理入队列
    '''
    scheduler_logger.info(
        "Starting runs validator publish process with PID {}.".format(
            os.getpid()))
    vaildate_pub()


def run_validate_subscribe():
    '''
       监听代理校验任务
    '''
    scheduler_logger.info(
        "Starting runs validator subscribe process with PID {}.".format(
            os.getpid()))
    subscribe_validator()


def run_cronjob(master, crawl, vaildator):
    scheduler_logger.info("Starting runs cronjob process with PID {}.".format(
        os.getpid()))
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
                      next_run_time=datetime.datetime.now())
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
    help=
    "Do you run a proxy vailator?\nIf it is used as a message queue publisher, be sure to add the '--master' parameter.",
)
@click.option(
    "--app/--no-app",
    default=False,
    help="Start API Server",
)
def scheduleder(master, crawl, vaildator, app):
    '''
       主调度器
    '''
    scheduler_logger.info(
        "Master value is {},crawl value is {},vaildator value is {}".format(
            master, crawl, vaildator))
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
    # parent_conn, child_conn = Pipe()
    scheduler_logger.info('Main process PID is %d.' % os.getpid())
    scheduleder()
