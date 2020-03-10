'''
@Author: John
@Date: 2020-03-02 02:44:01
@LastEditors: John
@LastEditTime: 2020-03-10 21:27:55
@Description: 常用工具
'''
import json
import asyncio
import requests
import traceback
from urllib.parse import urlparse
from GeeProxy.settings import ANONYMOUS_CHECK_API, WEB_AVAILABLE_PROXIES,\
     VAILDATORS, API_SERVER
from GeeProxy.validators.validators import ProxyValidator


def construct_proxy_url(scheme, ip, port):
    """construct proxy urls, so spiders can use them directly"""
    return '{}://{}:{}'.format(scheme, ip, port)


def get_domain(url: str) -> str:
    '''
    获取url的域名
    '''
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return domain


def get_web_index(url: str) -> str:
    """
    获取站点首页
    """
    parsed_uri = urlparse(url)
    index = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    return index


def get_key(protocol, domain, prefix=None):
    return "{}{}{}"


def get_proxy(usage: str):
    url = API_SERVER + "/proxy?usage={}".format(usage)
    res = requests.get(url, timeout=5)
    try:
        if res.status_code == 200:
            return res.json().get("resource").get("proxy")
        else:
            return None
    except Exception:
        print("response is{}".format(res.text))
        return None


def del_proxy(proxy: str, web_key: str):

    url = API_SERVER + "/proxy?usage={}&proxy={}".format(web_key, proxy)
    requests.delete(url, timeout=5)


def update_proxy(proxy: str, web: str, delay: float):

    url = API_SERVER + "/proxy"

    data = {"web": web, "proxy": proxy, "delay": delay}
    requests.post(url,
                  data=json.dumps(data),
                  headers={
                      'Content-type': 'application/json',
                      'Accept': 'text/plain'
                  },
                  timeout=5)


def is_check_anonymous(dst_web: str) -> bool:
    dst_domian = get_domain(dst_web)
    api_domian = get_domain(ANONYMOUS_CHECK_API)
    if dst_domian == api_domian:
        return True
    else:
        return False


def get_cache_key(web_key: str) -> str:
    return WEB_AVAILABLE_PROXIES[web_key]


def get_vaildator_task(proxy: str) -> list:
    tasks = []
    keys = VAILDATORS.keys()
    for k, v in WEB_AVAILABLE_PROXIES.items():
        vaildator = ProxyValidator()
        # 开始校验
        if v not in keys:
            continue
        task = vaildator.check_proxy(proxy=proxy, dst=VAILDATORS[v], web_key=k)
        tasks.append(task)
    return tasks


def run_sync(task):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(task)
    loop.close()
    return result

def get_traceback():
    traceback.format_exc()

def check_api_server():
    try:
        response = requests.get(API_SERVER,timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception:
        return False