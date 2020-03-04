'''
@Author: John
@Date: 2020-03-02 18:17:27
@LastEditors: John
@LastEditTime: 2020-03-04 23:07:53
@Description: 调度器
'''

import os
import asyncio
import click
import datetime
import multiprocessing as mp
from functools import wraps
from apscheduler.schedulers.blocking import BlockingScheduler
from GeeProxy.validators.validate_tasks import subscribe_validator
from GeeProxy.validators.vaildate_pub import vaildate_pub
from GeeProxy.crawls.crawl import crawl_runner
from GeeProxy.settings import PROXY_VALIDATE_TIME, PROXY_UPDATE_TIME
from GeeProxy.utils.logger import scheduler_logger


# def exit_process(process):
#     """退出子进程"""
#     @wraps
#     def wrapper(*args, **kwargs):
#         pass


def run_crawl():
    '''
        运行爬虫程序
    '''
    scheduler_logger.info("Starting runs spiders process with PID {}.".format(
        os.getpid()))
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    crawl_runner()


def run_validate_pub(is_master=False, crawl=True, vaildator=True):
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


def run_cronjob(master, crawl):
    scheduler_logger.info(
        "Starting runs cronjob process with PID {}.".format(
            os.getpid()))
    sched = BlockingScheduler()
    scheduler_logger.info("This node running as the slave role")
    if master:
        sched.add_job(run_validate_pub,
                      'interval',
                      seconds=PROXY_VALIDATE_TIME)
    if crawl:
        sched.add_job(run_crawl,
                      trigger='interval',
                      seconds=PROXY_UPDATE_TIME,
                      next_run_time=datetime.datetime.now())
    try:
        if sched.get_jobs():
            sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass


@click.command()
@click.option("--master/--slave",
              default=False,
              help="Set master node",
              is_flag=True)
@click.option("--crawl/--no-crawl",
              default=True,
              help="Only run crawl process",
              is_flag=True)
@click.option("--vaildator/--no-vaildator",
              default=True,
              help="Only run proxy vailator process",
              is_flag=True)
def scheduleder(master, crawl, vaildator):
    '''
       主调度器
    '''
    pool = mp.Pool(5)
    pool.apply_async(run_validate_subscribe)
    pool.apply_async(run_cronjob, (master, crawl))
    pool.close()
    pool.join()


if __name__ == "__main__":
    # parent_conn, child_conn = Pipe()
    scheduler_logger.info('Main process PID is %d.' % os.getpid())
    scheduleder()
