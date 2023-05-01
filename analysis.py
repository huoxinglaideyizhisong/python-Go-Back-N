'''
Author: CSDN/bilibili 火星来的一只松
Date: 2023-04-30 23:01:18
LastEditors: Do not edit
LastEditTime: 2023-04-30 23:29:24
FilePath: \Reliable file transfer using Go-Back-N protocol\analysis.py
'''


import re
from my_config import config
'''分析日志文件'''
def analyze_send(filename):
    first_send=0
    retransmit=0
    time_consumed_regex=re.compile('Transmission over! Time consumed: ([0-9]*.[0-9])s')
    time_consumed=0
    with open(filename,'r') as f:
        for line in f:
            if config.FirstSend in line:
                first_send+=1 # 这次是第一次传
            elif config.Retransmit in line:
                retransmit+=1 # 这次是重传
            matcher=time_consumed_regex.match(line)
            if matcher:
                time_consumed=matcher.group(1)
    total_transmit=first_send+retransmit
    print(f"总共发送PDU次数：{total_transmit}次")
    print(f'其中第一次发送{first_send}次，重传{retransmit}次, 重传占比{(retransmit/total_transmit)*100:.2f}%')
    print(f'总耗时{time_consumed}s')
    
def analyze_recv(filename):
    correct=0
    data_error=0
    out_of_order=0
    # time_consumed_regex=re.compile('Reception over! Time consumed: ([0-9]*.[0-9])s')
    time_consumed=0
    with open(filename,'r') as f:
        for line in f:
            if config.AllRight in line:
                correct+=1 # 这次是第一次传
            elif config.DataError in line:
                data_error+=1 # 这次是重传
            elif config.OutOfOrder in line:
                out_of_order+=1
            # matcher=time_consumed_regex.match(line)
            # if matcher:
            #     time_consumed=matcher.group(1)
    total_receive=correct+data_error+out_of_order
    print(f"总共收到PDU次数：{total_receive}次")
    print(f'其中正确接收{correct}次，乱序帧{out_of_order}次，占比{(out_of_order/total_receive)*100:.2f}%，数据出错{data_error}次，占比{(data_error/total_receive)*100:.2f}%。')
    # print(f'总耗时{time_consumed}s')
    
if __name__=='__main__':
    log_filename='./data/127.0.0.2/send_log_{test.txt}.txt' # 在这里写入日志文件
    if 'send' in log_filename:
        analyze_send(log_filename)
    elif 'recv' in log_filename:
        analyze_recv(log_filename)
    