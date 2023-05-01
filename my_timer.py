'''
Author: CSDN/bilibili 火星来的一只松
Date: 2023-04-30 23:01:18
LastEditors: Do not edit
LastEditTime: 2023-04-30 23:30:00
FilePath: \Reliable file transfer using Go-Back-N protocol\my_timer.py
'''

'''计时器类'''
import time
from my_config import config

class MyTimer:
    def __init__(self, interval=config.Interval):
        self.interval=config.Interval
        self.record={} # 记录每个帧发送的时间，key=seq_num, value=发送的时间
        
    def set(self,seq_num):
        '''开启seq_num的计时器'''
        self.record[seq_num]=time.time()
        
    def timeout(self,seq_num)-> bool:
        if seq_num in self.record:
            return time.time()-self.record[seq_num]>self.interval
        else:
            return False
        