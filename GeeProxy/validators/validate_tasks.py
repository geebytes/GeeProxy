"""
@Author: qinzhonghe96@163.com
@Date: 2020-03-02 17:14:07
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-10 19:54:48
@Description: 定时校验任务
"""

import time
import asyncio
from GeeProxy.utils.redis_cli import client
from GeeProxy.utils.logger import proxy_validator
from GeeProxy.client.client import AvailableProxy
from GeeProxy.utils.tools import get_vaildator_task
from GeeProxy.settings import VALIDATE_QUEUE_KEY, PUBLISH_LOCK


async def validate_task():
    """
    定时代理校验任务
    """
    tasks = []
    result = None
    proxy = client.rpop(VALIDATE_QUEUE_KEY)
    while proxy:
        proxy_validator.info("This proxy {} has joined the validation task.".format(proxy))
        tasks.extend(get_vaildator_task(proxy))
        proxy = client.rpop(VALIDATE_QUEUE_KEY)
        time.sleep(0.5)
    if tasks:
        result = await asyncio.gather(*tasks)
        for r in result:
            res = r
            s = "available" if res.available else "unavailable"
            proxy_validator.info(
                "{} validation for {} tasks result is {} .".format(
                    res.proxy, res.web_key, s))
            try:
                if not res.available:
                    # 不可用就删除
                    await AvailableProxy.delete_proxy(res.proxy, res.web_key)
                    proxy_validator.info("delete proxy {} with {}".format(
                        res.proxy, res.web_key))
                else:
                    proxy_validator.info("update proxy {}".format(res.proxy))
                    await AvailableProxy.update_proxy_delay(
                        res.proxy, res.dst, res.delay)
            except Exception as e:
                proxy_validator.error(
                    "An exception {} occurred while checking proxy {} availability."
                    .format(e, res.proxy))
            finally:
                client.delete(PUBLISH_LOCK)
    return result


def validate_runner():
    """
    启动校验任务
    """
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(validate_task())
    loop.close()


def subscribe_validator():
    """
    待校验队列
    """
    while True:
        time.sleep(3)
        if client.llen(VALIDATE_QUEUE_KEY):
            try:
                validate_runner()
            except Exception:
                pass
