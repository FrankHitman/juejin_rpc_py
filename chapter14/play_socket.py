# coding=utf-8
import socket, struct


def send_fds(sock, fd):
    return sock.sendmsg([b'x'], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, struct.pack("i", fd))])

# ancdata 参数是一个三元组的列表，
# 三元组的第一个参数表示网络协议栈级别 level，
# 第二个参数表示辅助数据的类型 type，
# 第三个参数才是携带的数据，
# level=SOL_SOCKET 表示传递的数据处于 TCP 协议层级，
# type=SCM_RIGHTS 就表示携带的数据是文件描述符。
# 我们传递的描述符 fd 是一个整数，需要使用 struct 包将它序列化成二进制。

def recv_fds(sock):
    bufsize = 1  # 消息内容的长度
    ancbufsize = socket.CMSG_LEN(struct.calcsize('i'))  # 辅助数据的长度
    msg, ancdata, flags, addr = sock.recvmsg(bufsize, ancbufsize)  # 收取消息
    # msg, ancdata, flags, addr = socket.recvmsg(bufsize, ancbufsize) # 收取消息， socket 没有 recvmsg 方法。
    level, type, fd_bytes = ancdata[0]  # 取第一个元祖，注意发送消息时我们传递的是一个三元组的列表
    fd = struct.unpack('i', fd_bytes)  # 反序列化
