# coding: utf8
# prefork.py

import os
import json
import struct
import socket


def handle_conn(conn, addr, handlers):
    print addr, "comes"
    while True:
        print 'process ', str(os.getpid()), ' is going to handle request'
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
        print 'process ', str(os.getpid()), ' has handled the request'


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
            print 'parent process pid number is ', str(os.getpid())
            continue
        if pid == 0:
            print 'child process pid number is ', str(os.getpid())
            break  # child process


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("localhost", 8080))
    sock.listen(1)
    prefork(2)  # 好戏在这里，开启了10个子进程
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

# output 添加了打印 pid 之后的日志
# (.venv) Franks-Mac:chapter11 frank$ python prefork.py
# parent process pid number is  30692
# parent process pid number is  30692
# child process pid number is  30693
# parent process pid number is  30692
# child process pid number is  30694
# parent process pid number is  30692
# child process pid number is  30695
# parent process pid number is  30692
# child process pid number is  30696
# parent process pid number is  30692
# child process pid number is  30697
# parent process pid number is  30692
# child process pid number is  30698
# parent process pid number is  30692
# child process pid number is  30699
# parent process pid number is  30692
# child process pid number is  30700
# parent process pid number is  30692
# child process pid number is  30701
# child process pid number is  30702
# ('127.0.0.1', 51225) comes
# process  30693  is going to handle request
# ping ireader 0
# process  30693  has handled the request
# process  30693  is going to handle request
# ping ireader 1
# process  30693  has handled the request
# process  30693  is going to handle request
# ping ireader 2
# process  30693  has handled the request
# process  30693  is going to handle request
# ping ireader 3
# process  30693  has handled the request
# process  30693  is going to handle request
# ping ireader 4
# process  30693  has handled the request
# process  30693  is going to handle request
# ping ireader 5
# process  30693  has handled the request
# process  30693  is going to handle request
# ping ireader 6
# process  30693  has handled the request
# process  30693  is going to handle request
# ping ireader 7
# process  30693  has handled the request
# process  30693  is going to handle request
# ping ireader 8
# process  30693  has handled the request
# process  30693  is going to handle request
# ping ireader 9
# process  30693  has handled the request
# process  30693  is going to handle request
# ('127.0.0.1', 51225) bye
# ('127.0.0.1', 51233) comes
# process  30694  is going to handle request
# ping ireader 0
# process  30694  has handled the request
# process  30694  is going to handle request
# ping ireader 1
# process  30694  has handled the request
# process  30694  is going to handle request
# ping ireader 2
# process  30694  has handled the request
# process  30694  is going to handle request
# ping ireader 3
# process  30694  has handled the request
# process  30694  is going to handle request
# ping ireader 4
# process  30694  has handled the request
# process  30694  is going to handle request
# ping ireader 5
# process  30694  has handled the request
# process  30694  is going to handle request
# ping ireader 6
# process  30694  has handled the request
# process  30694  is going to handle request
# ping ireader 7
# process  30694  has handled the request
# process  30694  is going to handle request
# ping ireader 8
# process  30694  has handled the request
# process  30694  is going to handle request
# ('127.0.0.1', 51234) comes
# process  30695  is going to handle request
# ping ireader 0
# process  30695  has handled the request
# process  30695  is going to handle request
# ping ireader 9
# process  30694  has handled the request
# process  30694  is going to handle request
# ping ireader 1
# process  30695  has handled the request
# process  30695  is going to handle request
# ('127.0.0.1', 51233) bye
# ping ireader 2
# process  30695  has handled the request
# process  30695  is going to handle request
# ping ireader 3
# process  30695  has handled the request
# process  30695  is going to handle request
# ('127.0.0.1', 51235) comes
# process  30696  is going to handle request
# ping ireader 0
# process  30696  has handled the request
# process  30696  is going to handle request
# ping ireader 4
# process  30695  has handled the request
# process  30695  is going to handle request
# ping ireader 1
# process  30696  has handled the request
# process  30696  is going to handle request
# ping ireader 5
# process  30695  has handled the request
# process  30695  is going to handle request
# ping ireader 2
# process  30696  has handled the request
# process  30696  is going to handle request
# ping ireader 6
# process  30695  has handled the request
# process  30695  is going to handle request
# ping ireader 3
# process  30696  has handled the request
# process  30696  is going to handle request
# ping ireader 7
# process  30695  has handled the request
# process  30695  is going to handle request
# ping ireader 4
# process  30696  has handled the request
# process  30696  is going to handle request
# ping ireader 8
# process  30695  has handled the request
# process  30695  is going to handle request
# ping ireader 5
# process  30696  has handled the request
# process  30696  is going to handle request
# ping ireader 9
# process  30695  has handled the request
# process  30695  is going to handle request
# ping ireader 6
# process  30696  has handled the request
# process  30696  is going to handle request
# ('127.0.0.1', 51234) bye
# ping ireader 7
# process  30696  has handled the request
# process  30696  is going to handle request
# ping ireader 8
# process  30696  has handled the request
# process  30696  is going to handle request
# ping ireader 9
# process  30696  has handled the request
# process  30696  is going to handle request
# ('127.0.0.1', 51235) bye

# 从上面的日志可以看出父进程没有参与处理客户端发来的请求，子进程创建太多，没有充分利用。把子进程从 10 个 改为 2 个试试

# output of prefork(10) -> prefork(2)
# (.venv) Franks-Mac:chapter11 frank$ python prefork.py
# parent process pid number is  30809
# parent process pid number is  30809
# child process pid number is  30810
# child process pid number is  30811
# ('127.0.0.1', 51284) comes
# process  30809  is going to handle request
# ping ireader 0
# process  30809  has handled the request
# process  30809  is going to handle request
# ping ireader 1
# process  30809  has handled the request
# process  30809  is going to handle request
# ping ireader 2
# process  30809  has handled the request
# process  30809  is going to handle request
# ('127.0.0.1', 51285) comes
# process  30810  is going to handle request
# ping ireader 0
# process  30810  has handled the request
# process  30810  is going to handle request
# ping ireader 3
# process  30809  has handled the request
# process  30809  is going to handle request
# ping ireader 1
# process  30810  has handled the request
# process  30810  is going to handle request
# ping ireader 4
# process  30809  has handled the request
# process  30809  is going to handle request
# ping ireader 2
# process  30810  has handled the request
# process  30810  is going to handle request
# ping ireader 5
# process  30809  has handled the request
# process  30809  is going to handle request
# ping ireader 3
# process  30810  has handled the request
# process  30810  is going to handle request
# ping ireader 6
# process  30809  has handled the request
# process  30809  is going to handle request
# ping ireader 4
# process  30810  has handled the request
# process  30810  is going to handle request
# ping ireader 7
# process  30809  has handled the request
# process  30809  is going to handle request
# ping ireader 5
# process  30810  has handled the request
# process  30810  is going to handle request
# ping ireader 8
# process  30809  has handled the request
# process  30809  is going to handle request
# ping ireader 6
# process  30810  has handled the request
# process  30810  is going to handle request
# ping ireader 9
# process  30809  has handled the request
# process  30809  is going to handle request
# ping ireader 7
# process  30810  has handled the request
# process  30810  is going to handle request
# ('127.0.0.1', 51284) bye
# ping ireader 8
# process  30810  has handled the request
# process  30810  is going to handle request
# ping ireader 9
# process  30810  has handled the request
# process  30810  is going to handle request
# ('127.0.0.1', 51285) bye
# 从上面可以看出 父进程 30809 确实参与到了处理 socket 的消息。