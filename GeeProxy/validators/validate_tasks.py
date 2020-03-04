'''
@Author: John
@Date: 2020-03-02 17:14:07
@LastEditors: John
@LastEditTime: 2020-03-05 01:03:42
@Description: 定时校验任务
'''
import asyncio
import time
from GeeProxy.settings import VAILDATORS, VALIDATE_CHANNEL,\
     VALIDATE_QUEUE_KEY, ITEM_HASH_KEY
from GeeProxy.utils.redis_cli import client
from GeeProxy.validators.validators import ProxyValidator
from GeeProxy.utils.logger import proxy_validator
from GeeProxy.utils.tools import get_domain


async def validate_task():
    """
    异步代理校验任务
    """
    tasks = []
    result = None
    proxy = client.spop(VALIDATE_QUEUE_KEY)
    while proxy:
        proxy_validator.info(
            "This proxy {} has joined the validation task.".format(proxy))
        for k, v in VAILDATORS.items():
            vaildator = ProxyValidator()
            tasks.append(vaildator.check_proxy(proxy=proxy, dst=v,
                                               cache_key=k))
        proxy = client.spop(VALIDATE_QUEUE_KEY)
    if tasks:
        result, _ = await asyncio.wait(tasks)
        pipelines = client.pipeline()
        for r in result:
            res = r.result()
            proxy_validator.info(
                "The reuslt validate proxy {} of '{}' is {}.".format(
                    res["proxy"], res["cache_key"],
                    "useful" if res["useful"] else "unavailable"))
            try:
                if not res["useful"]:
                    # 不可用就删除
                    pipelines.srem(res["cache_key"], res["proxy"])
                    pipelines.delete(
                        ITEM_HASH_KEY.format(proxy=res["proxy"],
                                             domain=get_domain(res["dst"])))
                    proxy_validator.info("delete proxy {}".format(
                        res["proxy"]))
                else:
                    proxy_validator.info("update proxy {}".format(
                        res["proxy"]))
                    key = ITEM_HASH_KEY.format(proxy=res["proxy"],
                                               domain=get_domain(res["dst"]))
                    pipelines.hset(key, "delay", res["delay"])
                    pipelines.sadd(res["cache_key"], res["proxy"])
            except Exception as e:
                proxy_validator.error(
                    "An exception {} occurred while checking \
                        proxy {} availability.".format(e, res["proxy"]))
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
    for msg in p.listen():
        if msg['type'] == 'message':
            proxy_validator.info(
                "Process has got a message '{}' and has started \
                 validator task.".format(msg["data"]))
            validate_runner()

    # while True:
    #     message = p.get_message()
    #     if message:
    #         proxy_validator.info(
    #             "Process has got a message '{}' and has started \
    #             validator task."
    #             .format(message))
    #         validate_runner()
    #     time.sleep(0.5)
