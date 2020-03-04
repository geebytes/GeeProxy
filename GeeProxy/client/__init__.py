'''
@Author: John
@Date: 2020-03-04 13:09:06
@LastEditors: John
@LastEditTime: 2020-03-04 16:55:54
@Description: 
'''
from GeeProxy.utils.redis_cli import client
from GeeProxy.settings import WEB_AVAILABLE_PROXIES
from GeeProxy.utils.logger import client_logger


class GeeProxyClientException(Exception):
    pass

class NotDefinedWebKey(GeeProxyClientException):
    pass

class AvailableProxy:
    
    def __init__(self):
        self.web = None
    
    def _get_available_proxy(self) -> str:
        return client.srandmember(self.web)

    def _get_available_proxies(self) -> list:
        return client.smembers(self.web)

    def available_proxy(self, web:str, all=False) -> list:
        if not WEB_AVAILABLE_PROXIES.get(web):
            raise NotDefinedWebKey("No proxy available for this site {}".format(web))
        self.web = web
        if all:
            return self._get_available_proxies()
        else:
            return [self._get_available_proxy()]
            
