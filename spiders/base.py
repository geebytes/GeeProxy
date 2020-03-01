# -*- coding: utf-8 -*-
import scrapy


class BaseSpider(scrapy.Spider):
    name = 'base'
    allowed_domains = ['scrapy.base.com']
    start_urls = ['http://scrapy.base.com/']

    def parse(self, response):
        pass
