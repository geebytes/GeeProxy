# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.utils.response import response_status_message
from GeeProxy.utils.user_agent import UserAgent
from GeeProxy.utils.logger import middlewares_logger
from GeeProxy.utils.tools import get_web_index, get_proxy, \
     update_proxy, del_proxy, get_web_key
from GeeProxy.settings import PROXY_REQUEST_DELAY


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
        if 'proxy' in response.meta and response.meta['proxy']:
            proxy = response.meta['proxy']
            delay = response.meta['download_latency']
            web = get_web_index(url)
            if PROXY_REQUEST_DELAY > delay:
                update_proxy(proxy, web, delay)
            else:
                key = get_web_key(url)
                del_proxy(proxy, key)
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            # middlewares_logger.info("spider output {}".format(i))
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
        # available_proxy = AvailableProxy()
        key = get_web_key(request.url)
        
        proxy = get_proxy(key)
        # print("url is %s" % request.url)
        if proxy:
            middlewares_logger.info("Request {} add proxy {}".format(
                request.url, proxy[0]))
            request.meta['proxy'] = proxy[0]
        return None


class ProxyRetryMiddleware(RetryMiddleware):
    def delete_proxy(self, url, proxy):
        if proxy:
            key = get_web_key(url)
            del_proxy(proxy, key)

    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # 删除该代理
            self.delete_proxy(request.url, request.meta.get('proxy', False))
            # run_sync(coro)

            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            # 删除该代理
            self.delete_proxy(request.url, request.meta.get('proxy', False))
            # run_sync(coro)
            middlewares_logger.info('连接异常, 进行重试...')
            request.headers['User-Agent'] = UserAgent.random()
            return self._retry(request, exception, spider)


class RandomUserAgentMiddleware(UserAgentMiddleware):
    """
    提供UserAgent代理中间件
    """
    @classmethod
    def from_crawler(cls, crawler):
        return cls(user_agent=UserAgent.random())

    def process_request(self, request, spider):
        # 设置请求头代理
        request.headers['User-Agent'] = UserAgent.random()
