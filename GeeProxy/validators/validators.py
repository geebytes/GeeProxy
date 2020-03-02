'''
@Author: John
@Date: 2020-03-01 18:33:41
@LastEditors: John
@LastEditTime: 2020-03-02 18:06:08
@Description: 代理校验器
'''
import requests
import asyncio
import time
from GeeProxy.utils.logger import proxy_validator
from aiohttp import ClientSession, ClientTimeout, ClientError
from aiohttp_proxy import ProxyConnector, ProxyType
from GeeProxy.settings import VAILDATORS_TIMEOUT, VAILDATORS_RETRY
from GeeProxy.utils.user_agent import UserAgent

class ProxyValidator:
    '''
      异步代理校验器
    '''
    def __init__(self):
        self.retry = 0
        self.timeout = ClientTimeout(total=VAILDATORS_TIMEOUT)
        self.ua = UserAgent()
    async def check_proxy(self, proxy: str, dst: str,cache_key:str) -> (bool,str,str):
        time_start = time.time()
        try:
            # 启用代理
            connector = ProxyConnector.from_url(proxy)
            requests.urllib3.disable_warnings()
            time_start = time.time()
            async with ClientSession(connector=connector, timeout=self.timeout) as session:
                # 异步http请求
                async with session.get(dst, ssl=False, timeout=self.timeout, headers={"User-Agent": self.ua.random()}) as response:
                    proxy_validator.info(
                        "wait proxy {} for {} response".format(proxy,dst))
                    await response.text()
                await session.close()
            time_end = time.time()
            proxy_validator.info("check proxy {} for {} success cost {} s".format(proxy, dst, time_end - time_start))
            return True, cache_key, proxy
        except (BaseException, asyncio.TimeoutError, ClientError) as e:
            err_msg = str(e)
            if isinstance(e, asyncio.TimeoutError):
               err_msg = "Http request timeout"
            if self.retry <=VAILDATORS_RETRY:
               self.retry = self.retry + 1
               result,cache_key,_ = await self.check_proxy(proxy,dst,cache_key)
               return result, cache_key, proxy
            time_end = time.time()
            proxy_validator.error(
                "check proxy {} {} times fail for {} and cost {} s".format(proxy, self.retry, dst, time_end - time_start))
            proxy_validator.error("check proxy {} for {} error: {}".format(proxy, dst, err_msg))
            self.retry = 0
            return False,cache_key, proxy
