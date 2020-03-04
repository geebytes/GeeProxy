'''
@Author: John
@Date: 2020-03-03 12:24:30
@LastEditors: John
@LastEditTime: 2020-03-04 10:55:17
@Description: 发布消息，待校验代理入队列
'''

from GeeProxy.utils.redis_cli import client
from GeeProxy.utils.logger import proxy_validator
from GeeProxy.settings import VALIDATE_QUEUE_KEY, VALIDATE_CHANNEL, VALIDATE_MSG, PROXY_KEY_PATTERN


def vaildate_pub():
    pipe = client.pipeline(transaction=False)
    # 获取所有的代理
    proxy_keys = client.keys(PROXY_KEY_PATTERN)
    for proxy in proxy_keys:
        pipe.hget(proxy, "url")
        proxy_validator.info("proxy key {} ready vildate".format(proxy))
    proxies = pipe.execute()
    for proxy in proxies:
        if proxy:
           pipe.sadd(VALIDATE_QUEUE_KEY, proxy)
           proxy_validator.info("This proxy '{}' has enter queue".format(proxy))
    pipe.execute()
    client.publish(VALIDATE_CHANNEL, "validator")
