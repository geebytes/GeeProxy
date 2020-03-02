'''
@Author: John
@Date: 2020-03-02 18:17:27
@LastEditors: John
@LastEditTime: 2020-03-02 18:23:37
@Description: 调度器
'''

from datetime import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from GeeProxy.validators.validate_tasks import validate_run
from GeeProxy.settings import PROXY_VALIDATE_TIME


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(validate_run, 'interval', seconds=PROXY_VALIDATE_TIME)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
