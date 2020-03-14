"""
@Author: qinzhonghe96@163.com
@Date: 2020-03-09 16:48:20
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-10 03:45:46
@Description: 校验爬取到的代理数据项的可用性和匿名程度
"""

import time
import asyncio
import threading
from GeeProxy.utils.redis_cli import client
from GeeProxy.utils.logger import item_logger
from GeeProxy.validators.validators import ProxyValidator
from GeeProxy.client.client import AvailableProxy
from GeeProxy.utils.tools import get_vaildator_task
from GeeProxy.settings import ITEM_VAILDATE_SET


class ItemAvalibleVaildate:
    """

    批量校验数据项，先校验匿名程度，如果该过程发生请求超时等异常就标记为不可用，
    并跳过对特定站点校验的流程程，否则进入特定站点的校验流程

    """
    def __init__(self, items: list):
        self._items = items

    def append(self, item: dict):
        """
        添加数据项

        :param item: 数据项
        :return:
        """
        self._items.append(item)

    async def start_check(self):
        """
        开始校验
        :return:
        """
        if not self._items:
            return
        try:
            # 构建任务列表
            tasks = [asyncio.ensure_future(self._process_item(item))for item in self._items]
            # 异步处理
            await asyncio.gather(*tasks)
        except Exception as e:
            item_logger.error("While start check proxy anonymous"
                              " occurred an {} exception {}.".format(type(e), str(e)))

    async def _process_item(self, item: dict):
        """
        处理数据项
        :param item: 单个数据项
        :return:
        """
        if not item:
            return item
        # 先校验匿名程度
        result = await self._check_anonymous(item)
        # 是否可用
        if result.get("available", ""):
            # 检测代理对所有特定站点的可用性
            check_result = await self._check_item(item["url"])
            for r in check_result:
                # 如果代理可用就入库
                if r.available:
                    item_logger.info("Add proxy {} to cache.".format(
                        item["url"]))
                    r = await AvailableProxy.add_proxy(r, item)
                    if r:
                        # 入库成功就删除临时记录
                        client.delete(item["url"])

        return item

    async def _check_anonymous(self, item: dict)-> dict:
        """
        检测代理的匿名程度,在请求检测接口的过程中如果超时或发生其他异常就认为代理不可用

        :param item: 待检测的数据项
        :return: 返回检测后的数据项
        """
        if not item:
            return item
        item["available"] = 0
        try:
            # 先判断一下库中有没有这条代理如果有就跳过
            if not AvailableProxy.proxy_exist(item["url"]):
                item_logger.info("Checking proxy {} anonymous.".format(item["url"]))
                try:
                    result = await ProxyValidator.check_anonymous(item["url"])
                    item["anonymous"] = int(result)
                    item["available"] = 1
                except Exception as e:
                    item_logger.error(
                        "While check proxy {} anonymous occurred an {} exception {}."
                        .format(item["url"], type(e), str(e)))
                    # 发生异常就直接删除临时记录
                    client.delete(item["url"])
                    # 代理标记为不可用
                    item["available"] = 0
        except Exception as e:
            item_logger.error(
                "While check proxy {} anonymous occurred an {} exception {}.".
                format(item, type(e), str(e)))
        return item

    async def _check_item(self, proxy: str) -> list:
        """
        校验代理对可用性

        :param proxy: 待校验的代理
        :return: 结果列表
        """
        result = []
        # 拿到代理校验任务列表
        tasks = get_vaildator_task(proxy)
        # 批量处理
        done = await asyncio.gather(*tasks)
        for d in done:
            check_result = d
            if check_result.available:
                result.append(check_result)
        return result


def start_loop(loop):
    """
    设置当前线程的循环事件

    :param loop: 循环事件
    :return:
    """
    asyncio.set_event_loop(loop)
    loop.run_forever()


def item_vaildator_runner():
    """
    采用多线程+协程的方式执行校验任务提高任务执行效率,
    每批启用5个线程，每个线程启用5个携程,
    分批次按每批5*5的数据量从待校验集合中读取数据。
    """
    pipe = client.pipeline()
    while True:
        try:
            items_number = client.scard(ITEM_VAILDATE_SET)
            if items_number:
                # 在当前线程下创建时间循环，（未启用），在start_loop里面启动它
                new_loop = asyncio.new_event_loop()

                # 通过当前线程开启新的线程去启动事件循环
                thread = threading.Thread(target=new_loop.run_forever)

                # 获取当前循环事件
                loop = asyncio.get_event_loop()
                futs = []
                thread.start()
                # 启用5个线程
                try:
                    for k in range(0, 5):
                        # 读取数据
                        for i in range(0, 5):
                            pipe.spop(ITEM_VAILDATE_SET)
                        urls = list(pipe.execute())
                        items = []
                        for url in urls:
                            if url is not None:
                                pipe.hgetall(url)
                        items = list(pipe.execute())
                        item_vaildator = ItemAvalibleVaildate(items=items)
                        # 这几个是关键，代表在新线程中事件循环不断“游走”执行
                        futs.append(
                            asyncio.run_coroutine_threadsafe(
                                item_vaildator.start_check(), loop=new_loop))
                except Exception as e:
                    item_logger.error(
                        "While create check proxies anonymous tasks occurred an {} exception {}."
                        .format(type(e), str(e)))
                futs = [asyncio.wrap_future(f, loop=loop) for f in futs]
                loop.run_until_complete(asyncio.wait(futs))
                new_loop.call_soon_threadsafe(new_loop.stop)
                thread.join()
            time.sleep(1)
        except Exception as e:
            item_logger.error(
                "While check proxies anonymous occurred an {} exception {}.".
                format(type(e), str(e)))
