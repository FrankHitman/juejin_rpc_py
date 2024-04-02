# coding: utf8
# prefork.py

import os
import json
import struct
import socket
import thread


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
        thread.start_new_thread(handle_conn, (conn, addr, handlers))


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
# (.venv) Franks-Mac:chapter11 frank$ python prefork_multithread.py
# ('127.0.0.1', 64228) comes
# ping ireader 0
# ping ireader 1
# ping ireader 2
# ping ireader 3
# ping ireader 4
# ping ireader 5
# ping ireader 6
# ping ireader 7
# ('127.0.0.1', 64233) comes
# ping ireader 0
# ping ireader 8
# ping ireader 1
# ping ireader 9
# ping ireader 2
# ('127.0.0.1', 64228) bye
# ping ireader 3
# ping ireader 4
# ping ireader 5
# ping ireader 6
# ping ireader 7
# ping ireader 8
# ping ireader 9
# ('127.0.0.1', 64233) bye
# ^CTraceback (most recent call last):
# Traceback (most recent call last):
# Traceback (most recent call last):
# Traceback (most recent call last):
#   File "prefork_multithread.py", line 66, in <module>
#   File "prefork_multithread.py", line 66, in <module>
#   File "prefork_multithread.py", line 66, in <module>
#   File "prefork_multithread.py", line 66, in <module>
#     loop(sock, handlers)
#   File "prefork_multithread.py", line 31, in loop
#     loop(sock, handlers)
#   File "prefork_multithread.py", line 31, in loop
#     loop(sock, handlers)
#   File "prefork_multithread.py", line 31, in loop
#     loop(sock, handlers)
#     conn, addr = sock.accept()
#   File "prefork_multithread.py", line 31, in loop
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     conn, addr = sock.accept()
# Traceback (most recent call last):
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#   File "prefork_multithread.py", line 66, in <module>
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     loop(sock, handlers)
# Traceback (most recent call last):
#   File "prefork_multithread.py", line 31, in loop
#   File "prefork_multithread.py", line 66, in <module>
# Traceback (most recent call last):
#   File "prefork_multithread.py", line 66, in <module>
#     sock, addr = self._sock.accept()
#         conn, addr = sock.accept()
# sock, addr = self._sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     sock, addr = self._sock.accept()
#     loop(sock, handlers)
#   File "prefork_multithread.py", line 31, in loop
# Traceback (most recent call last):
#     KeyboardInterrupt  File "prefork_multithread.py", line 66, in <module>
#
# loop(sock, handlers)
# sock, addr = self._sock.accept()
#   File "prefork_multithread.py", line 31, in loop
# KeyboardInterruptKeyboardInterrupt
#
# KeyboardInterrupt
#     conn, addr = sock.accept()
#     loop(sock, handlers)
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#   File "prefork_multithread.py", line 31, in loop
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     sock, addr = self._sock.accept()
#     sock, addr = self._sock.accept()
# KeyboardInterrupt
# KeyboardInterrupt
# Traceback (most recent call last):
#   File "prefork_multithread.py", line 66, in <module>
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     sock, addr = self._sock.accept()
# KeyboardInterrupt
# Traceback (most recent call last):
#   File "prefork_multithread.py", line 66, in <module>
#         loop(sock, handlers)
# loop(sock, handlers)
#   File "prefork_multithread.py", line 31, in loop
#   File "prefork_multithread.py", line 31, in loop
#     conn, addr = sock.accept()
#       File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
# conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     sock, addr = self._sock.accept()
#     sock, addr = self._sock.accept()
# KeyboardInterrupt
# Traceback (most recent call last):
#   File "prefork_multithread.py", line 66, in <module>
# conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     loop(sock, handlers)
#   File "prefork_multithread.py", line 31, in loop
#     conn, addr = sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     sock, addr = self._sock.KeyboardInterrupt
# accept()
#     sock, addr = self._sock.accept()
# KeyboardInterruptKeyboardInterrupt
#
# (.venv) Franks-Mac:chapter11 frank$