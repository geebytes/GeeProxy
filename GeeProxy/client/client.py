'''
@Author: John
@Date: 2020-03-04 13:09:06
@LastEditors: John
@LastEditTime: 2020-03-10 19:56:41
@Description: 提供代理查询、删除接口
'''
import time
from GeeProxy.utils.redis_cli import client, acquire_lock, release_lock
from GeeProxy.settings import WEB_AVAILABLE_PROXIES, PROXY_THRESHOLD, \
    ITEM_HASH_KEY, WEB_TRANSPARENT_PROXY, \
    ALLOWED_TRANSPARENT_PROXY, VAILDATORS, PROXY_LOCK
from GeeProxy.validators.validators import ValidateResult
from GeeProxy.utils.logger import client_logger
from GeeProxy.utils.tools import get_domain, get_cache_key
from GeeProxy.items import GeeproxyItem


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
            proxies = self._get_available_proxies()
            return list(proxies) if proxies else []
        else:
            proxy = self._get_available_proxy()
            return [proxy] if proxy else []

    @staticmethod
    async def delete_proxy(proxy: str, web_key: str):
        '''
            删除代理,主要逻辑是先取到这个代理请求目标网站失败的次数，
            若等于预先设定阈值，则直接删除，否则计数器加１;
            如果进入删除流程，先判断是否有网站还在使用该代理,
            即hash表中引用计数器等于0时就直接删除该代理，否则引用计数器减1,
            随后删除目标网站代理集合中的代理和请求失败集合中的代理。
        '''
        if proxy:
            key = "fail_proxy"
            cache_key = WEB_AVAILABLE_PROXIES.get(web_key)
            web = VAILDATORS.get(cache_key)
            value = "{}:{}".format(proxy, get_domain(web))
            # 代理请求失败的次数
            client.zincrby(key, 1, value)
            count = client.zscore(key, value)
            pipe = client.pipeline()
            lock_name = PROXY_LOCK.format(ITEM_HASH_KEY.format(proxy=proxy))
            identifier = acquire_lock(client, lock_name)
            client_logger.info(
                " Delete lock name is {} and identifier is {}".format(
                    lock_name, identifier))
            try:
                proxy_key = ITEM_HASH_KEY.format(proxy=proxy)
                if count < PROXY_THRESHOLD:
                    client_logger.info("Count={} and Do not delete {}".format(
                        count, value))
                else:
                    # 进入删除流程
                    client_logger.info("Count={} and delete {}".format(
                        count, value))
                    pipe.srem(cache_key, proxy)
                    pipe.hdel(proxy_key, proxy)
                    pipe.zrem(key, value)
                    count = client.hincrby(proxy_key, "counter", -1)
                    if count <= 0:
                        pipe.delete(proxy_key)
                        client_logger.info("delete proxy %s" % value)
                pipe.execute()
            except Exception as e:
                client_logger.error(
                    "An exception {} occurred while delete a proxy {} to the cache"
                    .format(str(e), proxy))
            finally:
                # client.unwatch()
                client_logger.info(
                    "Release delete lock name is {} and identifier is {}".
                    format(lock_name, identifier))
                release_lock(client, lock_name, identifier)

    @staticmethod
    async def add_proxy(data: ValidateResult, item: GeeproxyItem) -> bool:
        """
            添加代理，主要逻辑是，判断hash表中是否已经存在该代理，
            若不存在就将对应数据存入,否则就在该代理的hash对象中加上
            以目标网站地址的字段并以延迟为值,引用计数器加1。
        """
        mapping = data.__dict__
        try:
            # 匿名代理直接缓存，否则判断是否允许透明代理访问目标站点
            if not item["anonymous"] and not ALLOWED_TRANSPARENT_PROXY:
                return False
            cache_key = get_cache_key(data.web_key)
            if item["anonymous"] or WEB_TRANSPARENT_PROXY[data.web_key]:
                client.sadd(cache_key, data.proxy)
            protoclo_key = WEB_AVAILABLE_PROXIES[item["protocol"]]
            client.sadd(protoclo_key, data.proxy)
            key = ITEM_HASH_KEY.format(proxy=data.proxy)
            client_logger.info("Cache proxy '{}' to '{}'".format(
                data.proxy, cache_key))
            exist = client.exists(key) and client.hexists(key, "counter")
            if not exist:
                timestamp = int(round(time.time() * 1000))
                mapping["timestamp"] = timestamp
                mapping["available"] = 1
                mapping[data.dst] = data.delay
                mapping["counter"] = 1  # 引用计数器
                mapping.pop("delay")
                mapping.pop("dst")
                mapping.pop("web_key")
                mapping.update(dict(item))
                client.hmset(key, mapping)
                client_logger.info("Cache proxy '{}' to '{}'".format(
                    data.proxy, key))
            else:
                dst = client.hexists(key, data.proxy)
                if not dst:
                    if await AvailableProxy.update_proxy_delay(
                            data.proxy, data.dst, data.delay):
                        client.hincrby(key, "counter", 1)
                client_logger.info(
                    "Cache proxy '{}' delay time to '{}'".format(
                        data.proxy, key))
            return True
        except Exception as e:
            client_logger.error(
                "An exception {} occurred while adding a proxy {} to the cache"
                .format(str(e), mapping))
            return False

    @staticmethod
    async def update_proxy_delay(proxy: str, dst: str, delay: float) -> bool:
        """
            更新代理对目标站点的延迟
        """
        key = ITEM_HASH_KEY.format(proxy=proxy)
        lock_name = PROXY_LOCK.format(key)
        identifier = acquire_lock(client, lock_name)
        client_logger.info(
            "Update lock name is {} and identifier is {}".format(
                lock_name, identifier))
        pipe = client.pipeline()
        try:
            if client.exists(key):
                if not client.hexists(key, dst):
                    pipe.hincrby(key, "counter", 1)
                pipe.hset(key, dst, delay)
                pipe.execute()
                client_logger.info(
                    "update proxy {} delay of '{}' with value '{}'".format(
                        proxy, key, delay))
                return True
        except Exception as e:
            client_logger.error(
                "An exception {} occurred while update a proxy {} to the cache"
                .format(str(e), proxy))
            return False
        finally:
            client_logger.info(
                "Release update lock name is {} and identifier is {}".format(
                    lock_name, identifier))
            release_lock(client, lock_name, identifier)

    @staticmethod
    def proxy_exist(proxy: str):
        return client.exists(ITEM_HASH_KEY.format(proxy=proxy))
