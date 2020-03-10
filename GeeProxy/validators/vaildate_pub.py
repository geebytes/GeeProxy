'''
@Author: John
@Date: 2020-03-03 12:24:30
@LastEditors: John
@LastEditTime: 2020-03-10 02:02:01
@Description: 发布消息，待校验代理入队列
'''

from GeeProxy.utils.redis_cli import client
from GeeProxy.utils.logger import proxy_validator
from GeeProxy.settings import VALIDATE_QUEUE_KEY, \
    VALIDATE_CHANNEL, PROXY_KEY_PATTERN, PUBLISH_LOCK, PROXY_VALIDATE_TIME, WEB_AVAILABLE_PROXIES


def vaildate_pub():
    if client.setnx(
            PUBLISH_LOCK,
            "vaildate_publish") == 0 or client.llen(VALIDATE_QUEUE_KEY):
        proxy_validator.info("proxy key already vildate.")
    else:
        try:
            client.expire(PUBLISH_LOCK, PROXY_VALIDATE_TIME * 2)
            pipe = client.pipeline()
            # 获取所有的代理
            # proxy_keys = client.keys(PROXY_KEY_PATTERN)
            keys = (v for k, v in WEB_AVAILABLE_PROXIES.items())
            proxy_keys = client.sunion(*keys)
            print(proxy_keys)
            # for proxy in proxy_keys:
            #     pipe.hget(proxy, "url")
            #     proxy_validator.info("proxy key {} ready vildate".format(proxy))
            # proxies = pipe.execute()
            for proxy in proxy_keys:
                if proxy is not None:
                    pipe.lpush(VALIDATE_QUEUE_KEY, proxy)
                    proxy_validator.info(
                        "This proxy '{}' has enter queue".format(proxy))
            pipe.execute()
            client.publish(VALIDATE_CHANNEL, "validator")
        except Exception:
            pass