'''
@Author: John
@Date: 2020-03-01 02:10:32
@LastEditors: John
@LastEditTime: 2020-03-01 23:46:24
@Description: 
'''
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from GeeProxy.validators.validators import ProxyValidator
from GeeProxy.utils.redis_cli import pipeline

class GeeproxyPipeline(object):
    '''
    代理可用性校验
    
    '''
    vaildator = ProxyValidator()
    count = 0
    def process_item(self, item, spider):
        is_useful = self.vaildator.check_proxy(
            proxy=item["url"], dst="https://httpbin.org/ip")
        if is_useful:
            pipeline.sadd(item["protocol"], item["url"])
            self.count = self.count + 1
            if self.count == 5:
               pipeline.execute()
               self.count = 0
            return item
        return None
       
