'''
@Author: qinzhonghe96@163.com
@Date: 2020-03-01 02:10:32
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-10 19:59:39
@Description: 配置文件
'''
# -*- coding: utf-8 -*-

import os
import requests
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
# USER_AGENT = 'GeeProxy (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 5
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'GeeProxy.middlewares.GeeproxySpiderMiddleware': 543,
}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'GeeProxy.middlewares.RandomUserAgentMiddleware': 543,
    'GeeProxy.middlewares.ProxyRetryMiddleware': 543,
    'GeeProxy.middlewares.ProxyMiddleware': 542,
    # 'GeeProxy.middlewares.GeeproxyDownloaderMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'GeeProxy.extension.SpiderOpenCloseHandler': 500
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'GeeProxy.pipelines.GeeproxyPipeline': None,
    'GeeProxy.pipelines.ProxyAnonymousPipeline': None,
    'GeeProxy.pipelines.GeeProxyNoVaildatePipe': 300
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
#  The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
#  The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
#  The average number of requests Scrapy should be sending in parallel to
#  each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
#  Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

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
REDIS_MASTER_NODES = [
    {
        'host': '192.168.0.3',
        'port': 7000
    },
    {
        'host': '192.168.0.3',
        'port': 7001
    },
    {
        'host': '192.168.0.3',
        'port': 7002
    },
    {
        'host': '192.168.0.3',
        'port': 7003
    },
    {
        'host': '192.168.0.3',
        'port': 7004
    },
    {
        'host': '192.168.0.3',
        'port': 7005
    },
]

REDIS_START_URLS_BATCH_SIZE = 32

# redis密码
REDIS_PASSWORD = ""

# redis single mode
REDIS_SERVER = {"host": "", "port": ""}

LOG_PATH = os.path.abspath(os.path.dirname(__file__)) + '/logs'
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

HTTPERROR_ALLOWED_CODES = [403, 503]

RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403, 302]
# ITEM 对象存储键
ITEM_HASH_KEY = "geeproxy:{proxy}"

PROXY_KEY_PATTERN = "geeproxy:*"
# 待校验消息队列
VALIDATE_QUEUE_KEY = "vaildate:proxy"
# 校验消息发布/订阅频道
VALIDATE_CHANNEL = "vaildators"
# 校验消息的内容
VALIDATE_MSG = "vaildators start"

# 消息发布锁
PUBLISH_LOCK = "public_lock"
# 校验器，校验目标及结果存储键值
VAILDATORS = {
    "proxy:xiladaili": "http://www.xiladaili.com",
    "proxy:xicidaili": "https://www.xicidaili.com",
    "proxy:kuaidaili": "https://www.kuaidaili.com",
    # "proxy:https": "https://httpbin.org",
    # "proxy:http": "http://httpbin.org",
    "proxy:imooc": "https://www.imooc.com/",
    "proxy:ip3366": "http://www.ip3366.net"
}
# 校验器代理请求超时时间
VAILDATORS_TIMEOUT = 5
# 校验器的代理尝试重连次数
VAILDATORS_RETRY = 3
# 代理请求失败的最大次数
PROXY_THRESHOLD = 3
# 定时校验任务时间间隔
PROXY_VALIDATE_TIME = 20 * 60
# 允许校验代理请求的最大延迟时间 s
PROXY_REQUEST_DELAY = 5

# 使用的哈希函数数，默认为6
BLOOMFILTER_HASH_NUMBER = 6

# Bloomfilter使用的Redis内存位，30表示2 ^ 30 = 128MB，默认为22 (1MB 可去重130W URL)
BLOOMFILTER_BIT = 22

# 不清空redis队列
SCHEDULER_PERSIST = False
# 调度队列
SCHEDULER = "scrapy_redis_cluster.scheduler.Scheduler"
# 去重
DUPEFILTER_CLASS = "scrapy_redis_cluster.dupefilter.RFPDupeFilter"
# queue
SCHEDULER_QUEUE_CLASS = 'scrapy_redis_cluster.queue.PriorityQueue'

# 目标站点可用代理
WEB_AVAILABLE_PROXIES = {
    "imooc": "proxy:imooc",
    "http": "proxy:http",
    "https": "proxy:https",
    "xiladaili": "proxy:xiladaili",
    "xicidaili": "proxy:xicidaili",
    "kuaidaili": "proxy:kuaidaili",
    "ip3366": "proxy:ip3366",
}

PUBLIC_IP = "116.9.190.2"
if not PUBLIC_IP:
    try:
        PUBLIC_IP = requests.get("https://httpbin.org/ip", timeout=10).json()["origin"]
        print("公网ip为{}".format(PUBLIC_IP))
    except Exception:
        print("获取本机公网ip失败")
        os._exit(0)
# 代理更新抓取任务时间间隔
PROXY_UPDATE_TIME = 30 * 60 * 1

# 代理可匿程度检测接口
ANONYMOUS_CHECK_API = "https://httpbin.org/get"

# 全局设置是否允许使用透明代理
ALLOWED_TRANSPARENT_PROXY = False

# API　服务端口
API_SERVER_PORT = 5000

# API 地址
API_SERVER = "http://127.0.0.1:5000"

# 针对特定网站设置是否允许透明代理
WEB_TRANSPARENT_PROXY = {
    "xiladaili": False,
    "xicidaili": False,
    "kuaidaili": False,
    "https": False,
    "http": False,
    "imooc": False,
    "ip3366": False
}

# 抓取数据过程中使用的默认代理
DEFAULT_PROXY = "https"

# 在删、改代理字段操作时加锁
PROXY_LOCK = "lock:proxy:{}"

# 待校验数据项
ITEM_VAILDATE_SET = "vaildate:proxy:set"

# TWISTED_REACTOR="twisted.internet.asyncioreactor.AsyncioSelectorReactor"



try:
    from GeeProxy.dev_config import *
except ImportError:
    print("use dev config file")
    pass
