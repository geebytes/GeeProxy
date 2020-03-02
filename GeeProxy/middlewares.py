# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
import time
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.utils.response import response_status_message
from .utils.user_agent import UserAgent
from .utils.redis_cli import client
from .utils.logger import middlewares_logger
from .utils.tools import get_domain
from GeeProxy.settings import PROXY_THRESHOLD, PROXY_VALIDATE_TIME

class GeeproxySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        url = response.url
        # middlewares_logger.info(
        #     "spider request meta {} response meta {}".format(response.request.meta, response.meta))
        proxy = response.meta['proxy']
        protocol = response.meta['protocol']
        domain = get_domain(url)
        now_time = int(round(time.time() * 1000))
        key = "{}:{}".format(protocol,domain)
        value = {proxy: now_time}
        middlewares_logger.info("update proxy {} timestamp of '{}' with value '{}'".format(
            proxy, key,value))
        # 更新时间戳
        client.zadd(key,value)
        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            middlewares_logger.info("spider output {}".format(i))
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class GeeproxyDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        

class ProxyMiddleware(object):
    """
    提供IP代理中间件
    """

    def process_request(self, request, spider):
        # print(type(client.srandmember("https")))
        protocol = request.url.split(":")[0]
        options = {"http": "https", "https": "http"}
        key = ""
        domain = ""
        number = 0
        def get_proxy_number():
            nonlocal domain
            nonlocal key
            nonlocal number
            domain = get_domain(request.url)
            key = "{}:{}".format(protocol, domain)
            number = client.zcard(key)
        get_proxy_number()
        if not number:
            # 当前的协议没有对应的代理则切换代理的协议
            protocol = options[protocol]
            get_proxy_number()
        index = random.randint(0, number - 1)
        proxy = client.zrange(key, index, index)
        if proxy:
            proxy = proxy[0]
            middlewares_logger.info("add proxy %s" %
                                    str(proxy, encoding='utf-8'))
            request.meta['proxy'] = str(proxy, encoding='utf-8')
            request.meta['protocol'] = protocol
        return None


class ProxyRetryMiddleware(RetryMiddleware):
    def delete_proxy(self, url, proxy):
        if proxy:
            domain = get_domain(url)
            key = "fail_proxy"
            value = "{}:{}".format(proxy,domain)
            count = client.zscore(key, value)
            if count != PROXY_THRESHOLD:
                client.zincrby(key, 1, value)
            else:
                protocol = proxy.split(":")[0]
                domain = get_domain(url)
                middlewares_logger.info("delete proxy %s" % value)
                client.zrem("{}:{}".format(protocol, domain), proxy)
                client.zrem(key,value)

    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # 删除该代理
            self.delete_proxy(request.url, request.meta.get('proxy', False))
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            # 删除该代理
            self.delete_proxy(request.url, request.meta.get('proxy', False))
            middlewares_logger.info('连接异常, 进行重试...')
            request.headers['User-Agent'] = UserAgent.random()
            return self._retry(request, exception, spider)


class RandomUserAgentMiddleware(UserAgentMiddleware):
    """
    提供UserAgent代理中间件
    """

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent=UserAgent.random()
        )

    def process_request(self, request, spider):
        # 设置请求头代理
        request.headers['User-Agent'] = UserAgent.random()
        
