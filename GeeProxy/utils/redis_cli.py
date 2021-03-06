'''
@Author: qinzhonghe96@163.com
@Date: 2020-03-01 11:43:19
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-10 20:03:21
@Description: This module provides redis connect pool sigleton client
'''
import os
import uuid
import time
from rediscluster.pipeline import ClusterPipeline
from rediscluster import RedisCluster
from rediscluster.connection import ClusterConnectionPool
from redis.client import Redis
from redis import ConnectionPool
from GeeProxy.settings import REDIS_CLUSTER, REDIS_MASTER_NODES, REDIS_PASSWORD


class GeeClusterPipeline(ClusterPipeline):
    def __init__(self, *args, **keywords):
        super(GeeClusterPipeline, self).__init__(*args, **keywords)

    def watch(self, *name):
        self.execute_command("WATCH", *name)

    def unwatch(self):
        self.execute_command("UNWATCH")

    def multi(self):
        self.execute_command("MULTI")


class RedisSingleton(RedisCluster, Redis):
    """
    redis 单例模式下的客户端
    """

    def __init__(self, *args, **keywords):
        if isinstance(self._instance, Redis):
            super(RedisSingleton, self).__init__(*args, **keywords)
        else:
            super(RedisSingleton, self).__init__(*args, **keywords)

    def __new__(cls, *args, **kwargs):
        pid = os.getpid()
        if not hasattr(cls, '_instance') or pid != cls._pid:
            print("PID is {} and father PID is {}".format(
                os.getpid(), os.getppid()))
            if hasattr(cls, "_pid"):
                print("Instance PID is {} and PID is {}".format(cls._pid, pid))
            if REDIS_CLUSTER:
                pool = ClusterConnectionPool(*args, **kwargs)
                cls._instance = RedisCluster(connection_pool=pool,
                                             decode_responses=True,
                                             password=REDIS_PASSWORD
                                             )
                cls._pid = pid
            else:
                pool = ConnectionPool(*args, **kwargs)
                cls._instance = Redis(connection_pool=pool, password=REDIS_PASSWORD)
                cls._pid = pid
        return cls._instance


def acquire_lock(client: RedisSingleton, lock_name: str, acquire_time=20, time_out=15):
    """
    获取一个分布式锁

    :param client: redis客户端
    :param lock_name: 分布式锁名称
    :param acquire_time: 等待锁的时间
    :param time_out: 锁的超时时间
    :return: 如果成功拿到锁就返回一个锁的标识，否则就返回False
    """

    identifier = str(uuid.uuid4())
    end = time.time() + acquire_time
    lock = lock_name
    try:
        while time.time() < end:
            if client.setnx(lock, identifier):
                # 给锁设置超时时间, 防止进程崩溃导致其他进程无法获取锁
                client.expire(lock, time_out)
                return identifier
            elif client.ttl(lock) == -1:
                client.expire(lock, time_out)
            time.sleep(0.001)
        return False
    except Exception:
        client.expire(lock, time_out)


def release_lock(client: RedisSingleton, lock_name: str, identifier: str)-> bool:
    """
    通用的锁释放函数

    :param client: redis客户端
    :param lock_name: 锁的名称
    :param identifier: 锁的标识
    :return: 如果成功释放锁就返回True,否则返回False
    """
    lock = lock_name
    pip = client.pipeline()
    while True:
        try:
            # client.watch(lock)
            lock_value = client.get(lock)
            if not lock_value:
                return True
            if lock_value == identifier:
                # pip.multi()
                pip.delete(lock)
                pip.execute()
                return True
            # client.unwatch()
            break
        except Exception:
            # client.unwatch()
            return False


client = RedisSingleton(startup_nodes=REDIS_MASTER_NODES,
                        skip_full_coverage_check=True,
                        decode_responses=True)
# pipeline = client.pipeline()
