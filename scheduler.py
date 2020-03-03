'''
@Author: John
@Date: 2020-03-02 18:17:27
@LastEditors: John
@LastEditTime: 2020-03-04 00:51:26
@Description: 调度器
'''

import os
import click
import signal
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from GeeProxy.validators.validate_tasks import subscribe_validator
from GeeProxy.validators.vaildate_pub import vaildate_pub
from GeeProxy.crawls.crawl import crawl_runner
from GeeProxy.settings import PROXY_VALIDATE_TIME
from GeeProxy.utils.logger import scheduler_logger


def run_crawl():
    crawl_runner()


def run_validate(is_master=False):
    scheduler_logger.info("Starting runs validate.")
    if is_master:
        scheduler_logger.info("This node running as the master role")
        scheduler = BlockingScheduler()
        scheduler.add_job(vaildate_pub, 'interval',seconds=PROXY_VALIDATE_TIME)
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass
    else:
        scheduler_logger.info("This node running as the slave role")
        subscribe_validator()


@click.command()
@click.option("--master", default=0, help="是否是主节点", type=int)
def main(master):
    p = ProcessPoolExecutor()
    crawl = p.submit(run_crawl)
    validate = p.submit(run_validate, master)
    p.shutdown()
    print(crawl, validate)

if __name__ == '__main__':
    main()
