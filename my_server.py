'''
Author: CSDN/bilibili 火星来的一只松
Date: 2023-04-30 23:01:18
LastEditors: Do not edit
LastEditTime: 2023-04-30 23:29:57
FilePath: \Reliable file transfer using Go-Back-N protocol\my_server.py
'''
import socket
import my_PDU
from my_config import config
'''服务器类的实现，它只是起一个转发作用'''
class MyServer:
    def __init__(self, ip, port):
        self.server_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.ip=ip
        self.port=port
        self.PDUSize=config.PDUSize
        self.IP_PORT=(ip, port)
        self.server_socket.bind(self.IP_PORT)
        # 读取用户ip
        self.client_ips=[]
        self.client_ips_path='./data/127.0.0.1/clients.txt'
        with open(self.client_ips_path,'r') as f:
            for line in f:
                self.client_ips.append(line.strip())
                
    def start(self):
        print('-------server has been successfully started!-------')
        while True:
            data, addr=self.server_socket.recvfrom(self.PDUSize)
            # 解码数据
            header, raw_data=my_PDU.decode_PDU(data)
            # 若源ip不在自己的用户ip表里（表示一个未注册的用户上线）：更新用户表
            source_ip=header.source_addr[0]
            if source_ip not in self.client_ips:
                self.client_ips.append(source_ip)
                with open(self.client_ips_path,'a+') as f:
                    f.write(f'{source_ip}\n')
            # 若源ip在自己的用户ip表里（用户已经注册）：
            if source_ip in self.client_ips:
                dest_ip=header.dest_addr[0]
                if dest_ip not in self.client_ips:
                    self.client_ips.append(dest_ip)
                    with open(self.client_ips_path,'a+') as f:
                        f.write(f'{dest_ip}\n')

                print(f'收到{source_ip}给{dest_ip}的信息')
                # 转发
                self.server_socket.sendto(data,header.dest_addr)
                
            # 若目的ip不在自己的用户ip表里：
            elif source_ip not in self.client_ips:
            # todo:增加这一块内容
                pass
        print('-------server has been successfully shut down!-------')
        self.server_socket.close()
        