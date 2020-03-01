'''
@Author: John
@Date: 2020-03-01 12:40:33
@LastEditors: John
@LastEditTime: 2020-03-01 13:11:25
@Description: 
'''

from utils.redis_cli import client

if __name__ == "__main__":
    print(id(client))
    client.set("aa", "bb")
    print(client.get("aa"))
    print(id(client))
    
