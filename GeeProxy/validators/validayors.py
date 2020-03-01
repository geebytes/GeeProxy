'''
@Author: John
@Date: 2020-03-01 18:33:41
@LastEditors: John
@LastEditTime: 2020-03-01 19:00:31
@Description: 
'''
from GeeProxy.utils.logger import proxy_validator
import requests

class ProxyValidator:
    def check_proxy(self,proxy:str,dst:str) -> bool:
        try:
            requests.urllib3.disable_warnings()
            proxies = {'https': proxy, 'http': proxy}
            resp = requests.get(dst, verify=False, timeout=5, proxies=proxies)
            proxy_validator.info("check proxy %s" % proxy)
            proxy = resp.json().get("origin")
            proxy_validator.info("remote proxy %s" % proxy)
            return True
        except Exception :
            proxy_validator.info("check proxy %s fail" % proxy)
            return False
