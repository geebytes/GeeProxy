"""
@Author: John
@Date: 2020-03-09 00:14:54
@LastEditors: John
@LastEditTime: 2020-03-10 10:52:22
@Description: web server api
"""

import json
import tornado
import tornado.ioloop
from GeeProxy.settings import API_SERVER_PORT
from GeeProxy.api.base import BaseHandler
from GeeProxy.client.client import AvailableProxy
from GeeProxy.utils.logger import api_logger


class IndexHandler(BaseHandler):
    """
    首页
    """
    def get(self):
        """
        获取首页内容

        :return: 返回json格式的api相关信息
        """
        self.response(data={"description": "GeeProxy Client Web API", "version": "0.0.1"})
        return


class ProxyHandler(BaseHandler):
    """
    提供代理查询、更新、删除接口

    """
    async def get(self):
        """
        获取代理

        :return:
        """

        # 目标站点的key
        usage = self.get_argument("usage", "")
        proxy_type = "https"
        proxy = AvailableProxy()
        if usage:
            proxy_type = usage
        try:
            result = proxy.available_proxy(proxy_type)
            if not result:
                self.write_error(404)
                return
            self.response(data={"proxy": result})
            return
        except Exception as e:
            api_logger.error(
                "Getting proxy from {} occurred an exception {}".format(
                    proxy_type, str(e)))
            self.write_error(500)

    async def delete(self):
        """

        :return:
        """

        # 目标站点的key
        usage = self.get_argument("usage", "")
        # 对应代理
        proxy = self.get_argument("proxy", "")
        if not usage or not proxy:
            self.write_error(400)
            return
        try:
            await AvailableProxy.delete_proxy(proxy, usage)
            self.response(data={})
            return
        except Exception as e:
            api_logger.error(
                "Delete proxy from {} occurred an exception {}".format(
                    usage, str(e)))
            self.write_error(500)

    async def post(self):
        """
        更新代理的延迟

        :return:
        """
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        # 目标站点的key
        usage = param.get("web", "")
        # 代理
        proxy = param.get("proxy", "")
        # 延迟
        delay = param.get("delay", "")
        if isinstance(delay, str):
            delay = float(delay)
        try:
            if not usage or not proxy or not delay:
                self.write_error(400)
            await AvailableProxy.update_proxy_delay(proxy, usage, delay)
        except Exception as e:
            self.write_error(500)
            api_logger.error(
                "Update proxy from {} occurred an exception {}".format(
                    usage, str(e)))


class ProxyPoolHandler(BaseHandler):
    """
    代理池处理

    """
    async def get(self):
        """
        获取指定站点的代理池

        :return:
        """
        # 目标站点的key
        usage = self.get_argument("usage", "")
        proxy_type = "https"
        try:
            if not usage:
                self.write_error(400)
                return
            proxy_type = usage
            proxy = AvailableProxy()
            proxies = proxy.available_proxy(proxy_type,True)
            if not proxies:
                self.write_error(404)
                return
            self.response(data={"pool": proxies, "size": len(proxies)})
        except Exception as e:
            self.write_error(500)
            api_logger.error("Getting proxy pool from {} occurred an exception {}".format(proxy_type, str(e)))

    async def delete(self, *args, **kwargs):
        #实现post逻辑
        pass


def make_app():
    return tornado.web.Application([
        (r"^/proxy", ProxyHandler),
        (r"^/pool", ProxyPoolHandler),
        (r"^/", IndexHandler),
    ])


def run_app():
    app = make_app()
    app.listen(API_SERVER_PORT)
    tornado.ioloop.IOLoop.current().start()