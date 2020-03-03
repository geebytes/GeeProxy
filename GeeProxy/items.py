'''
@Author: John
@Date: 2020-03-01 02:10:32
@LastEditors: John
@LastEditTime: 2020-03-03 13:08:11
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
    
    
