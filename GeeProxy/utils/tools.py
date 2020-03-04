'''
@Author: John
@Date: 2020-03-02 02:44:01
@LastEditors: John
@LastEditTime: 2020-03-04 17:23:57
@Description: 
'''
from urllib.parse import urlparse

def get_domain(url):
    '''
    获取url的域名
    '''
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return domain


def get_key(protocol,domain,prefix=None):
    return "{}{}{}"

def get_proxy(key):
    pass



