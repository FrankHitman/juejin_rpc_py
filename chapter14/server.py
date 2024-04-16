# coding: utf
# sendmsg recvmsg python3.5+才可以支持

import os
import json
import struct
import socket


def handle_conn(conn, addr, handlers):
    print(addr, "comes")
    while True:
        # 简单起见，这里就没有使用循环读取了
        length_prefix = conn.recv(4)
        if not length_prefix:
            print(addr, "bye")
            conn.close()
            break  # 关闭连接，继续处理下一个连接
        length, = struct.unpack("I", length_prefix)
        body = conn.recv(length)
        request = json.loads(body)
        in_ = request['in']
        params = request['params']
        print(in_, params)
        handler = handlers[in_]
        handler(conn, params)


def loop_slave(pr, handlers):
    while True:
        bufsize = 1
        ancsize = socket.CMSG_LEN(struct.calcsize('i'))
        msg, ancdata, flags, addr = pr.recvmsg(bufsize, ancsize)
        cmsg_level, cmsg_type, cmsg_data = ancdata[0]
        fd = struct.unpack('i', cmsg_data)[0]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, fileno=fd)
        handle_conn(sock, sock.getpeername(), handlers)


def ping(conn, params):
    send_result(conn, "pong", params)


def send_result(conn, out, result):
    response = json.dumps({"out": out, "result": result}).encode('utf-8')
    length_prefix = struct.pack("I", len(response))  # unsigned int 正整数
    conn.sendall(length_prefix)
    conn.sendall(response)


# serv_sock 是接受客户端请求的 socket，
# pws 是用于父进程与子进程通讯的 Unix socket，这个 socket 里面存储着 serv_sock
def loop_master(serv_sock, pws):
    idx = 0
    while True:
        sock, addr = serv_sock.accept()

        # 父进程从写的Unix socket file descriptor 列表中选出一个，用来给相应的子进程分配客户端连接过来的 socket
        # 通过求余 % 的方式轮询列表，round robin
        pw = pws[idx % len(pws)]
        # 消息数据，whatever
        msg = [b'x']
        # 辅助数据，携带描述符
        ancdata = [(
            socket.SOL_SOCKET,
            socket.SCM_RIGHTS,
            struct.pack('i', sock.fileno()))]
        pw.sendmsg(msg, ancdata)
        sock.close()  # 关闭父进程的socket引用，因为底层是复制，而不是传递。
        idx += 1


def prefork(serv_sock, n):
    pws = []
    for i in range(n):
        # 开辟父子进程通信「管道」
        pr, pw = socket.socketpair()
        pid = os.fork()
        if pid < 0:  # fork error
            return pws
        if pid > 0:
            # 父进程
            pr.close()  # 父进程不用读
            pws.append(pw)
            continue
        if pid == 0:
            # 子进程
            serv_sock.close()  # 关闭引用
            pw.close()  # 子进程不用写
            return pr
    return pws


if __name__ == '__main__':
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_sock.bind(("localhost", 8080))
    serv_sock.listen(1)
    pws_or_pr = prefork(serv_sock, 10)
    if hasattr(pws_or_pr, '__len__'):  # 父进程返回的是列表，里面存储着和子进程通讯的 Unix 域 socket 文件描述符
        if pws_or_pr:
            loop_master(serv_sock, pws_or_pr)
        else:
            # fork 全部失败，没有子进程，Game Over
            serv_sock.close()
    else:  # 子进程返回的是一个和父进程通讯的 Unix socket 文件描述符 file descriptor
        handlers = {
            "ping": ping
        }
        loop_slave(pws_or_pr, handlers)

# output
# (.venv) Franks-Mac:chapter14 frank$ python server.py
# ('127.0.0.1', 64093) comes
# Traceback (most recent call last):
#   File "/Users/frank/play/playRPC/juejin_rpc_py/chapter14/server.py", line 105, in <module>
#     loop_slave(pws_or_pr, handlers)
#   File "/Users/frank/play/playRPC/juejin_rpc_py/chapter14/server.py", line 37, in loop_slave
#     handle_conn(sock, sock.getpeername(), handlers)
#   File "/Users/frank/play/playRPC/juejin_rpc_py/chapter14/server.py", line 21, in handle_conn
#     request = json.loads(body)
#               ^^^^^^^^^^^^^^^^
#   File "/Users/frank/.pyenv/versions/3.11.8/lib/python3.11/json/__init__.py", line 346, in loads
#     return _default_decoder.decode(s)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/frank/.pyenv/versions/3.11.8/lib/python3.11/json/decoder.py", line 337, in decode
#     obj, end = self.raw_decode(s, idx=_w(s, 0).end())
#                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/frank/.pyenv/versions/3.11.8/lib/python3.11/json/decoder.py", line 355, in raw_decode
#     raise JSONDecodeError("Expecting value", s, err.value) from None
# json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
# ('127.0.0.1', 64106) comes
# ('127.0.0.1', 64106) bye
# ('127.0.0.1', 64752) comes
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
# ('127.0.0.1', 64752) bye
# ('127.0.0.1', 64935) comes
# ping ireader 0
# ping ireader 1
# ping ireader 2
# ping ireader 3
# ('127.0.0.1', 64936) comes
# ping ireader 0
# ping ireader 4
# ping ireader 1
# ping ireader 5
# ping ireader 2
# ping ireader 6
# ping ireader 3
# ping ireader 7
# ping ireader 4
# ping ireader 8
# ping ireader 5
# ping ireader 9
# ping ireader 6
# ('127.0.0.1', 64935) bye
# ping ireader 7
# ping ireader 8
# ping ireader 9
# ('127.0.0.1', 64936) bye