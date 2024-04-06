# coding=utf-8
import socket
import thread
import time


def main():
    # 创建 socket 连接
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8000))

    # 发送 HTTP 请求
    request = "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    client_socket.sendall(request)

    # 接收响应
    response = client_socket.recv(1024)
    print "Received response:\n%s" % response

    # 关闭连接
    client_socket.close()
    time.sleep(2)

if __name__ == "__main__":
    for i in range(10):
        print 'this is child thread ', i
        thread.start_new_thread(main, ())
        time.sleep(0.5)
    time.sleep(20)

# output 在多个terminal 里面执行 python client2.py
# (.venv) Franks-Mac:chapter11 frank$ python client2.py
# this is child thread  0
# Received response:
# HTTP/1.1 200 OK
#
# Hello, World!
# this is child thread  1
# Received response:
# HTTP/1.1 200 OK
#
# Hello, World!
# this is child thread  2
# Received response:
# HTTP/1.1 200 OK
#
# Hello, World!
# this is child thread  3
# Received response:
# HTTP/1.1 200 OK
#
# Hello, World!
# this is child thread  4
# Received response:
# HTTP/1.1 200 OK
#
# Hello, World!
# this is child thread  5
# Received response:
# HTTP/1.1 200 OK
#
# Hello, World!
# this is child thread  6
# Received response:
# HTTP/1.1 200 OK
#
# Hello, World!
# this is child thread  7
# Received response:
# HTTP/1.1 200 OK
#
# Hello, World!
# this is child thread  8
# Received response:
# HTTP/1.1 200 OK
#
# Hello, World!
# this is child thread  9
# Received response:
# HTTP/1.1 200 OK
#
# Hello, World!

# refer to http://www.geminitalk.cn:8021/r?q=24510472364076824