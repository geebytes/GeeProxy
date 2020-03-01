'''
@Author: John
@Date: 2020-03-01 18:33:41
@LastEditors: John
@LastEditTime: 2020-03-01 23:53:45
@Description: 
'''
from GeeProxy.utils.logger import proxy_validator
import requests

class ProxyValidator:
    def __init__(self):
        self.retry = 0
    def check_proxy(self,proxy:str,dst:str) -> bool:
        try:
            requests.urllib3.disable_warnings()
            proxies = {'https': proxy, 'http': proxy}
            requests.get(dst, verify=False, timeout=5, proxies=proxies)
            proxy_validator.info("check proxy %s" % proxy)
            proxy_validator.info("check proxy %s success" %(proxy))
            return True
        except Exception :
            if self.retry <=2:
               self.retry = self.retry + 1
               self.check_proxy(proxy,dst)
            proxy_validator.info(
                "check proxy %s %d times fail" % (proxy, self.retry))
            self.retry = 0
            return False
