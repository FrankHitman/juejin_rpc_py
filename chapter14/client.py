# coding: utf-8
# client.py

import json
import time
import struct
import socket


def rpc(sock, in_, params):
    request = json.dumps({"in": in_, "params": params})  # 请求消息体
    length_prefix = struct.pack("I", len(request))  # 请求长度前缀
    sock.sendall(length_prefix)
    # py2 to py3 error: TypeError: a bytes-like object is required, not 'str'
    # https://stackoverflow.com/questions/33003498/typeerror-a-bytes-like-object-is-required-not-str
    sock.sendall(request.encode('utf-8'))
    length_prefix = sock.recv(4)  # 响应长度前缀
    length, = struct.unpack("I", length_prefix)
    body = sock.recv(length)  # 响应消息体
    response = json.loads(body)
    return response["out"], response["result"]  # 返回响应类型和结果


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 8080))
    for i in range(10):  # 连续发送10个rpc请求
        out, result = rpc(s, "ping", "ireader %d" % i)
        print(out, result)
        time.sleep(1)  # 休眠1s，便于观察
    s.close()  # 关闭连接

# output run multiple clients in multiple terminals
# (.venv) Franks-Mac:chapter14 frank$ python client.py
# Traceback (most recent call last):
#   File "/Users/frank/play/playRPC/juejin_rpc_py/chapter14/client.py", line 26, in <module>
#     out, result = rpc(s, "ping", "ireader %d" % i)
#                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/frank/play/playRPC/juejin_rpc_py/chapter14/client.py", line 14, in rpc
#     sock.sendall(request)
# TypeError: a bytes-like object is required, not 'str'
# (.venv) Franks-Mac:chapter14 frank$ python client.py
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
# (.venv) Franks-Mac:chapter14 frank$