# coding: utf8

import os
import sys
import math
import json
import errno
import struct
import signal
import socket
import asyncore
from cStringIO import StringIO
from kazoo.client import KazooClient


class RPCHandler(asyncore.dispatcher_with_send):

    def __init__(self, sock, addr):
        asyncore.dispatcher_with_send.__init__(self, sock=sock)
        self.addr = addr
        self.handlers = {
            "ping": self.ping,
            "pi": self.pi
        }
        self.rbuf = StringIO()

    def handle_connect(self):
        print self.addr, 'comes'

    def handle_close(self):
        print self.addr, 'bye'
        self.close()

    def handle_read(self):
        while True:
            content = self.recv(1024)
            if content:
                self.rbuf.write(content)
            if len(content) < 1024:
                break
        self.handle_rpc()

    def handle_rpc(self):
        while True:
            self.rbuf.seek(0)
            length_prefix = self.rbuf.read(4)
            if len(length_prefix) < 4:
                break
            length, = struct.unpack("I", length_prefix)
            body = self.rbuf.read(length)
            if len(body) < length:
                break
            request = json.loads(body)
            in_ = request['in']
            params = request['params']
            print os.getpid(), in_, params
            handler = self.handlers[in_]
            handler(params)
            left = self.rbuf.getvalue()[length + 4:]
            self.rbuf = StringIO()
            self.rbuf.write(left)
        self.rbuf.seek(0, 2)

    def ping(self, params):
        self.send_result("pong", params)

    def pi(self, n):
        s = 0.0
        for i in range(n+1):
            s += 1.0/(2*i+1)/(2*i+1)
        result = math.sqrt(8*s)
        self.send_result("pi_r", result)

    def send_result(self, out, result):
        response = {"out": out, "result": result}
        body = json.dumps(response)
        length_prefix = struct.pack("I", len(body))
        self.send(length_prefix)
        self.send(body)


class RPCServer(asyncore.dispatcher):

    zk_root = "/demo"
    zk_rpc = zk_root + "/rpc"

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.host = host
        self.port = port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(1)
        self.child_pids = []
        if self.prefork(10):  # 产生子进程
            self.register_zk()  # 注册服务
            self.register_parent_signal()  # 父进程善后处理
        else:
            self.register_child_signal()  # 子进程善后处理

    def prefork(self, n):
        for i in range(n):
            pid = os.fork()
            if pid < 0:  # fork error
                raise
            if pid > 0:  # parent process
                self.child_pids.append(pid)
                continue
            if pid == 0:
                return False  # child process
        return True

    def register_zk(self):
        self.zk = KazooClient(hosts='127.0.0.1:2181')
        self.zk.start()  # 启动客户端，尝试连接
        self.zk.ensure_path(self.zk_root)  # 创建根节点 # 确保根节点存在，如果没有会自动创建
        value = json.dumps({"host": self.host, "port": self.port})
        # 创建服务子节点 # 创建顺序临时节点，这就是服务列表中的一个子服务地址信息
        self.zk.create(self.zk_rpc, value, ephemeral=True, sequence=True)

    def exit_parent(self, sig, frame):
        self.zk.stop()  # 关闭zk客户端 # 关闭 zk 会话，关闭客户端，否则临时节点不会立即消失
        self.close()  # 关闭serversocket
        asyncore.close_all()  # 关闭所有clientsocket
        pids = []
        for pid in self.child_pids:
            print 'before kill'
            try:
                os.kill(pid, signal.SIGINT)  # 关闭子进程
                pids.append(pid)
            except OSError, ex:
                if ex.args[0] == errno.ECHILD:  # 目标子进程已经提前挂了
                    continue
                raise ex
            print 'after kill', pid
        for pid in pids:
            while True:
                try:
                    os.waitpid(pid, 0)  # 收割目标子进程
                    break
                except OSError, ex:
                    if ex.args[0] == errno.ECHILD:  # 子进程已经割过了
                        break
                    if ex.args[0] != errno.EINTR:
                        raise ex  # 被其它信号打断了，要重试
            print 'wait over', pid

    def reap_child(self, sig, frame):
        print 'before reap'
        while True:
            try:
                info = os.waitpid(-1, os.WNOHANG)  # 收割任意子进程
                break
            except OSError, ex:
                if ex.args[0] == errno.ECHILD:
                    return  # 没有子进程可以收割
                if ex.args[0] != errno.EINTR:
                    raise ex  # 被其它信号打断要重试
        pid = info[0]
        try:
            self.child_pids.remove(pid)
        except ValueError:
            pass
        print 'after reap', pid

    def register_parent_signal(self):
        signal.signal(signal.SIGINT, self.exit_parent)
        signal.signal(signal.SIGTERM, self.exit_parent)
        signal.signal(signal.SIGCHLD, self.reap_child)  # 监听子进程退出

    def exit_child(self, sig, frame):
        self.close()  # 关闭serversocket
        asyncore.close_all()  # 关闭所有clientsocket
        print 'all closed'

    def register_child_signal(self):
        signal.signal(signal.SIGINT, self.exit_child)
        signal.signal(signal.SIGTERM, self.exit_child)

    def handle_accept(self):
        pair = self.accept()  # 接收新连接
        if pair is not None:
            sock, addr = pair
            RPCHandler(sock, addr)


if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    RPCServer(host, port)
    asyncore.loop()  # 启动事件循环

# output 启动 server 1 在 8001 端口
# [chapter16]# python server.py 127.0.0.1 8001
# 4525 ping ireader 0
# 4525 pi 0
# 4525 ping ireader 1
# 4525 pi 1
# 4525 ping ireader 2
# 4525 pi 2
# 4525 ping ireader 3
# 4525 pi 3
# 4525 ping ireader 4
# 4525 pi 4
# 4525 ping ireader 5
# 4525 pi 5
# 4525 ping ireader 6
# 4525 pi 6
# 4525 ping ireader 7
# 4525 pi 7
# 4525 ping ireader 8
# 4525 pi 8
# 4525 ping ireader 9
# 4525 pi 9
# 4525 ping ireader 10
# 4525 pi 10
# 4525 ping ireader 11
# 4525 pi 11
# 4525 ping ireader 12
# 4525 pi 12
# 4525 ping ireader 13
# 4525 pi 13
# 4525 ping ireader 14
# 4525 pi 14
# 4525 ping ireader 15
# 4525 pi 15
# 4525 ping ireader 16
# 4525 pi 16
# 4525 ping ireader 17
# 4525 pi 17
# 4525 ping ireader 18
# 4525 pi 18
# 4525 ping ireader 19
# 4525 pi 19
# 4525 ping ireader 20
# 4525 pi 20
# 4525 ping ireader 21
# 4525 pi 21
# 4525 ping ireader 22
# 4525 pi 22
# 4525 ping ireader 23
# 4525 pi 23
# 4525 ping ireader 24
# 4525 pi 24
# 4525 ping ireader 25
# 4525 pi 25
# 4525 ping ireader 26
# 4525 pi 26
# 4525 ping ireader 27
# 4525 pi 27
# 4525 ping ireader 28
# 4525 pi 28
# 4525 ping ireader 29
# 4525 pi 29
# 4525 ping ireader 30
# 4525 pi 30
# 4525 ping ireader 31
# 4525 pi 31
# 4525 ping ireader 32
# 4525 pi 32
# 4525 ping ireader 33
# 4525 pi 33
# 4525 ping ireader 34
# 4525 pi 34
# 4525 ping ireader 35
# 4525 pi 35
# 4525 ping ireader 36
# 4525 pi 36
# 4525 ping ireader 37
# 4525 pi 37
# 4525 ping ireader 38
# 4525 pi 38
# 4525 ping ireader 39
# 4525 pi 39
# 4525 ping ireader 40
# 4525 pi 40
# 4525 ping ireader 41
# 4525 pi 41
# 4525 ping ireader 42
# 4525 pi 42
# 4525 ping ireader 43
# 4525 pi 43
# 4525 ping ireader 44
# 4525 pi 44
# 4525 ping ireader 45
# 4525 pi 45
# 4525 ping ireader 46
# 4525 pi 46
# 4525 ping ireader 47
# 4525 pi 47
# 4525 ping ireader 48
# 4525 pi 48
# 4525 ping ireader 49
# 4525 pi 49
# 4525 ping ireader 50
# 4525 pi 50
# 4525 ping ireader 51
# 4525 pi 51
# 4525 ping ireader 52
# 4525 pi 52
# 4525 ping ireader 53
# 4525 pi 53
# 4525 ping ireader 54
# 4525 pi 54
# 4525 ping ireader 55
# 4525 pi 55
# 4525 ping ireader 56
# 4525 pi 56
# 4525 ping ireader 57
# 4525 pi 57
# 4525 ping ireader 58
# 4525 pi 58
# 4525 ping ireader 59
# 4525 pi 59
# 4525 ping ireader 60
# 4525 pi 60
# 4525 ping ireader 61
# 4525 pi 61
# 4525 ping ireader 62
# 4525 pi 62
# 4525 ping ireader 63
# 4525 pi 63
# 4525 ping ireader 64
# 4525 pi 64
# 4525 ping ireader 65
# 4525 pi 65
# 4525 ping ireader 66
# 4525 pi 66
# 4525 ping ireader 67
# 4525 pi 67
# 4525 ping ireader 68
# 4525 pi 68
# 4525 ping ireader 69
# 4525 pi 69
# 4525 ping ireader 70
# 4525 pi 70
# 4525 ping ireader 71
# 4525 pi 71
# 4525 ping ireader 72
# 4525 pi 72
# 4525 ping ireader 73
# 4525 pi 73
# 4525 ping ireader 74
# 4525 pi 74
# 4525 ping ireader 75
# 4525 pi 75
# 4525 ping ireader 76
# 4525 pi 76
# 4525 ping ireader 77
# 4525 pi 77
# 4525 ping ireader 78
# 4525 pi 78
# 4525 ping ireader 79
# 4525 pi 79
# 4525 ping ireader 80
# 4525 pi 80
# 4525 ping ireader 81
# 4525 pi 81
# 4525 ping ireader 82
# 4525 pi 82
# 4525 ping ireader 83
# 4525 pi 83
# 4525 ping ireader 84
# 4525 pi 84
# 4525 ping ireader 85
# 4525 pi 85
# 4525 ping ireader 86
# 4525 pi 86
# 4525 ping ireader 87
# 4525 pi 87
# 4525 ping ireader 88
# 4525 ping ireader 89
# 4525 ping ireader 90
# 4525 ping ireader 92
# 4525 ping ireader 93
# 4525 ping ireader 94
# 4525 ping ireader 96
# 4525 pi 96
# 4525 pi 97
# 4525 ping ireader 98
# ('127.0.0.1', 59290) bye

# 在启动 client 之后几秒钟 启动另外一个服务器节点在 8002 端口加入集群。
# [chapter16]$ python server.py 127.0.0.1 8002
# 4791 pi 88
# 4791 pi 89
# 4791 pi 90
# 4791 ping ireader 91
# 4791 pi 91
# 4791 pi 92
# 4791 pi 93
# 4791 pi 94
# 4791 ping ireader 95
# 4791 pi 95
# 4791 ping ireader 97
# 4791 pi 98
# 4791 ping ireader 99
# 4791 pi 99
# ('127.0.0.1', 2948) bye

# 退出 server 优雅的收割 子进程
# ^Call closed
# all closed
# all closed
# all closed
# all closed
# all closed
# all closed
# all closed
# all closed
# all closed
# before kill
# after kill 4530
# before kill
# after kill 4531
# before kill
# after kill 4532
# before kill
# after kill 4533
# before kill
# after kill 4534
# before kill
# after kill 4535
# before kill
# after kill 4536
# before kill
# after kill 4537
# before kill
# after kill 4538
# before kill
# after kill 4539
# before reap
# after reap 4536
# before reap
# after reap 4537
# before reap
# after reap 0
# wait over 4530
# before reap
# after reap 4534
# before reap
# after reap 4539
# before reap
# after reap 4533
# before reap
# after reap 4538
# before reap
# after reap 0
# wait over 4531
# before reap
# after reap 0
# wait over 4532
# wait over 4533
# wait over 4534
# before reap
# wait over 4535
# wait over 4536
# wait over 4537
# wait over 4538
# wait over 4539
# [chapter16]#

# 删除 client.py 中重复代码的 output
# 18904 ping ireader 0
# 18904 ping ireader 1
# 18904 ping ireader 4
# 18904 ping ireader 6
# 18904 ping ireader 7
# 18904 ping ireader 8
# 18904 ping ireader 9
# 18904 ping ireader 15
# 18904 ping ireader 16
# 18904 ping ireader 18
# 18904 ping ireader 19
# 18904 ping ireader 22
# 18904 ping ireader 25
# 18904 ping ireader 29
# 18904 ping ireader 30
# 18904 ping ireader 31
# 18904 ping ireader 32
# 18904 ping ireader 35
# 18904 ping ireader 36
# 18904 ping ireader 37
# 18904 ping ireader 38
# 18904 ping ireader 39
# 18904 ping ireader 41
# 18904 ping ireader 43
# 18904 ping ireader 44
# 18904 ping ireader 48
# 18904 ping ireader 54
# 18904 ping ireader 55
# 18904 ping ireader 56
# 18904 ping ireader 57
# 18904 ping ireader 59
# 18904 ping ireader 61
# 18904 ping ireader 67
# 18904 ping ireader 68
# 18904 ping ireader 70
# 18904 ping ireader 71
# 18904 ping ireader 74
# 18904 ping ireader 75
# 18904 ping ireader 76
# 18904 ping ireader 77
# 18904 ping ireader 78
# 18904 ping ireader 79
# 18904 ping ireader 81
# 18904 ping ireader 82
# 18904 ping ireader 83
# 18904 ping ireader 84
# 18904 ping ireader 86
# 18904 ping ireader 91
# 18904 ping ireader 92
# 18904 ping ireader 93
# 18904 ping ireader 94
# 18904 ping ireader 95
# 18904 ping ireader 97
# 18904 ping ireader 98
# ('127.0.0.1', 59304) bye

# 启动的另外一个 server 的 output
# 18927 ping ireader 2
# 18927 ping ireader 3
# 18927 ping ireader 5
# 18927 ping ireader 10
# 18927 ping ireader 11
# 18927 ping ireader 12
# 18927 ping ireader 13
# 18927 ping ireader 14
# 18927 ping ireader 17
# 18927 ping ireader 20
# 18927 ping ireader 21
# 18927 ping ireader 23
# 18927 ping ireader 24
# 18927 ping ireader 26
# 18927 ping ireader 27
# 18927 ping ireader 28
# 18927 ping ireader 33
# 18927 ping ireader 34
# 18927 ping ireader 40
# 18927 ping ireader 42
# 18927 ping ireader 45
# 18927 ping ireader 46
# 18927 ping ireader 47
# 18927 ping ireader 49
# 18927 ping ireader 50
# 18927 ping ireader 51
# 18927 ping ireader 52
# 18927 ping ireader 53
# 18927 ping ireader 58
# 18927 ping ireader 60
# 18927 ping ireader 62
# 18927 ping ireader 63
# 18927 ping ireader 64
# 18927 ping ireader 65
# 18927 ping ireader 66
# 18927 ping ireader 69
# 18927 ping ireader 72
# 18927 ping ireader 73
# 18927 ping ireader 80
# 18927 ping ireader 85
# 18927 ping ireader 87
# 18927 ping ireader 88
# 18927 ping ireader 89
# 18927 ping ireader 90
# 18927 ping ireader 96
# 18927 ping ireader 99
# ('127.0.0.1', 2960) bye