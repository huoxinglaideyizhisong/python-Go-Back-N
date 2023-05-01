'''
Author: CSDN/bilibili 火星来的一只松
Date: 2023-04-30 23:01:18
LastEditors: Do not edit
LastEditTime: 2023-04-30 23:30:10
FilePath: \Reliable file transfer using Go-Back-N protocol\start_server.py
'''
from my_server import MyServer
from my_config import config

'''由此文件开启服务器端'''
def main_server():
    server=MyServer(config.ServerIP, config.UDPPort)
    server.start()

        
if __name__=='__main__':
    main_server()