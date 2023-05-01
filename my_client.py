'''
Author: CSDN/bilibili 火星来的一只松
Date: 2023-04-30 23:01:18
LastEditors: Do not edit
LastEditTime: 2023-04-30 23:29:35
FilePath: \Reliable file transfer using Go-Back-N protocol\my_client.py
'''
import my_timer
import my_PDU
import my_crc
import socket
import _thread
import threading
import time
from my_config import config

'''客户端类的实现，应该实现的功能有：发送、接收数据，发送、接收ack帧。维护窗口和一系列变量'''
class MyClient:
    def __init__(self, ip_port:tuple[str, int], server_ip_port=(config.ServerIP, config.UDPPort)):
        '''封装了MyClient类，定义了client的一系列操作。最基本的两种操作是send_data和recv_data'''
        self.IP=ip_port[0]  # ip地址
        self.PORT=ip_port[1]    # 端口
        self.IP_PORT=ip_port    # ip和端口
        self.SERVER_IP_PORT=server_ip_port  # 服务器的ip和端口
        self.send_window_size=config.SWsize  # 发送窗口大小，接收窗口大小始终为1
        self.data_size=config.DataSize  # 一次从文件中读取多少字节数据
        self.pdu_size= config.PDUSize  # pdu大小
        self.max_seq_num=2**config.Nnumber-1 # 用n位给seq_num编号，最大的编号是2^n-1
        self.mod=2**config.Nnumber # seq_num增加时应该对它取模
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp socket
        self.sock.bind(self.IP_PORT)    # 绑定自己的地址
        self.folder=f'./data/{self.IP}/'    # 自己的文件夹
        # self.send_log_filename=self.folder+'send_log.txt'   # 发送日志文件名字
        # self.recv_log_filename=self.folder+'recv_log.txt'
        
    def __load_data(self, filename:str, receiver_addr: tuple[str: int]):
        '''从filename加载数据，根据reciver_addr封装好帧。注意filename必须在自己的文件夹下'''
        buffer=[]   # 保存所有需要发送的数据
        packet_index=0
        with open(self.folder+filename, 'rb') as file:
            while True:
                data=file.read(self.data_size)   # 这里使用rb模式读取，直接得到字节，注意前面文件打开格式必须是rb！
                if not data:    # 读到文件末尾，返回空,退出循环
                    break
                # 获取crc校验码
                checksum=my_crc.crc(data)
                # 创建header , 记得要模mod！
                header=my_PDU.MyPDUHeader(source_addr=self.IP_PORT, dest_addr=receiver_addr, data_length=len(data), 
                            crc_num=checksum, pdu_type=config.TypeData, seq_num=packet_index%self.mod)
                # 创建pdu
                pdu=my_PDU.MyPDU(header)
                pdu=pdu.to_byte(data)
                # 装入buffer
                buffer.append(pdu)
                packet_index+=1      
        return buffer
    
    def send_data(self, filename:str, receiver_addr: tuple[str: int]):
        '''
        发送方发送数据
        - `filename`: `str`, 需要发送的文件的名字，必须保证在自己的目录下。自己的目录是`./data/self.IP`
        - `receiver_addr`: `tuple[str: int]`, 发送方的地址, 元组第一个元素是点分十进制格式的ip地址，第二个元素是端口号
        '''
        # *此变量不受用多少位编码帧序号的限制
        self.ack_expected=0 # 由于另一个函数__send_ack也要使用这个变量，所以定义成自己的属性，不能定义为局部变量
        self.is_timeout=False   # 是否超时的标志
        # *此变量不受用多少位编码帧序号的限制，但是在发送帧序号时需要模2^n
        self.next_frame_to_send=0 # 下一次需要发送哪个帧, 是一个指针。由于python没有指针，只得用整数代替
        self.timer=my_timer.MyTimer()   # 计时器
        self.mutex = _thread.allocate_lock()    # 互斥锁，避免多线程同时修改同一变量
        log_filename=self.folder+f'send_log_{{{filename}}}.txt'
        with open(log_filename,'w') as log_file:
            self.buffer=self.__load_data(filename, receiver_addr) # 加载数据
            # 写入日志
            log_file.write('---------------------------------\n')
            log_file.write(f'send file {filename} to {str(receiver_addr)}, {len(self.buffer)} packets in total\n')
            start_time=time.time()
            t1=start_time
            # *开启接受ack的线程
            ack_thread=threading.Thread(target=self.__recv_ack)
            ack_thread.start()         
            # 只要还有可以发送的数据，就一直发送
            print('start transmission!')
            while self.ack_expected<len(self.buffer):
                # 由于发送中需要改变重要的变量，所以必须使用互斥锁
                self.mutex.acquire()
                # 可以发送的帧被限制在[self.ack_expected, self.ack_expected+ self.send_window_size) 范围内
                # 此外还不能超过buffer的帧数量
                if self.next_frame_to_send<self.ack_expected+self.send_window_size and self.next_frame_to_send<len(self.buffer):
                    self.timer.set(self.next_frame_to_send) # 开启计时器
                    cur_pdu=self.buffer[self.next_frame_to_send] # 本次要发送的帧
                    cur_pdu=my_PDU.damage(cur_pdu) # 根据error rate随机损坏帧
                    if not my_PDU.is_lost(): # 随机丢失包
                        self.sock.sendto(cur_pdu, self.SERVER_IP_PORT)
                        # print(f'send pdu {self.next_frame_to_send%self.mod}, ack_expected={self.ack_expected}')
                    # 写入日志
                    status=config.Retransmit if self.is_timeout else config.FirstSend
                    log_file.write(f'{time.ctime()}, {status} PDU={self.next_frame_to_send%self.mod} to {str(receiver_addr)}, ack received={self.ack_expected%self.mod}\n')
                    # 更新下一次应该发送的帧  
                    self.next_frame_to_send+=1 
                    self.is_timeout=False # 刚刚发送了帧，重置超时标志为False
                
                # 当计时器超时的时候，需要重传数据帧
                if self.timer.timeout(self.ack_expected):
                    self.is_timeout=True
                    self.next_frame_to_send=self.ack_expected
                    # print(f'pdu {self.ack_expected%self.mod} timeout')  
                # 弄一个简单的进度条，每隔0.5秒更新一下
                prop=self.ack_expected/len(self.buffer)
                t2=time.time()
                if t2-t1>0.5:
                    t1=t2
                    print(f"\rprocess: {int(prop*100):3d}%",end='')
                self.mutex.release()

            ack_thread.join() # 等待接收ack的线程结束
            # 发送结束帧，标志结束， 不然接收方不知道什么时候停止
            header=my_PDU.MyPDUHeader(source_addr=self.IP_PORT, 
                    dest_addr=receiver_addr, data_length=0, pdu_type=config.TypeOver)
            # 创建空pdu
            pdu=my_PDU.MyPDU(header)
            pdu=pdu.to_byte(b'')
            self.sock.sendto(pdu, self.SERVER_IP_PORT)
            end_time=time.time()
            time_consumed=end_time-start_time
            print(f"\rprocess: {100}%",end='')
            print(f'\nTransmission over! Time consumed: {time_consumed:.1f}s')    
            log_file.write(f'Transmission over! Time consumed: {time_consumed:.1f}s\n') 
            log_file.write('---------------------------------\n\n')
            self.ack_expected=0
            self.is_timeout=False
            self.next_frame_to_send=0
        
    def __recv_ack(self):
        '''发送方需要同时接收来自接收方的ack帧'''
        while self.ack_expected<len(self.buffer):
            raw_bytes, addr=self.sock.recvfrom(self.pdu_size)   # 注意，这里是读取pdu_size大小的数据！不是data_size！
            header, data=my_PDU.decode_PDU(raw_bytes)
                  
            # 由于send_data线程中可能需要用到一些重要的变量，所以这儿要用互斥锁！
            self.mutex.acquire() # 尝试得到锁
            # 对比收到的帧序号是不是期望的帧序号
            # *注意，接收到的帧序号是模了mod的！而self.ack_expected不受模的限制！
            not_acked_frame_nums=[i%self.mod for i in range(self.ack_expected, self.next_frame_to_send)]
            seq_acked=(header.seq_num-1+self.mod)%self.mod # 采用的是ack n，确认n之前的帧
            if seq_acked in not_acked_frame_nums: # 收到的序号在窗口里面
                # 记得要模mod！！
                # 由于需要讨论的情况太多，自己想不出来，就只好用while循环了
                while self.ack_expected % self.mod != seq_acked:
                    # 修改变量，采用的是cumulative ack，收到ack n，表示收到了n之前的帧，下一个期望收到的帧是n
                    self.ack_expected+=1 
                self.ack_expected+=1 # 移动到下一个未ack的位置
                # print(f'recv ack {header.seq_num}')
            else: # 迟到的ack帧，直接丢弃
                pass # 啥也不干
            self.mutex.release() # 释放锁
                         
    def recv_data(self, filename):
        '''接收对方发过来的data'''
        frame_expected=0 
        log_filename=self.folder+f'recv_log_{{{filename}}}.txt'
        with open(log_filename,'w') as log_file, open(self.folder+filename,'wb') as file:
            log_file.write('---------------------------------\n')
            log_file.write(f'receive {filename}\n')
            while True:
                raw_bytes, addr=self.sock.recvfrom(self.pdu_size)
                header, data=my_PDU.decode_PDU(raw_bytes)
                if header.pdu_type==config.TypeOver:
                    break # 收到结束帧，退出
                
                if header.seq_num!=frame_expected: # 乱序帧
                    log_file.write(f'{time.ctime()}, recv {config.OutOfOrder} PDU={header.seq_num} from {str(header.dest_addr)}, frame expected={frame_expected}\n')
                else:
                    checksum=my_crc.crc(data)
                    if checksum!=header.crc_num: # 数据校验不对
                        log_file.write(f'{time.ctime()}, recv {config.DataError} PDU={header.seq_num} from {str(header.dest_addr)}, frame expected={frame_expected}\n')
                    else: # 正确帧
                        file.write(data)
                        # print(f'recv pdu {header.seq_num}')
                        log_file.write(f'{time.ctime()}, recv {config.AllRight} PDU={header.seq_num} from {str(header.dest_addr)}, frame expected={frame_expected}\n')
                        frame_expected=(frame_expected+1)%self.mod # 采用累积确认，发送ack n，表示n之前的信息都收到了，下一个期望的帧是n
                        self.__send_ack(frame_expected, header.source_addr)
            print(f'Reception over!')    
            log_file.write(f'Reception over!\n')
            log_file.write('---------------------------------\n\n')
            
    def __send_ack(self, seq_num, source_ip_port):
        '''接收方在收到数据，检查无误后，需要返回ack帧'''
        header=my_PDU.MyPDUHeader(self.IP_PORT, source_ip_port, config.HeaderLength, 
            data_length=0, seq_num=seq_num, pdu_type=config.TypeAck)
        ack_bytes=header.to_byte()
        if not my_PDU.is_lost(): # 模拟ack帧丢失
            self.sock.sendto(ack_bytes, self.SERVER_IP_PORT)
            # print(f'send ack {seq_num}')
    
    def close(self):
        self.sock.close()