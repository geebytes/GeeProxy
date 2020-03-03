'''
@Author: John
@Date: 2020-03-02 17:14:07
@LastEditors: John
@LastEditTime: 2020-03-03 21:49:47
@Description: 定时校验任务
'''
import asyncio
import time
from GeeProxy.settings import VAILDATORS_RETRY, VAILDATORS_TIMEOUT, VAILDATORS, \
    PROXY_VALIDATE_TIME, VAILDATORS, VALIDATE_CHANNEL, VALIDATE_QUEUE_KEY, ITEM_HASH_KEY
from GeeProxy.utils.redis_cli import client
from GeeProxy.validators.validators import ProxyValidator
from GeeProxy.utils.logger import proxy_validator
from GeeProxy.utils.tools import get_domain
from GeeProxy.utils.logger import proxy_validator


async def validate_task():
    """
    异步代理校验任务
    """
    tasks = []
    result = None
    proxy = client.spop(VALIDATE_QUEUE_KEY)
    while proxy:
        for k, v in VAILDATORS.items():
            proxy_validator.info("This proxy {} has joined the validation task.".format(proxy))
            vaildator = ProxyValidator()
            tasks.append(vaildator.check_proxy(
                proxy=proxy, dst=v, cache_key=k))
        proxy = client.spop(VALIDATE_QUEUE_KEY)
    if tasks:
        result, _ = await asyncio.wait(tasks)
        pipelines = client.pipeline()
        for r in result:
            res = r.result()
            proxy_validator.info("The reuslt validate proxy {} of '{}' is {}.".format(
                res["proxy"], res["cache_key"], "useful" if res["useful"] else "unuseful"))
            try:
                if not res["useful"]:
                    # 不可用就删除
                    pipelines.srem(res["cache_key"], res["proxy"])
                    pipelines.delete(ITEM_HASH_KEY.format(
                        proxy=res["proxy"], domain=get_domain(res["dst"])))
                    proxy_validator.info(
                        "delete proxy {}".format(res["proxy"]))
                else:
                    proxy_validator.info(
                        "update proxy {}".format(res["proxy"]))
                    key = ITEM_HASH_KEY.format(
                        proxy=res["proxy"], domain=get_domain(res["dst"]))
                    pipelines.hset(key, "delay", res["delay"])
                    pipelines.sadd(res["cache_key"], res["proxy"])
            except Exception as e:
                proxy_validator.error(
                    "An exception {} occurred while checking proxy {} availability.".format(e,
                                                                                            res["proxy"]))
        # 提交更新操作
        pipelines.execute()
    return result


def validate_runner():
    """
    启动校验任务
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(validate_task())
    loop.close()


def subscribe_validator():
    """
    订阅待校验队列
    """
    p = client.pubsub()
    p.subscribe(VALIDATE_CHANNEL)
    while True:
        message = p.get_message()
        if message:
            validate_runner()
        time.sleep(0.5)
