'''
Author: CSDN/bilibili 火星来的一只松
Date: 2023-04-30 23:01:18
LastEditors: Do not edit
LastEditTime: 2023-04-30 23:33:50
FilePath: \Reliable file transfer using Go-Back-N protocol\my_config.py
'''
'''config文件，记录配置参数'''

class config:
    '''记录所有配置参数的类'''
    UDPPort=44444                       # UDP端口号
    HeaderLength=24                     # 头部长度
    DataSize=2048                       # 数据段长度
    Nnumber=4                           # 使用多少个bit对帧序号编号
    PDUSize=HeaderLength+DataSize       # PDU长度
    ErrorRate=0.001                      # 包错误率
    LostRate=0.001                       # 包丢失率
    SWsize=2**Nnumber-1                 # 发送方窗口大小, 注意它必须<=2**Nnumber-1
    Interval=1                          # 间隔超时计时器
    EndianType='little'                 # 编码字节时用大端还是小段
    isSigned=False                      # 编码字节的时候，数字是否是有符号数
    ServerIP='127.0.0.1'                # 服务器的Ip, 因为其他ip连不上，建议都用127.0.0.x
    ExitSign='exit'                     # 退出的标志
    ReturnSign='return'                 # 返回上一步的标志
    TypeData=0                          # 数据帧的标志
    TypeAck=1                           # ack帧的标志
    TypeOver=2                          # 发送结束
    TypeLogin=3                         # 用户登入
    TypeLogout=4                        # 用户退出

    FirstSend='first send'              # 第一次发送帧
    Retransmit='retransmit'             # 重传帧
    OutOfOrder='OutOfOrder'             # 乱序帧
    DataError='DataError'               # 数据出错
    AllRight='correct'                  # 帧一切正确