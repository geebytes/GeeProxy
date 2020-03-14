"""
@Author: qinzhonghe96@163.com
@Date: 2020-03-02 02:44:01
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-10 21:27:55
@Description: 常用工具
"""
import json
import requests
import traceback
from urllib.parse import urlparse
from GeeProxy.settings import WEB_AVAILABLE_PROXIES,\
    VAILDATORS, API_SERVER
from GeeProxy.validators.validators import ProxyValidator


def construct_proxy_url(scheme:str, ip:str, port:str)->str:
    """
    构造代理url

    :param scheme: 代理的协议 HTTP or HTTPS
    :param ip: ip地址
    :param port: 端口
    :return: 完整的代理地址
    """
    return '{}://{}:{}'.format(scheme, ip, port)


def get_domain(url: str) -> str:
    """
    获取url的域名

    :param url:目标URL
    :return: 站点域名
    """
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return domain


def get_web_key(url: str) -> str:
    """
    通过url获取对应的web key
   
    :param url:目标URL
    :return: web key
    """
    domian = get_domain(url)
    if domian:
        return domian.split(".")[1]


def get_web_index(url: str) -> str:
    """
    获取站点首页

    :param url:目标URL
    :return: 站点首页
    """
    parsed_uri = urlparse(url)
    index = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    return index


# def get_key(protocol, domain, prefix=None):
#     return "{}{}{}"


def get_proxy(usage: str):
    """
    通过WEB API接口获取代理

    :param usage: 目标站点，对应WEB_AVAILABLE_PROXIES的key
    :return: 可用代理或None
    """
    url = API_SERVER + "/proxy?usage={}".format(usage)
    res = requests.get(url, timeout=5)
    try:
        if res.status_code == 200:
            return res.json().get("resource").get("proxy")
        else:
            return None
    except Exception:
        return None


def del_proxy(proxy: str, web_key: str):
    """
    通过WEB API接口删除某个代理

    :param proxy: 待删除代理
    :param web_key: 目标站点,对应WEB_AVAILABLE_PROXIES的key
    :return:
    """

    url = API_SERVER + "/proxy?usage={}&proxy={}".format(web_key, proxy)
    requests.delete(url, timeout=5)


def update_proxy(proxy: str, web: str, delay: float):
    """
    通过WEB API更新代理延迟

    :param proxy: 待更新代理
    :param web: 目标站点
    :param delay: 请求延迟
    :return:
    """
    url = API_SERVER + "/proxy"

    data = {"web": web, "proxy": proxy, "delay": delay}
    requests.post(url,
                  data=json.dumps(data),
                  headers={
                      'Content-type': 'application/json',
                      'Accept': 'text/plain'
                  },
                  timeout=5
                  )


# def is_check_anonymous(dst_web: str) -> bool:
#     dst_domian = get_domain(dst_web)
#     api_domian = get_domain(ANONYMOUS_CHECK_API)
#     if dst_domian == api_domian:
#         return True
#     else:
#         return False


def get_cache_key(web_key: str) -> str:
    """
    获取代理的hash　key

    :param web_key: 目标站点,对应WEB_AVAILABLE_PROXIES的key
    :return: 代理的hash key
    """
    return WEB_AVAILABLE_PROXIES[web_key]


def get_vaildator_task(proxy: str) -> list:
    """
    获取校验代理可用性任务协程的列表

    :param proxy: 待校验代理
    :return: 校验代理任务列表
    """
    tasks = []
    keys = VAILDATORS.keys()
    for k, v in WEB_AVAILABLE_PROXIES.items():
        vaildator = ProxyValidator()
        # 开始校验
        if v not in keys:
            # 跳过 http/https
            continue
        task = vaildator.check_proxy(proxy=proxy, dst=VAILDATORS[v], web_key=k)
        tasks.append(task)
    return tasks


# def run_sync(task):
#     loop = asyncio.get_event_loop()
#     if loop.is_closed():
#         new_loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(new_loop)
#     loop = asyncio.get_event_loop()
#     result = loop.run_until_complete(task)
#     loop.close()
#     return result


def get_traceback():
    traceback.format_exc()


def check_api_server()-> bool:
    """
    检查WEB API服务的状态

    :return: 如果可用则返回True否则返回False
    """
    try:
        response = requests.get(API_SERVER, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception:
        return False