'''
@Author: qinzhonghe96@163.com
@Date: 2020-03-05 16:20:03
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-06 10:37:17
@Description: 从web　api中提取代理
'''

import scrapy
from GeeProxy.items import GeeproxyItem
from GeeProxy.utils.tools import construct_proxy_url


class FileSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):

        self.name = kwargs["name"]
        self.allowed_domains = kwargs["allowed_domains"]
        self.start_urls = kwargs["start_urls"]

    def parse(self, response):

        text = response.text.replace("\r", "")
        proxies = text.split("\n")
        for proxy in proxies:
            if proxy:
                ip, port = tuple(proxy.split(":"))
                item = GeeproxyItem(url=construct_proxy_url("http", ip, port),
                                    protocol="http",
                                    ip=ip,
                                    port=port)
                yield item
