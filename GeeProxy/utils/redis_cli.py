'''
@Author: John
@Date: 2020-03-01 11:43:19
@LastEditors: John
@LastEditTime: 2020-03-09 00:06:00
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
from GeeProxy.settings import REDIS_CLUSTER, REDIS_NODES


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
    '''
        This is a redis singleton connect client class
    '''
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
                                             decode_responses=True)
                cls._pid = pid
            else:
                pool = ConnectionPool(*args, **kwargs)
                cls._instance = Redis(connection_pool=pool)
                cls._pid = pid
        return cls._instance

    # def watch(self, *name):
    #     self.execute_command("WATCH", *name)
#
# def unwatch(self):
#     self.execute_command("UNWATCH")
#
# def multi(self):
#     self.execute_command("MULTI")

# def pipeline(self, transaction=None, shard_hint=None):
#     """
#     Cluster impl:
#         Pipelines do not work in cluster mode the same way they do in normal mode.
#         Create a clone of this object so that simulating pipelines will work correctly.
#         Each command will be called directly when used and when calling execute() will only return the # result stack.
#     """
#     if shard_hint:
#         raise RedisClusterException(
#             "shard_hint is deprecated in cluster mode")
#
#     if transaction:
#         raise RedisClusterException(
#             "transaction is deprecated in cluster mode")
#
#     return GeeClusterPipeline(
#         connection_pool=self.connection_pool,
#         startup_nodes=self.connection_pool.nodes.startup_nodes,
#         result_callbacks=self.result_callbacks,
#         response_callbacks=self.response_callbacks,
#     )


def acquire_lock(client, lock_name, acquire_time=20, time_out=15):
    """获取一个分布式锁"""
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
    except Exception as e:
        client.expire(lock, time_out)


def release_lock(client, lock_name, identifier):
    """通用的锁释放函数"""
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


client = RedisSingleton(startup_nodes=REDIS_NODES,
                        skip_full_coverage_check=True,
                        decode_responses=True)
# pipeline = client.pipeline()
