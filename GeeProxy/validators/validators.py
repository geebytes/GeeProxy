'''
@Author: John
@Date: 2020-03-01 18:33:41
@LastEditors: John
@LastEditTime: 2020-03-03 23:38:23
@Description: 代理校验器
'''
import requests
import asyncio
import time
from GeeProxy.utils.logger import proxy_validator
from aiohttp import ClientSession, ClientTimeout, ClientError
from aiohttp.client_exceptions import ClientHttpProxyError, ClientOSError
from aiohttp_proxy import ProxyConnector, ProxyType
from GeeProxy.settings import VAILDATORS_TIMEOUT, VAILDATORS_RETRY, PROXY_REQUEST_DELAY
from GeeProxy.utils.user_agent import UserAgent


class ProxyValidator:
    '''
      异步代理校验器
    '''

    def __init__(self):
        self.retry = 0
        self.timeout = ClientTimeout(total=VAILDATORS_TIMEOUT)
        self.ua = UserAgent()
        self.result = {}
    async def check_proxy(self, proxy: str, dst: str, cache_key: str) -> dict:
        result = {"useful": True, "cache_key": cache_key, "proxy": proxy,"delay":-1,"dst":dst}
        time_start = time.time()
        try:
            # 启用代理
            connector = ProxyConnector.from_url(proxy)
            requests.urllib3.disable_warnings()
            async with ClientSession(connector=connector, timeout=self.timeout) as session:
                # 异步http请求
                async with session.get(dst, ssl=False, timeout=self.timeout, headers={"User-Agent": self.ua.random()}) as response:
                    proxy_validator.info(
                        "wait proxy {} for {} response".format(proxy, dst))
                    await response.text()
                await session.close()
            time_end = time.time()
            delay = time_end - time_start
            proxy_validator.info("check proxy {} for {} success cost {} s".format(
                proxy, dst, delay))
            result["delay"] = delay
            # 最大的请求延迟
            if delay <= PROXY_REQUEST_DELAY:
                result["useful"] = True
                return result
            result["useful"] = False
            return result
        except (BaseException, asyncio.TimeoutError, ClientError, ClientHttpProxyError) as e:
            err_msg = e
            if isinstance(e, asyncio.TimeoutError) or isinstance(e, ClientHttpProxyError):
                err_msg = "Http request timeout"
            result["useful"] = False
            if self.retry <= VAILDATORS_RETRY:
                self.retry = self.retry + 1
                result = await self.check_proxy(proxy, dst, cache_key)
                return result
            time_end = time.time()
            proxy_validator.error(
                "check proxy {} {} times fail for {} and cost {} s".format(proxy, self.retry, dst, time_end - time_start))
            proxy_validator.error(
                "check proxy {} for {} error:{} type {}".format(proxy, dst, err_msg,type(e)))
            self.retry = 0
            result["delay"] = time_end - time_start
            return result
