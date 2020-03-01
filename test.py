'''
@Author: John
@Date: 2020-03-01 22:38:01
@LastEditors: John
@LastEditTime: 2020-03-01 23:33:52
@Description: 
'''


import requests

proxies = {'https': "http://163.172.146.119:8811",
           'http': "http://163.172.146.119:8811"}
resp = requests.get("https://httpbin.org/ip", verify=False,
                    timeout=5, proxies=proxies)
print(resp.text)
