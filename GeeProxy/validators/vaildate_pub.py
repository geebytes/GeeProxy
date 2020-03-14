"""
@Author: qinzhonghe96@163.com
@Date: 2020-03-03 12:24:30
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-10 13:41:18
@Description: 发布消息，待校验代理入队列
"""

from GeeProxy.utils.redis_cli import client
from GeeProxy.utils.logger import proxy_validator
from GeeProxy.settings import VALIDATE_QUEUE_KEY, \
    VALIDATE_CHANNEL, PUBLISH_LOCK, PROXY_VALIDATE_TIME, WEB_AVAILABLE_PROXIES


def vaildate_pub():
    """
    将待校验的代理送入队列

    :return:
    """
    if client.setnx(PUBLISH_LOCK, "vaildate_publish") == 0 or client.llen(VALIDATE_QUEUE_KEY):
        # 如果已有代理正在入队列，或者队列中存在经过两次校验周期仍存在的代理
        proxy_validator.info("proxy key already vildate.")
    else:
        try:
            client.expire(PUBLISH_LOCK, PROXY_VALIDATE_TIME * 2)
            pipe = client.pipeline()
            # 获取所有的代理
            keys = (v for k, v in WEB_AVAILABLE_PROXIES.items())
            proxy_keys = client.sunion(*keys)
            for proxy in proxy_keys:
                if proxy is not None:
                    pipe.lpush(VALIDATE_QUEUE_KEY, proxy)
                    proxy_validator.info("This proxy '{}' has enter queue".format(proxy))
            pipe.execute()
            client.publish(VALIDATE_CHANNEL, "validator")
        except Exception:
            client.delete(PUBLISH_LOCK)