# coding: utf-8
# client.py

import json
import time
import struct
import socket


def rpc(sock, in_, params):
    response = json.dumps({"in": in_, "params": params})  # 请求消息体
    length_prefix = struct.pack("I", len(response))  # 请求长度前缀
    sock.sendall(length_prefix)
    sock.sendall(response)
    length_prefix = sock.recv(4)  # 响应长度前缀，为什么设置 buffer size 为4？
    length, = struct.unpack("I", length_prefix)
    body = sock.recv(length)  # 响应消息体
    response = json.loads(body)
    return response["out"], response["result"]  # 返回响应类型和结果


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 8080))
    for i in range(10):  # 连续发送10个rpc请求
        out, result = rpc(s, "ping", "ireader %d" % i)
        print out, result
        time.sleep(1)  # 休眠1s，便于观察
    s.close()  # 关闭连接

# output
# (.venv) Franks-Mac:chapter8 frank$ python client.py
# pong ireader 0
# pong ireader 1
# pong ireader 2
# pong ireader 3
# pong ireader 4
# pong ireader 5
# pong ireader 6
# pong ireader 7
# pong ireader 8
# pong ireader 9
# (.venv) Franks-Mac:chapter8 frank$ python client.py
# pong ireader 0
# pong ireader 1
# pong ireader 2
# pong ireader 3
# pong ireader 4
# pong ireader 5
# pong ireader 6
# pong ireader 7
# pong ireader 8
# pong ireader 9
# ^CTraceback (most recent call last):
#   File "blocking_single.py", line 52, in <module>
#     loop(sock, handlers)  # 进入服务循环
#   File "blocking_single.py", line 29, in loop
#     conn, addr = sock.accept()  # 接收连接
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     sock, addr = self._sock.accept()
# KeyboardInterrupt