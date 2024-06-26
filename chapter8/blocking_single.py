# coding: utf8
# blocking_single.py

import json
import struct
import socket


def handle_conn(conn, addr, handlers):
    print addr, "comes"
    while True:  # 循环读写
        length_prefix = conn.recv(4)  # 请求长度前缀，我有个疑问为什么设置 buffersize 为4？
        if not length_prefix:  # 连接关闭了
            print addr, "bye"
            conn.close()
            break  # 退出循环，处理下一个连接
        length, = struct.unpack("I", length_prefix)
        body = conn.recv(length)  # 请求消息体  
        request = json.loads(body)
        in_ = request['in']
        params = request['params']
        print in_, params
        handler = handlers[in_]  # 查找请求处理器
        handler(conn, params)  # 处理请求


def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()  # 接收连接
        handle_conn(conn, addr, handlers)  # 处理连接


def ping(conn, params):
    send_result(conn, "pong", params)  # 服务器端收到"ping"回复"pong"


def send_result(conn, out, result):
    response = json.dumps({"out": out, "result": result})  # 响应消息体
    length_prefix = struct.pack("I", len(response))  # 响应长度前缀
    conn.sendall(length_prefix)
    conn.sendall(response)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建一个TCP套接字
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 打开reuse addr选项
    sock.bind(("localhost", 8080))  # 绑定服务端对外端口
    sock.listen(1)  # 监听客户端连接
    handlers = {  # 注册请求处理器
        "ping": ping
    }
    loop(sock, handlers)  # 进入服务循环

# output
# (.venv) Franks-Mac:chapter8 frank$ python blocking_single.py
# ('127.0.0.1', 53589) comes  # 53589应该是客户端的端口号
# ping ireader 0
# ping ireader 1
# ping ireader 2
# ping ireader 3
# ping ireader 4
# ping ireader 5
# ping ireader 6
# ping ireader 7
# ping ireader 8
# ping ireader 9
# ('127.0.0.1', 53589) bye
# ('127.0.0.1', 53601) comes
# ping ireader 0
# ping ireader 1
# ping ireader 2
# ping ireader 3
# ping ireader 4
# ping ireader 5
# ping ireader 6
# ping ireader 7
# ping ireader 8
# ping ireader 9
# ('127.0.0.1', 53601) bye
