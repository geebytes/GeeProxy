'''
@Author: John
@Date: 2020-03-01 11:29:03
@LastEditors: John
@LastEditTime: 2020-03-02 20:12:41
@Description: 
'''

# -*- coding: utf-8 -*-
import scrapy
from GeeProxy.items import GeeproxyItem
from scrapy.selector import Selector
from GeeProxy.utils.logger import crawler_logger


class BaseSpider(scrapy.Spider):
    
    def __init__(self, *args, **kwargs):
        
        self.name = 'GeeProxy'
        self.allowed_domains = kwargs["allowed_domains"]
        self.start_urls = kwargs["start_urls"]
        self.table_xpath_expression = kwargs["table_xpath_expression"]
        self.ip_expression = kwargs["ip_xpath_expression"]
        self.port_expression = kwargs["port_xpath_expression"]
        self.protocol_xpath_expression = kwargs["protocol_xpath_expression"]

    def parse(self, response):
        items = self.common_parse(
            response, self.table_xpath_expression, self.ip_expression, self.port_expression, self.protocol_xpath_expression)
        for item in items:
            yield item

    def common_parse(self, response, table_xpath_expression, ip_expression, port_expression, protocol_xpath_expression):
        items = list()
        try:
            # 数据表
            table = response.xpath(table_xpath_expression).extract()
            if not table:
                crawler_logger.error({"url": response.url, "info": "获取表格失败", "table_xpath_expression":table_xpath_expression})
                return items
            table = table[0]
            # ip列表
            ips = Selector(text=table).xpath(ip_expression).extract()
            # 端口
            ports = ""
            # 协议
            protocols = Selector(text=table).xpath(
                protocol_xpath_expression).extract()
            if port_expression:
               ports = Selector(text=table).xpath(port_expression).extract()
        except Exception as e:
            crawler_logger.error({"url":response.url,"error":e.args})
            return items
        try:
            for index, ip in enumerate(ips):
                if port_expression:
                    port = ports[index]
                else:
                    port = ip.split(":")[1]
                    ip = ip.split(":")[0]
                # 是否同时支持http、https
                protocol = protocols[index]
                if "https" in protocol or "HTTPS" in protocol:
                    items.append(GeeproxyItem(
                           url=self.construct_proxy_url("https", ip, port), ip=ip, protocol="https", port=port))
                if "http" in protocol or "HTTP" in protocol:
                    items.append(GeeproxyItem(
                        url=self.construct_proxy_url("http", ip, port), ip=ip, protocol="http", port=port))
        except Exception as e:
            crawler_logger.error({"url": response.url, "error": e.args,"ips":ips})
            return items
        return items

    def construct_proxy_url(self, scheme, ip, port):
        """construct proxy urls, so spiders can use them directly"""
        return '{}://{}:{}'.format(scheme, ip, port)
