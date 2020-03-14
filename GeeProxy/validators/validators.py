'''
@Author: qinzhonghe96@163.com
@Date: 2020-03-01 18:33:41
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-10 19:51:30
@Description: 代理校验器
'''
import os
import requests
import asyncio
import time
import json
import ssl
from GeeProxy.utils.logger import proxy_validator
from aiohttp import ClientSession, ClientTimeout, ClientError, ClientSSLError
from aiohttp.client_exceptions import ClientHttpProxyError
from aiohttp_proxy import ProxyConnector
from GeeProxy.settings import VAILDATORS_TIMEOUT,\
     VAILDATORS_RETRY, PROXY_REQUEST_DELAY, PUBLIC_IP,\
     ANONYMOUS_CHECK_API
from GeeProxy.utils.user_agent import UserAgent


class AiohttpSingleton(ClientSession):
    '''
        This is a redis singleton connect client class
    '''
    def __new__(cls, *args, **keywords):
        pid = os.getpid()
        if not hasattr(cls, '_instance') or pid != cls._pid:
            print("Aiohttp PID is {} and father PID is {}".format(
                os.getpid(), os.getppid()))
            if hasattr(cls, "_pid"):
                print("Aiohttp Instance PID is {} and PID is {}".format(
                    cls._pid, pid))
            cls._instance = ClientSession(*args, **keywords)
            cls._pid = os.getpid()
        return cls._instance

    @property
    def connector(self, connector):
        proxy_connector = connector
        self._instance._connector = proxy_connector


class ValidateResult:
    """
    校验结果
    """
    def __init__(self, proxy=None, web_key=None, delay=-1, dst=None, useful=1):
        """
        :param proxy: 代理地址
        :param web_key: 缓存key
        :param delay: 延迟
        :param dst: 目标站点
        :param useful: 是否可用
        """
        # 代理地址
        self.proxy = proxy
        # 缓存key
        self.web_key = web_key
        # 延迟
        self.delay = delay
        # 目标站点
        self.dst = dst
        # 是否为可匿代理
        # self.anonymous = anonymous
        # 是否可用
        self.available = useful


class ProxyValidator:
    """
      异步代理校验器,校验过程如下，通过代理请求目标站点，若超时,
      则重试，当重试次数大于给定的阈值时，请求仍失败就认为这个代理不可用,
      期间会计算请求过程的延迟。
    """
    def __init__(self):
        self._retry = 0
        self._timeout = ClientTimeout(total=VAILDATORS_TIMEOUT)
        self._ua = UserAgent()
        self._result = {}

    async def check_proxy(self, proxy: str, dst: str, web_key: str) -> ValidateResult:
        """
        校验代理的可用性

        :param proxy: 待校验的代理
        :param dst: 目标站点地址
        :param web_key: 目标站点
        :return: 校验结果
        """
        result = ValidateResult(proxy=proxy, delay=-1, web_key=web_key, dst=dst, useful=1)
        time_start = time.time()
        try:
            # 启用代理
            connector = ProxyConnector(verify_ssl=False).from_url(proxy)
            requests.urllib3.disable_warnings()
            # 异步http请求
            async with ClientSession(connector=connector,
                                     timeout=self._timeout) as session:
                params = {
                    "url": dst,
                    "verify_ssl": False,
                    "timeout": self._timeout,
                    "headers": {
                        "User-Agent": self._ua.random()
                    }
                }
                # verify_ssl = False
                if "https" in proxy.split(":"):
                    params["verify_ssl"] = False
                # 异步http请求
                async with session.get(**params) as response:
                    proxy_validator.info(
                        "wait proxy {} for {} response".format(proxy, dst))
                    await response.text()
                await session.close()
            time_end = time.time()
            delay = time_end - time_start
            proxy_validator.info(
                "check proxy {} for {} success cost {} s".format(
                    proxy, dst, delay))
            result.delay = delay
            result.available = 1
            # 请求超时就认为代理不可用
            if delay > PROXY_REQUEST_DELAY:
                result.available = 0
            return result
        except (BaseException, asyncio.TimeoutError, ClientError,
                ClientHttpProxyError, ClientSSLError) as e:
            err_msg = e
            if isinstance(e, asyncio.TimeoutError) or isinstance(
                    e, ClientHttpProxyError):
                err_msg = "Http request timeout"
            if not isinstance(e, ClientSSLError) or not isinstance(
                    e, ssl.SSLError):
                result.available = 0
            # 重试
            if self._retry <= VAILDATORS_RETRY:
                # 重试次数小于阈值就再试一次
                self._retry = self._retry + 1
                result = await self.check_proxy(proxy, dst, web_key)
                return result
            time_end = time.time()
            proxy_validator.error("check proxy {} {} times fail for {} "
                                  "and cost {} s".format(proxy, self._retry, dst, time_end - time_start))
            proxy_validator.error("check proxy {} for {} "
                                  "error:{} type {}".format(proxy, dst, err_msg, type(e)))
            self._retry = 0
            result.delay = time_end - time_start
            return result

    @staticmethod
    async def check_anonymous(proxy: str) -> bool:
        """
        检测代理的匿名程度

        :param proxy: 待校验的代理
        :return: 校验结果,如果是高匿代理就返回True
        """
        anonymous = True
        try:
            connector = ProxyConnector.from_url(proxy)
            requests.urllib3.disable_warnings()
            ua = UserAgent()
            async with ClientSession(connector=connector, timeout=5) as session:
                # 异步http请求
                async with session.get(ANONYMOUS_CHECK_API,
                                       ssl=False,
                                       headers={"User-Agent": ua.random()},
                                       timeout=5) as response:
                    res = await response.text()
                    res = json.loads(res)
                    anonymous = ProxyValidator.is_anonymous(res)
                    if anonymous:
                        proxy_validator.info("The proxy {} is anonymous".format(proxy))
                await session.close()
                return anonymous
        except Exception as e:
            proxy_validator.error("Checking proxy {} anonymous "
                                  "has an error:{} type {}".format(proxy, str(e), type(e)))
            raise ClientError("check anonymous")

    @staticmethod
    def is_anonymous(response: dict) -> bool:
        """
        通过接口判断当前代理的可匿程度

        :param response: 请检测api的响应
        :return: 校验结果,如果是高匿代理就返回True
        """
        origin = response["origin"]
        proxy_connection = response.get("Proxy-Connection", "")
        proxy_validator.info(
            "Checking anonymous proxy response is {}".format(response))
        if origin != PUBLIC_IP and not proxy_connection:
            return True
        return False
