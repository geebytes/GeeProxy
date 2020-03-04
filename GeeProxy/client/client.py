'''
@Author: John
@Date: 2020-03-04 13:09:06
@LastEditors: John
@LastEditTime: 2020-03-04 17:40:04
@Description: 提供代理查询、删除接口
'''
from GeeProxy.utils.redis_cli import client
from GeeProxy.settings import WEB_AVAILABLE_PROXIES, PROXY_THRESHOLD, \
    ITEM_HASH_KEY
from GeeProxy.utils.logger import client_logger


class GeeProxyClientException(Exception):
    pass


class NotDefinedWebKey(GeeProxyClientException):
    pass


class AvailableProxy:

    def __init__(self):
        self.web = None

    def _get_available_proxy(self) -> str:
        """
            随机拿到一个代理
        """
        return client.srandmember(self.web)

    def _get_available_proxies(self) -> list:
        """
          拿到所有的代理
        """
        return client.smembers(self.web)

    def available_proxy(self, web_key: str, all=False) -> list:
        """
            获取可用代理
        """
        if not WEB_AVAILABLE_PROXIES.get(web_key):
            raise NotDefinedWebKey(
                "No proxy available for this site {}".format(web_key))
        self.web = WEB_AVAILABLE_PROXIES.get(web_key)
        if all:
            return self._get_available_proxies()
        else:
            return [self._get_available_proxy()]

    def delete_proxy(self, proxy: str, dst_web_domain: str):
        '''
            删除代理
        '''
        if proxy:
            key = "fail_proxy"
            value = "{}:{}".format(proxy, dst_web_domain)
            count = client.zscore(key, value)
            if count != PROXY_THRESHOLD - 1:
                client.zincrby(key, 1, value)
            else:
                client_logger.info("delete proxy %s" % value)
                client.srem("proxy:{}".format(dst_web_domain), proxy)
                client.delete(ITEM_HASH_KEY.format(
                    proxy=proxy, domain=dst_web_domain))
                client.zrem(key, value)
