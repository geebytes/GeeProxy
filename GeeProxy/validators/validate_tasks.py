'''
@Author: John
@Date: 2020-03-02 17:14:07
@LastEditors: John
@LastEditTime: 2020-03-02 18:53:26
@Description: 定时校验任务
'''
import asyncio
import time
from GeeProxy.settings import VAILDATORS_RETRY, VAILDATORS_TIMEOUT, VAILDATORS, PROXY_VALIDATE_TIME, VAILDATORS
from GeeProxy.utils.redis_cli import client
from GeeProxy.validators.validators import ProxyValidator
from GeeProxy.utils.logger import proxy_validator

async def validate_task():
    now_time = int(round(time.time() * 1000))
    end_time = now_time - PROXY_VALIDATE_TIME * 1000
    start_time = end_time - PROXY_VALIDATE_TIME * 1000
    tasks = []
    result = None
    for k, v in VAILDATORS.items():
        # 校验前一个10mim区间的值
        proxies = client.zrangebyscore(k,start_time,end_time)
        for proxy in proxies:
            vaildator = ProxyValidator()
            proxy = str(proxy,'utf-8')
            tasks.append(vaildator.check_proxy(proxy=proxy, dst=v, cache_key=k))
    if tasks:
         result, _ = await asyncio.wait(tasks)
         pipelines = client.pipeline()
         for r in result:
             proxy_validator.info("The reuslt validate proxy {} of '{}' is {}".format(
                 r.result()[2], r.result()[1], "success" if r.result()[0] else "fail"))
             if not r.result()[0]:
                 #不可用就删除
                 pipelines.zrem(r.result()[1], r.result()[2])
                 proxy_validator.info("delete proxy {}".format(r.result()[2]))
             else:
                 # 可用的就更新时间戳
                 now_time = int(round(time.time() * 1000))
                 proxy_validator.info("update proxy {}".format(r.result()[2]))
                 pipelines.zadd(r.result()[1], {r.result()[2]:now_time})
         # 提交更新操作
         pipelines.execute()
    return result


def validate_run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(validate_task())
    loop.close()


        



