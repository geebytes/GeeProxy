'''
@Author: qinzhonghe96@163.com
@Date: 2020-03-01 02:10:32
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-06 16:37:56
@Description: 定义数据字段
'''
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GeeproxyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # 代理协议
    protocol = scrapy.Field()

    ip = scrapy.Field()

    port = scrapy.Field()

    url = scrapy.Field()

    anonymous = scrapy.Field()

    available = scrapy.Field()
    