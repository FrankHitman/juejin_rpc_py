# coding=utf-8
import os
import signal
import socket
import time

# 设置 worker 进程数量
NUM_WORKERS = 3

# 创建 socket 监听
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 8000))
server_socket.listen(1)

# 创建子进程
def worker():
    while True:
        print 'worker ', str(os.getpid()), ' is going to handle the connection'
        conn, addr = server_socket.accept()
        handle_request(conn)
        conn.close()
        time.sleep(1)

def handle_request(conn):
    request = conn.recv(1024)
    print "Received request: %s" % request
    response = "HTTP/1.1 200 OK\r\n\r\nHello, World!"
    conn.sendall(response)
    print 'worker ', str(os.getpid()), ' has handled the incoming request'

def main():
    # 创建子进程
    for i in range(NUM_WORKERS):
        pid = os.fork()
        if pid == 0:
            # 子进程
            worker()
            os._exit(0)

    # 主进程监听 KeyboardInterrupt 事件
    def signal_handler(signal, frame):
        print("Received KeyboardInterrupt, shutting down gracefully...")
        # 收割子进程
        for i in range(NUM_WORKERS):
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid > 0:
                    print "Child process %d exited with status %d" % (pid, status)
            except OSError:
                pass
        os._exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # 主进程等待子进程退出
    while True:
        try:
            pid, status = os.waitpid(-1, 0)
            print "Child process %d exited with status %d" % (pid, status)
        except OSError:
            break

if __name__ == "__main__":
    main()

# output
# (.venv) Franks-Mac:chapter11 frank$ python prefork2.py
# worker  30442  is going to handle the connection
# worker  30443  is going to handle the connection
# worker  30444  is going to handle the connection
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30442  has handled the incoming request
# worker  30442  is going to handle the connection
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30443  has handled the incoming request
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30444  has handled the incoming request
# worker  30443  is going to handle the connection
# worker  30444  is going to handle the connection
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30442  has handled the incoming request
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30443  has handled the incoming request
# worker  30442  is going to handle the connection
# worker  30443  is going to handle the connection
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30444  has handled the incoming request
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30442  has handled the incoming request
# worker  30444  is going to handle the connection
# worker  30442  is going to handle the connection
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30443  has handled the incoming request
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30444  has handled the incoming request
# worker  30443  is going to handle the connection
# worker  30444  is going to handle the connection
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30442  has handled the incoming request
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30443  has handled the incoming request
# worker  30442  is going to handle the connection
# worker  30443  is going to handle the connection
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30444  has handled the incoming request
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30442  has handled the incoming request
# worker  30444  is going to handle the connection
# worker  30442  is going to handle the connection
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30443  has handled the incoming request
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30444  has handled the incoming request
# worker  30443  is going to handle the connection
# worker  30444  is going to handle the connection
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30442  has handled the incoming request
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30443  has handled the incoming request
# worker  30442  is going to handle the connection
# worker  30443  is going to handle the connection
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30444  has handled the incoming request
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30442  has handled the incoming request
# worker  30444  is going to handle the connection
# worker  30442  is going to handle the connection
# Received request: GET / HTTP/1.1
# Host: localhost
#
#
# worker  30443  has handled the incoming request
# worker  30443  is going to handle the connection
# ^CReceived KeyboardInterrupt, shutting down gracefully...
# Traceback (most recent call last):
# Traceback (most recent call last):
# Traceback (most recent call last):
#   File "prefork2.py", line 64, in <module>
#   File "prefork2.py", line 64, in <module>
#   File "prefork2.py", line 64, in <module>
#     main()
#   File "prefork2.py", line 37, in main
#     main()
#   File "prefork2.py", line 37, in main
#         worker()
# main()
#   File "prefork2.py", line 19, in worker
#   File "prefork2.py", line 37, in main
#     conn, addr = server_socket.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     worker()
#   File "prefork2.py", line 19, in worker
#     worker()
#       File "prefork2.py", line 19, in worker
# conn, addr = server_socket.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     conn, addr = server_socket.accept()
#     sock, addr = self._sock.accept()
#   File "/Users/frank/.pyenv/versions/2.7.18/lib/python2.7/socket.py", line 206, in accept
#     sock, addr = self._sock.accept()
# KeyboardInterrupt
# KeyboardInterrupt
# sock, addr = self._sock.accept()
# KeyboardInterrupt
# (.venv) Franks-Mac:chapter11 frank$

# 以上代码出自 ChatGPT，子进程设置为3，只在子进程中处理 socket。 自始至终子进程的 pid 没有变，说明子进程没有重新创建，资源没有浪费
# refer to http://www.geminitalk.cn:8021/r?q=24510474780451479 and
# http://www.geminitalk.cn:8021/r?q=24510489431979507
