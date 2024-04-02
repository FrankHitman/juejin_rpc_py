# coding: utf8
# prefork.py

import os
import json
import struct
import socket


def handle_conn(conn, addr, handlers):
    print addr, "comes"
    while True:
        length_prefix = conn.recv(4)
        if not length_prefix:
            print addr, "bye"
            conn.close()
            break  # 关闭连接，继续处理下一个连接
        length, = struct.unpack("I", length_prefix)
        body = conn.recv(length)
        request = json.loads(body)
        in_ = request['in']
        params = request['params']
        print in_, params
        handler = handlers[in_]
        handler(conn, params)


def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()
        handle_conn(conn, addr, handlers)


def ping(conn, params):
    send_result(conn, "pong", params)


def send_result(conn, out, result):
    response = json.dumps({"out": out, "result": result})
    length_prefix = struct.pack("I", len(response))
    conn.sendall(length_prefix)
    conn.sendall(response)


def prefork(n):
    for i in range(n):
        pid = os.fork()
        if pid < 0:  # fork error
            return
        if pid > 0:  # parent process
            continue
        if pid == 0:
            break  # child process


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("localhost", 8080))
    sock.listen(1)
    prefork(10)  # 好戏在这里，开启了10个子进程
    handlers = {
        "ping": ping
    }
    loop(sock, handlers)

# output
# (.venv) Franks-Mac:chapter11 frank$ python prefork.py
# ('127.0.0.1', 63763) comes
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
# ('127.0.0.1', 63763) bye
# ('127.0.0.1', 63767) comes
# ping ireader 0
# ping ireader 1
# ping ireader 2
# ping ireader 3
# ping ireader 4
# ('127.0.0.1', 63768) comes
# ping ireader 0
# ping ireader 5
# ping ireader 1
# ping ireader 6
# ping ireader 2
# ping ireader 7
# ping ireader 3
# ping ireader 8
# ping ireader 4
# ping ireader 9
# ping ireader 5
# ('127.0.0.1', 63767) bye
# ping ireader 6
# ping ireader 7
# ping ireader 8
# ping ireader 9
# ('127.0.0.1', 63768) bye
# ^CTraceback (most recent call last):
#   File "prefork.py", line 65, in <module>
# Traceback (most recent call last):
#   File "prefork.py", line 65, in <module>
# Traceback (most recent call last):
#   File "prefork.py", line 65, in <module>
#     loop(sock, handlers)
#   File "prefork.py", line 30, in loop
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     loop(sock, handlers)
#   File "prefork.py", line 30, in loop
#         loop(sock, handlers)
# conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#   File "prefork.py", line 30, in loop
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
# Traceback (most recent call last):
#   File "prefork.py", line 65, in <module>
# Traceback (most recent call last):
#   File "prefork.py", line 65, in <module>
# Traceback (most recent call last):
#   File "prefork.py", line 65, in <module>
#     loop(sock, handlers)
#   File "prefork.py", line 30, in loop
# Traceback (most recent call last):
#   File "prefork.py", line 65, in <module>
# Traceback (most recent call last):
#     loop(sock, handlers)
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#   File "prefork.py", line 30, in loop
#     loop(sock, handlers)
#   File "prefork.py", line 30, in loop
#     loop(sock, handlers)
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#   File "prefork.py", line 30, in loop
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#   File "prefork.py", line 65, in <module>
# Traceback (most recent call last):
#   File "prefork.py", line 65, in <module>
# Traceback (most recent call last):
#   File "prefork.py", line 65, in <module>
#     Traceback (most recent call last):
# loop(sock, handlers)
#   File "prefork.py", line 65, in <module>
#     loop(sock, handlers)
#       File "prefork.py", line 30, in loop
# sock, addr = self._sock.accept()
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     sock, addr = self._sock.accept()
#   File "prefork.py", line 30, in loop
#     sock, addr = self._sock.accept()
# KeyboardInterrupt
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
# KeyboardInterrupt
#     sock, addr = self._sock.accept()
#     loop(sock, handlers)
# KeyboardInterrupt
#   File "prefork.py", line 30, in loop
#     sock, addr     = self._sock.accept()
#         loop(sock, handlers)
# sock, addr = self._sock.accept()
#   File "prefork.py", line 30, in loop
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
# KeyboardInterruptKeyboardInterrupt
#
#     sock, addr = self._sock.accept()
# sock, addr = self._sock.accept()
# KeyboardInterrupt
# KeyboardInterrupt
#     sock, addr = self._sock.accept()
# KeyboardInterrupt
#     KeyboardInterruptsock, addr = self._sock.accept()
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
# KeyboardInterrupt
#     sock, addr = self._sock.accept()
# KeyboardInterrupt
#
# (.venv) Franks-Mac:chapter11 frank$
# 从上面的 ctrl+c 强制退出的错误中可以看出，退出socket报错有11个，那么说明父进程也参与了监听。
