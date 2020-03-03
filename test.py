'''
@Author: John
@Date: 2020-03-01 22:38:01
@LastEditors: John
@LastEditTime: 2020-03-03 23:57:30
@Description: 
'''


import requests
import threading
# 
# proxies = {'https': "http://163.172.146.119:8811",
#            'http': "http://163.172.146.119:8811"}
# resp = requests.get("https://httpbin.org/ip", verify=False,
#                     timeout=5, proxies=proxies)
# print(resp.text)

from GeeProxy.utils.redis_cli import client
from GeeProxy.utils.tools import get_domain
import time
import random
import asyncio
from GeeProxy.validators.validators import ProxyValidator
from GeeProxy.settings import VAILDATORS, PROXY_KEY_PATTERN
from GeeProxy.validators.vaildate_pub import vaildate_pub
from GeeProxy.validators.validate_tasks import subscribe_validator_msg
# protocol = "http"
# number = client.zcard(protocol)
# if not number:
#     pass
# else:
#     index = random.randint(0, number - 1)
#     protocol = client.zrange(protocol, index, index)
#     print(index,protocol)

# print(get_domain("https://www.cnblogs.com/itlqs/p/6055365.html"))
# proxies = {'https': "https://49.76.12.110:9999",
#            'http': "http://59.110.154.102:8080"}
# requests.get("http://httpbin.org/ip", verify=False,
#              timeout=10, proxies=proxies)


class GeeproxyPipeline(object):
    '''
    代理可用性校验
    
    '''
    loop = asyncio.get_event_loop()

#    def process_item(self, item, spider):
#       future = asyncio.ensure_future(self.check_item(item["url"]))
#       self.loop.run_until_complete(future)  # 事件循环
#       result = future.result()
#       for k in result:
#           timestamp = int(round(time.time() * 1000))
#           client.zadd(k, {item["url"]: timestamp})
#       self.loop.close()
#       return item
#       # is_useful = self.vaildator.check_proxy(
#       #     proxy=item["url"], dst="{}://httpbin.org/ip".format(item["protocol"]))
#       # if is_useful:
#       #     timestamp = int(round(time.time() * 1000))
#       #     client.zadd(item["protocol"], {item["url"]:timestamp})
#       #     return item
#       # return item
#
async def check_item(proxy):
    result = []
    # coros = []
    # loop = asyncio.get_event_loop()
    tasks = []
    for k, v in VAILDATORS.items():
        print(k,v)
        vaildator = ProxyValidator()
        tasks.append(vaildator.check_proxy(proxy=proxy, dst=v,cache_key=k))
        # coros.append(vaildator.check_proxy(proxy=proxy, dst=v))
    result, _ = await asyncio.wait(tasks)
    # result = loop.run_until_complete(asyncio.gather(*coros))
    # loop.close()
    for r in result:
        print("check result{}".format(r.result()))
    return result


# async def check_proxy(proxy):
#     result = []
#     # coros = []
#     # loop = asyncio.get_event_loop()
#     tasks = []
#     for k, v in VAILDATORS.items():
#         print(k, v)
#         vaildator = ProxyValidator()
#         tasks.append(vaildator.check_proxy(proxy=proxy, dst=v))
#         # coros.append(vaildator.check_proxy(proxy=proxy, dst=v))
#     result, _ = await asyncio.wait(tasks)
#     for r in result:
#         print("check result %s" % r.result())
#     # result = loop.run_until_complete(asyncio.gather(*coros))
#     # loop.close()
#     return result

def thread1_test():
    print("thread 1 is running...")

def thread1():
    scheduler_logger.info("This node running as the master role")
    scheduler = BlockingScheduler()
    scheduler.add_job(thread1_test, 'interval',seconds=5)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    

def thread2():
    print("thread 2 is running...")

if __name__ == "__main__":
    # vaildate_pub()
    # subscribe_validator_msg()
    # client.hmset("httphash",{"aad":"bbc","cctv":"aadda","useful":0})
    # print(client.keys("http*"))
    # checklist = [("http://59.110.154.102:8080", "http://httpbin.org/ip"),
    #              ("http://221.1.205.74:8060", "http://httpbin.org/ip"),
    #              ("http://119.180.173.36:8060", "http://httpbin.org/ip"),
    #              ("http://211.147.226.4:8118", "http://httpbin.org/ip"),
    #              ("http://117.87.180.144:8118", "http://httpbin.org/ip")]
    # # check_item("http://59.110.154.102:8080")
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(check_item("http://123.154.164.37:8118"))
    # future = asyncio.ensure_future(check_item("http://59.110.154.102:8080"))
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(future)  # 事件循环
    # result = future.result()
    # for k in result:
    #     timestamp = int(round(time.time() * 1000))
    #     print(k)
    #     # client.zadd(k, {item["url"]: timestamp})
    # loop.close()
    # loop = asyncio.get_event_loop()
    # for i in range(0, 5):
    #     validator = ProxyValidator()
    #     loop.run_until_complete(validator.check_proxy(*checklist[i]))
    # loop.close()

