'''
Author: CSDN/bilibili 火星来的一只松
Date: 2023-04-30 23:01:18
LastEditors: Do not edit
LastEditTime: 2023-04-30 23:29:49
FilePath: \Reliable file transfer using Go-Back-N protocol\my_PDU.py
'''
from my_config import config
import random
'''
此文件主要包括：
MyPDUHeader类，定义了header的结构
MyPDU类，将数据和header封装在一起
一些有用的函数，如decode_PDU的作用是解码PDU等
'''

class MyPDUHeader:
    def __init__(self,source_addr:tuple[str, int],dest_addr:tuple[str, int], 
                 header_length= config.HeaderLength, data_length=0, 
                 crc_num=0, pdu_type=config.TypeData, seq_num=0):
        '''
        定义了我的PDU数据帧结构。
        打算将PDU头部长度设定为config.HeaderLength个字节
        前三个是header_length, data_length, crc_num, 分别占2字节，共6字节。
        然后是sourceIp和sourcePort，destIp和destPort，Ip占4字节，port占2字节。共12字节。
        最后是type（指定是数据帧还是ack帧）,seq_num，type占2字节，seq_num占4字节
        如果还需要添加，在代码中修改即可，并且记得在config文件中修改相关参数。并且记得修改此文件中的编码和解码函数
        '''
        self.header_length=header_length
        self.data_legnth=data_length
        self.crc_num=crc_num
        self.source_addr=source_addr
        self.dest_addr=dest_addr
        self.seq_num=seq_num
        self.pdu_type=pdu_type
        
    def to_byte(self) -> bytes:
        '''将header打包成config.HeaderLength字节的byte流'''
        header_length=self.header_length.to_bytes(2, config.EndianType, signed=config.isSigned)
        data_length=self.data_legnth.to_bytes(2, config.EndianType, signed=config.isSigned) # 虽然现在还不知道，但是先转化为字节流，然后在PDU中改
        crc_num=self.crc_num.to_bytes(2, config.EndianType, signed=config.isSigned) # 虽然现在还不知道，但是先转化为字节流，然后在PDU中改
        source_ip=self.__ip2byte(self.source_addr[0])
        source_port=self.source_addr[1].to_bytes(2, config.EndianType, signed=config.isSigned)
        dest_ip=self.__ip2byte(self.dest_addr[0])
        dest_port=self.dest_addr[1].to_bytes(2, config.EndianType, signed=config.isSigned)
        PDUtype=self.pdu_type.to_bytes(2, byteorder= config.EndianType, signed= config.isSigned)
        seq_num=self.seq_num.to_bytes(4, byteorder= config.EndianType, signed= config.isSigned)
        return header_length+data_length+crc_num+source_ip+source_port+dest_ip+dest_port+PDUtype+seq_num  
        
    def __ip2byte(self, ip_address:str) ->bytes:
        '''将一个Dotted-Decimal Notation的ip地址转化为4字节的byte流'''
        four_nums=list(map(int, ip_address.split('.')))
        num1=four_nums[0].to_bytes(1, byteorder = config.EndianType, signed = config.isSigned)
        num2=four_nums[1].to_bytes(1, byteorder = config.EndianType, signed = config.isSigned)
        num3=four_nums[2].to_bytes(1, byteorder = config.EndianType, signed = config.isSigned)
        num4=four_nums[3].to_bytes(1, byteorder = config.EndianType, signed = config.isSigned)
        return num1+num2+num3+num4


class MyPDU:
    def __init__(self, header:MyPDUHeader):
        '''将数据封装成一个PDU，并且在头部添加header'''
        self.header=header  # 头部
        self.header_length=header.header_length # 头部长度
        self.data_length=header.data_legnth # 数据部分长度
        self.lost_rate=config.LostRate    # 丢包率
        self.error_rate=config.ErrorRate  # 错误率       

    def to_byte(self, data: bytes):
        '''将头部和data封装为比特流'''
        return self.header.to_byte()+data
    
    

'''一些有用的函数'''
def byte2ip(raw_bytes: bytes) ->str:
    '''将一个四字节的byte转换为点分十进制格式的ip地址'''
    # print(raw_bytes[0])
    # print(type(raw_bytes[0])) # int! 只获取一位，直接得到int!
    # print(raw_bytes)
    # print(type(raw_bytes))
    # 这样写反而出错了
    # num1=int.from_bytes(raw_bytes[0], byteorder= config.EndianType, signed=config.isSigned)
    # num2=int.from_bytes(raw_bytes[1], byteorder= config.EndianType, signed=config.isSigned)
    # num3=int.from_bytes(raw_bytes[2], byteorder= config.EndianType, signed=config.isSigned)
    # num4=int.from_bytes(raw_bytes[3], byteorder= config.EndianType, signed=config.isSigned)
    num1=raw_bytes[0]
    num2=raw_bytes[1]
    num3=raw_bytes[2]
    num4=raw_bytes[3]
    return f'{num1}.{num2}.{num3}.{num4}'
        

def decode_PDU(raw_bytes: bytes):
    '''根据定义的PDU格式，将raw_bytes解包成header和data'''
    header_length=int.from_bytes(raw_bytes[0:2], byteorder= config.EndianType, signed=config.isSigned)
    data_length=int.from_bytes(raw_bytes[2:4], byteorder= config.EndianType, signed=config.isSigned)
    crc_num=int.from_bytes(raw_bytes[4:6], byteorder= config.EndianType, signed=config.isSigned)
    source_ip=byte2ip(raw_bytes[6:10])
    source_port=int.from_bytes(raw_bytes[10:12], byteorder= config.EndianType, signed= config.isSigned)
    dest_ip=byte2ip(raw_bytes[12:16])
    dest_port=int.from_bytes(raw_bytes[16:18], byteorder= config.EndianType, signed= config.isSigned)
    pdu_type=int.from_bytes(raw_bytes[18:20], byteorder= config.EndianType, signed=config.isSigned)
    seq_num=int.from_bytes(raw_bytes[20:24], byteorder= config.EndianType, signed=config.isSigned)
    raw_data=raw_bytes[config.HeaderLength:]
    header=MyPDUHeader((source_ip, source_port), (dest_ip, dest_port), header_length, data_length, crc_num, pdu_type,seq_num)
    return header, raw_data

def damage(raw_bytes):
    '''根据error rate随机损坏PDU数据帧，为了方便实验，不损坏头部'''
    if random.random()<config.ErrorRate: # 损坏
        # 随机选取一些损坏的位置, 选取10%的位置破坏
        damaged_positions=random.sample(range(config.HeaderLength,config.HeaderLength+config.DataSize),
                    int(0.1*config.DataSize))
        damaged_pdu=bytearray(raw_bytes) # 由于bytes是不可变序列，所以需要转换成bytearray
        for position in damaged_positions:
            damaged_pdu[position]=random.randint(0,255)
        return bytes(damaged_pdu)
    else: # 不损坏，完好无损
        return raw_bytes
    
def is_lost():
    '''根据lost rate，返回帧是否丢失'''
    return random.random()<config.LostRate