'''
@Author: John
@Date: 2020-03-01 16:11:59
@LastEditors: John
@LastEditTime: 2020-03-04 18:02:29
@Description: 爬取规则
'''

CRAWL_RULES = [
    {
        "name": "xiladaili.com",
        "start_urls": ["http://www.xiladaili.com/https/%d/" % i for i in range(1, 20)] +
        ["http://www.xiladaili.com/gaoni/%d/" % i for i in range(1, 20)],
        "allowed_domains": ['www.xiladaili.com'],
        "table_xpath_expression": "//table[@class='fl-table']",
        "ip_xpath_expression": "//td[1]/text()",
        "port_xpath_expression": "",
        "protocol_xpath_expression": "//td[2]/text()",
        "next_page":"//li[@class='page-item'][last()]//@href",
        "max_page":30
    },
    {
        "name": "www.xicidaili.com",
        "start_urls": ["https://www.xicidaili.com/wn/%d/" % i for i in range(1, 20)],
        "allowed_domains": ['www.xicidaili.com'],
        "table_xpath_expression": "//table[@id='ip_list']",
        "ip_xpath_expression": "//td[2]/text()",
        "port_xpath_expression": "//td[3]/text()",
        "protocol_xpath_expression": "//td[6]/text()",
        "next_page":"//a[@rel='next'][last()]/@href",
        "max_page":20
    },
    {
        "name": "www.kuaidaili.com",
        "start_urls": ["https://www.kuaidaili.com/free/inha/%d/" % i for i in range(1, 20)],
        "allowed_domains": ['www.kuaidaili.com'],
        "table_xpath_expression": "//table[@class='table table-bordered table-striped']",
        "ip_xpath_expression": "//td[@data-title='IP']/text()",
        "port_xpath_expression": "//td[@data-title='PORT']/text()",
        "protocol_xpath_expression": "//td[@data-title='类型']/text()",
        "next_page":"//a[@rel='next'][last()]/@href",
        "max_page":20
    },
]
