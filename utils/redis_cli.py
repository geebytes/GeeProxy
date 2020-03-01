'''
@Author: John
@Date: 2020-03-01 11:43:19
@LastEditors: John
@LastEditTime: 2020-03-01 13:10:50
@Description: redis连接模块
'''
from rediscluster import RedisCluster
from rediscluster.connection import ClusterConnectionPool
from redis.client import Redis
from redis import ConnectionPool
from settings import REDIS_CLUSTER, REDIS_NODES

class RedisSingleton(ClusterConnectionPool, Redis):
    def __new__(cls,*args,**keywords):
        if not hasattr(cls,'_instance'):
            if REDIS_CLUSTER:
                pool = ClusterConnectionPool(*args, **keywords)
                cls._instance = RedisCluster(connection_pool=pool, decode_responses=True)
            else:
                pool = ConnectionPool(*args, **keywords)
                cls._instance = Redis(connection_pool=pool)
        return cls._instance

client = RedisSingleton(startup_nodes=REDIS_NODES,
                        skip_full_coverage_check=True)
    
    
    
