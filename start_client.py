'''
Author: CSDN/bilibili 火星来的一只松
Date: 2023-04-30 23:01:18
LastEditors: Do not edit
LastEditTime: 2023-04-30 23:30:07
FilePath: \Reliable file transfer using Go-Back-N protocol\start_client.py
'''
import socket
import sys
import os
import my_client
import my_client
from my_config import config
import threading
'''由此文件开启客户端'''
def input_ip_and_port(target: str):
    # 输入我的ip
    inp=input(f'请输入{target}的ip, 点分十进制格式:').strip()
    if inp==config.ExitSign:
        sys.exit()
    else:
        myip=inp
    # 输入我的port
    inp=input(f'请输入{target}的端口号:').strip()
    if inp==config.ExitSign:
        sys.exit()
    else:
        myport=int(inp)
    IP_PORT=(myip,myport)
    return IP_PORT

def sendfile(client: my_client.MyClient):
    source_folder=client.folder # 我的文件对应的文件夹，接收和发送的文件都在这个文件夹下面
    if not os.path.exists(source_folder):
        os.mkdir(source_folder)

    # 输入对方的ip和端口
    DEST_IP_PORT=input_ip_and_port('对方')
    filename=input('请输入您想发送给对方的文件，请注意，此文件必须在您的文件夹下！')
    files=os.listdir(source_folder)
    while filename not in files:
        print('您想发送的文件不存在，请输入正确的文件名！')
        filename=input('请输入您想发送给对方的文件，请注意，此文件必须在您的文件夹下！')
        if filename==config.ExitSign:
            client.close()
            sys.exit()
        continue
    send_thread=threading.Thread(target=client.send_data,args=(filename,DEST_IP_PORT))
    send_thread.start()
    send_thread.join()

def recvfile(client:my_client.MyClient):
    dest_folder=client.folder
    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)
    filename=input('请输入您想要保存的文件名：').strip()
    if filename==config.ExitSign:
        client.close()
        sys.exit()
    
    # 开启接收的线程
    receive_thread=threading.Thread(target=client.recv_data,args=(filename,))
    receive_thread.start()
    receive_thread.join()
    return
    
def main_client():
    print("请您的ip地址和端口号，以便发送文件。随时输入exit退出系统")
    MY_IP_PORT=input_ip_and_port('您')
    client=my_client.MyClient(MY_IP_PORT)
    while True:
        choice=input('您想发送还是接受文件？send/recv/exit:').strip()
        if choice=='recv':
            recvfile(client)
        elif choice=='send':
            sendfile(client)
        elif choice==config.ExitSign:
            client.close()
            sys.exit()
            
        
if __name__=='__main__':
    main_client()
        