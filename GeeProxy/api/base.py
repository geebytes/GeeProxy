"""
@Author: qinzhonghe96@163.com
@Date: 2020-03-09 00:27:46
@LastEditors: qinzhonghe96@163.com
@LastEditTime: 2020-03-09 19:14:06
@Description:
"""
from tornado import web
import json


class BaseHandler(web.RequestHandler):
    def set_default_headers(self):
        # print("执行了set_default_headers()")
        # 设置get与post方式的默认响应体格式为json
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.set_status(status_code)
        if "exc_info" in kwargs:
            self.write(
                json.dumps({
                    'reason': 'Sever Error',
                    'status_code': 500
                }))
        else:
            if status_code == 404:
                self.write(
                    json.dumps({
                        'reason': 'resource not found',
                        'status_code': 404
                    }))
            elif status_code == 500:
                self.write(
                    json.dumps({
                        'reason': 'Sever Error',
                        'status_code': 500
                    }))
            elif status_code == 400:
                self.write(
                    json.dumps({
                        'reason': 'Missing Params',
                        'status_code': 400
                    }))
            else:
                self.write(
                    json.dumps({
                        'reason': 'Unknow Error',
                        'status_code': status_code
                    }))

    def response(self, data={}, status_code=200):
        res = {"resource": data, "status_code": status_code}
        self.write(json.dumps(res))
