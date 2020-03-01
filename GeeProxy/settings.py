'''
@Author: John
@Date: 2020-03-01 02:10:32
@LastEditors: John
@LastEditTime: 2020-03-01 23:59:42
@Description: 配置文件
'''
# -*- coding: utf-8 -*-

import os
# Scrapy settings for GeeProxy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'GeeProxy'

SPIDER_MODULES = ['GeeProxy.spiders']
NEWSPIDER_MODULE = 'GeeProxy.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'GeeProxy (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'GeeProxy.middlewares.GeeproxySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'GeeProxy.middlewares.RandomUserAgentMiddleware': 543,
    'GeeProxy.middlewares.ProxyRetryMiddleware': 543,
    'GeeProxy.middlewares.ProxyMiddleware':542,
    # 'GeeProxy.middlewares.GeeproxyDownloaderMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'GeeProxy.pipelines.GeeproxyPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# 缓存Scrapy会缓存你有的Requests
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 启用redis集群模式
REDIS_CLUSTER = True

# 集群节点
REDIS_NODES = [
    {
        'host':'192.168.0.3', 'port':7000
    },
    {
        'host': '192.168.0.3', 'port': 7001
    },
    {
        'host': '192.168.0.3', 'port': 7002
    },
    {
        'host': '192.168.0.3', 'port': 7003
    },
    {
        'host': '192.168.0.3', 'port': 7004
    },
    {
        'host': '192.168.0.3', 'port': 7005
    },
]

# redis密码
REDIS_PASSWORD = ""

# redis single mode
REDIS_SERVER = {
    "host": "",
    "port": ""
}

LOG_PATH = os.path.abspath(os.path.dirname(__file__)) + '/logs'
if not os.path.exists(LOG_PATH):
   os.mkdir(LOG_PATH)
   
HTTPERROR_ALLOWED_CODES = [403]
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403]
try:
    from dev_config import *
except:
    print("use dev config file")
    pass
