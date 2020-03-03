'''
@Author: John
@Date: 2020-03-03 16:33:44
@LastEditors: John
@LastEditTime: 2020-03-03 18:27:57
@Description: 将zset 转为set
'''
from GeeProxy.utils.redis_cli import client
from GeeProxy.utils.tools import get_domain
def cover_task():
    zset_keys = client.keys("http:*")
    zset_keys = zset_keys + client.keys("https:*")
    # zset_keys = client.keys("proxy:*")
    pipe = client.pipeline()
    for key in zset_keys:
        numbers = client.zrange(key,0,-1)
        for number in numbers:
            pipe.sadd(key.split(":")[0], number)
            print("proxy:{}".format(key.split(":")[1]))
            pipe.sadd("proxy:{}".format(key.split(":")[1]), number)
    pipe.execute()
cover_task()
    
