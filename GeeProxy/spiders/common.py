"""
@Author: qinzhonghe96@163.com
@Date: 2020-03-01 11:29:03
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-10 11:44:32
@Description: 代理抓取主程序
主要的实现思路是，先拿到页面的Table，然后进一步解析拿到的Table，分别提取端口、IP、协议
"""

# -*- coding: utf-8 -*-

from scrapy_redis_cluster.spiders import RedisSpider
from GeeProxy.items import GeeproxyItem
from scrapy.selector import Selector
from GeeProxy.utils.logger import crawler_logger
from GeeProxy.utils.tools import construct_proxy_url


class BaseSpider(RedisSpider):
    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        self.name = kwargs["name"]
        self.allowed_domains = kwargs["allowed_domains"]
        self.table_xpath_expression = kwargs["table_xpath_expression"]
        self.ip_expression = kwargs["ip_xpath_expression"]
        self.port_expression = kwargs["port_xpath_expression"]
        self.protocol_xpath_expression = kwargs["protocol_xpath_expression"]
        self.next_page = kwargs["next_page"]
        self.max_page = kwargs["max_page"]

    def parse(self, response):
        items = self.common_parse(response, self.table_xpath_expression,
                                  self.ip_expression, self.port_expression,
                                  self.protocol_xpath_expression)
        for item in items:
            yield item

    def common_parse(self, response, table_xpath_expression, ip_expression,
                     port_expression, protocol_xpath_expression):
        items = list()
        try:
            # 先拿到数据表
            table = response.xpath(table_xpath_expression).extract()
            if not table:
                crawler_logger.error(
                    "Getting table fail from {} while"
                    " using {}.".format(response.url, table_xpath_expression))
                return items
            table = table[0]
            # ip列表
            ips = Selector(text=table).xpath(ip_expression).extract()
            # 端口
            ports = ""
            # 协议
            protocols = Selector(text=table).xpath(protocol_xpath_expression).extract()
            if port_expression:
                ports = Selector(text=table).xpath(port_expression).extract()
        except Exception as e:
            crawler_logger.error({"url": response.url, "error": e.args})
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
                if "http" in protocol or "HTTP" in protocol:
                    items.append(
                        GeeproxyItem(
                            url=construct_proxy_url("http", ip, port),
                            ip=ip,
                            protocol="http",
                            port=port)
                    )
                if "https" in protocol or "HTTPS" in protocol:
                    items.append(
                        GeeproxyItem(url=construct_proxy_url("https", ip, port),
                                     ip=ip,
                                     protocol="https",
                                     port=port)
                    )
        except Exception as e:
            crawler_logger.error({
                "url": response.url,
                "error": str(e),
                "ips": ips
            })
            return items
        return items
