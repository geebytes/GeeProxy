'''
@Author: John
@Date: 2020-03-01 02:10:32
@LastEditors: John
@LastEditTime: 2020-03-01 18:52:37
@Description: 
'''
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from GeeProxy.validators.validayors import ProxyValidator

class GeeproxyPipeline(object):
    vaildator = ProxyValidator()
    def process_item(self, item, spider):
        is_useful = self.vaildator.check_proxy(
            proxy=item["url"], dst="https://httpbin.org/ip")
        if is_useful:
           return item
        return None
       
