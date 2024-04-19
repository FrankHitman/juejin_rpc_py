# coding: utf-8

import json
import time
import struct
import socket
import random
from kazoo.client import KazooClient

zk_root = "/demo"

G = {"servers": None}  # 全局变量，RemoteServer对象列表


class RemoteServer(object):  # 封装rpc套接字对象

    def __init__(self, addr):
        self.addr = addr
        self._socket = None

    @property
    def socket(self):  # 懒惰连接
        if not self._socket:
            self.connect()
        return self._socket

    def ping(self, twitter):
        return self.rpc("ping", twitter)

    def pi(self, n):
        return self.rpc("pi", n)

    def rpc(self, in_, params):
        sock = self.socket
        request = json.dumps({"in": in_, "params": params})
        length_prefix = struct.pack("I", len(request))
        sock.sendall(length_prefix)
        sock.sendall(request)
        length_prefix = sock.recv(4)
        length, = struct.unpack("I", length_prefix)
        body = sock.recv(length)
        response = json.loads(body)
        return response["out"], response["result"]

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host, port = self.addr.split(":")
        sock.connect((host, int(port)))
        self._socket = sock

    def reconnect(self):  # 重连
        self.close()
        self.connect()

    def close(self):
        if self._socket:
            self._socket.close()
            self._socket = None


def get_servers():
    zk = KazooClient(hosts="127.0.0.1:2181")
    zk.start()
    current_addrs = set()  # 当前活跃地址列表

    def watch_servers(*args):  # 闭包函数
        new_addrs = set()
        # 获取新的服务地址列表，并持续监听服务列表变动
        for child in zk.get_children(zk_root, watch=watch_servers):  # 获取子节点名称
            node = zk.get(zk_root + "/" + child)  # 获取子节点 value
            addr = json.loads(node[0])
            new_addrs.add("%s:%d" % (addr["host"], addr["port"]))
        # 新增的地址
        add_addrs = new_addrs - current_addrs
        # 删除的地址
        del_addrs = current_addrs - new_addrs
        del_servers = []
        # 先找出所有的待删除server对象
        for addr in del_addrs:
            for s in G["servers"]:
                if s.addr == addr:
                    del_servers.append(s)
                    break
        # 依次删除每个server
        for server in del_servers:
            G["servers"].remove(server)
            current_addrs.remove(server.addr)
        # 新增server
        for addr in add_addrs:
            G["servers"].append(RemoteServer(addr))
            current_addrs.add(addr)

    # 首次获取节点列表并持续监听服务列表变更
    for child in zk.get_children(zk_root, watch=watch_servers):
        node = zk.get(zk_root + "/" + child)
        addr = json.loads(node[0])
        current_addrs.add("%s:%d" % (addr["host"], addr["port"]))
    G["servers"] = [RemoteServer(s) for s in current_addrs]
    return G["servers"]


def random_server():  # 随机获取一个服务节点
    if G["servers"] is None:
        get_servers()  # 首次初始化服务列表
    if not G["servers"]:
        return
    return random.choice(G["servers"])


if __name__ == '__main__':
    for i in range(100):
        server = random_server()
        if not server:
            break  # 如果没有节点存活，就退出
        time.sleep(0.5)
        try:
            out, result = server.ping("ireader %d" % i)
            print server.addr, out, result
        except Exception, ex:
            server.close()  # 遇到错误，关闭连接
            print ex


# output 原作者的初始 client.py 代码，未删除重复
# [chapter16]# python client.py
# 127.0.0.1:8001 pong ireader 0
# 127.0.0.1:8001 pi_r 2.82842712475
# 127.0.0.1:8001 pong ireader 1
# 127.0.0.1:8001 pi_r 2.98142397
# 127.0.0.1:8001 pong ireader 2
# 127.0.0.1:8001 pi_r 3.0346151138
# 127.0.0.1:8001 pong ireader 3
# 127.0.0.1:8001 pi_r 3.0613974252
# 127.0.0.1:8001 pong ireader 4
# 127.0.0.1:8001 pi_r 3.07748592639
# 127.0.0.1:8001 pong ireader 5
# 127.0.0.1:8001 pi_r 3.08820908126
# 127.0.0.1:8001 pong ireader 6
# 127.0.0.1:8001 pi_r 3.09586379024
# 127.0.0.1:8001 pong ireader 7
# 127.0.0.1:8001 pi_r 3.10160090328
# 127.0.0.1:8001 pong ireader 8
# 127.0.0.1:8001 pi_r 3.10606017716
# 127.0.0.1:8001 pong ireader 9
# 127.0.0.1:8001 pi_r 3.10962545799
# 127.0.0.1:8001 pong ireader 10
# 127.0.0.1:8001 pi_r 3.11254093604
# 127.0.0.1:8001 pong ireader 11
# 127.0.0.1:8001 pi_r 3.11496933402
# 127.0.0.1:8001 pong ireader 12
# 127.0.0.1:8001 pi_r 3.11702325174
# 127.0.0.1:8001 pong ireader 13
# 127.0.0.1:8001 pi_r 3.11878307819
# 127.0.0.1:8001 pong ireader 14
# 127.0.0.1:8001 pi_r 3.12030773705
# 127.0.0.1:8001 pong ireader 15
# 127.0.0.1:8001 pi_r 3.12164140089
# 127.0.0.1:8001 pong ireader 16
# 127.0.0.1:8001 pi_r 3.12281783409
# 127.0.0.1:8001 pong ireader 17
# 127.0.0.1:8001 pi_r 3.1238632872
# 127.0.0.1:8001 pong ireader 18
# 127.0.0.1:8001 pi_r 3.12479847649
# 127.0.0.1:8001 pong ireader 19
# 127.0.0.1:8001 pi_r 3.12563996907
# 127.0.0.1:8001 pong ireader 20
# 127.0.0.1:8001 pi_r 3.12640117199
# 127.0.0.1:8001 pong ireader 21
# 127.0.0.1:8001 pi_r 3.12709305127
# 127.0.0.1:8001 pong ireader 22
# 127.0.0.1:8001 pi_r 3.12772466316
# 127.0.0.1:8001 pong ireader 23
# 127.0.0.1:8001 pi_r 3.12830355253
# 127.0.0.1:8001 pong ireader 24
# 127.0.0.1:8001 pi_r 3.12883605544
# 127.0.0.1:8001 pong ireader 25
# 127.0.0.1:8001 pi_r 3.1293275319
# 127.0.0.1:8001 pong ireader 26
# 127.0.0.1:8001 pi_r 3.12978254684
# 127.0.0.1:8001 pong ireader 27
# 127.0.0.1:8001 pi_r 3.13020501223
# 127.0.0.1:8001 pong ireader 28
# 127.0.0.1:8001 pi_r 3.1305982998
# 127.0.0.1:8001 pong ireader 29
# 127.0.0.1:8001 pi_r 3.13096533115
# 127.0.0.1:8001 pong ireader 30
# 127.0.0.1:8001 pi_r 3.13130865048
# 127.0.0.1:8001 pong ireader 31
# 127.0.0.1:8001 pi_r 3.13163048357
# 127.0.0.1:8001 pong ireader 32
# 127.0.0.1:8001 pi_r 3.13193278611
# 127.0.0.1:8001 pong ireader 33
# 127.0.0.1:8001 pi_r 3.13221728347
# 127.0.0.1:8001 pong ireader 34
# 127.0.0.1:8001 pi_r 3.13248550357
# 127.0.0.1:8001 pong ireader 35
# 127.0.0.1:8001 pi_r 3.13273880444
# 127.0.0.1:8001 pong ireader 36
# 127.0.0.1:8001 pi_r 3.13297839708
# 127.0.0.1:8001 pong ireader 37
# 127.0.0.1:8001 pi_r 3.13320536492
# 127.0.0.1:8001 pong ireader 38
# 127.0.0.1:8001 pi_r 3.13342068016
# 127.0.0.1:8001 pong ireader 39
# 127.0.0.1:8001 pi_r 3.13362521765
# 127.0.0.1:8001 pong ireader 40
# 127.0.0.1:8001 pi_r 3.13381976684
# 127.0.0.1:8001 pong ireader 41
# 127.0.0.1:8001 pi_r 3.13400504189
# 127.0.0.1:8001 pong ireader 42
# 127.0.0.1:8001 pi_r 3.1341816905
# 127.0.0.1:8001 pong ireader 43
# 127.0.0.1:8001 pi_r 3.13435030139
# 127.0.0.1:8001 pong ireader 44
# 127.0.0.1:8001 pi_r 3.13451141094
# 127.0.0.1:8001 pong ireader 45
# 127.0.0.1:8001 pi_r 3.13466550883
# 127.0.0.1:8001 pong ireader 46
# 127.0.0.1:8001 pi_r 3.13481304301
# 127.0.0.1:8001 pong ireader 47
# 127.0.0.1:8001 pi_r 3.13495442411
# 127.0.0.1:8001 pong ireader 48
# 127.0.0.1:8001 pi_r 3.13509002917
# 127.0.0.1:8001 pong ireader 49
# 127.0.0.1:8001 pi_r 3.13522020506
# 127.0.0.1:8001 pong ireader 50
# 127.0.0.1:8001 pi_r 3.13534527143
# 127.0.0.1:8001 pong ireader 51
# 127.0.0.1:8001 pi_r 3.1354655233
# 127.0.0.1:8001 pong ireader 52
# 127.0.0.1:8001 pi_r 3.13558123342
# 127.0.0.1:8001 pong ireader 53
# 127.0.0.1:8001 pi_r 3.13569265432
# 127.0.0.1:8001 pong ireader 54
# 127.0.0.1:8001 pi_r 3.13580002015
# 127.0.0.1:8001 pong ireader 55
# 127.0.0.1:8001 pi_r 3.13590354831
# 127.0.0.1:8001 pong ireader 56
# 127.0.0.1:8001 pi_r 3.13600344095
# 127.0.0.1:8001 pong ireader 57
# 127.0.0.1:8001 pi_r 3.13609988626
# 127.0.0.1:8001 pong ireader 58
# 127.0.0.1:8001 pi_r 3.13619305966
# 127.0.0.1:8001 pong ireader 59
# 127.0.0.1:8001 pi_r 3.13628312486
# 127.0.0.1:8001 pong ireader 60
# 127.0.0.1:8001 pi_r 3.13637023485
# 127.0.0.1:8001 pong ireader 61
# 127.0.0.1:8001 pi_r 3.13645453272
# 127.0.0.1:8001 pong ireader 62
# 127.0.0.1:8001 pi_r 3.13653615248
# 127.0.0.1:8001 pong ireader 63
# 127.0.0.1:8001 pi_r 3.13661521976
# 127.0.0.1:8001 pong ireader 64
# 127.0.0.1:8001 pi_r 3.13669185244
# 127.0.0.1:8001 pong ireader 65
# 127.0.0.1:8001 pi_r 3.13676616127
# 127.0.0.1:8001 pong ireader 66
# 127.0.0.1:8001 pi_r 3.13683825036
# 127.0.0.1:8001 pong ireader 67
# 127.0.0.1:8001 pi_r 3.13690821772
# 127.0.0.1:8001 pong ireader 68
# 127.0.0.1:8001 pi_r 3.13697615566
# 127.0.0.1:8001 pong ireader 69
# 127.0.0.1:8001 pi_r 3.1370421512
# 127.0.0.1:8001 pong ireader 70
# 127.0.0.1:8001 pi_r 3.13710628647
# 127.0.0.1:8001 pong ireader 71
# 127.0.0.1:8001 pi_r 3.13716863905
# 127.0.0.1:8001 pong ireader 72
# 127.0.0.1:8001 pi_r 3.13722928222
# 127.0.0.1:8001 pong ireader 73
# 127.0.0.1:8001 pi_r 3.13728828534
# 127.0.0.1:8001 pong ireader 74
# 127.0.0.1:8001 pi_r 3.13734571405
# 127.0.0.1:8001 pong ireader 75
# 127.0.0.1:8001 pi_r 3.13740163053
# 127.0.0.1:8001 pong ireader 76
# 127.0.0.1:8001 pi_r 3.13745609374
# 127.0.0.1:8001 pong ireader 77
# 127.0.0.1:8001 pi_r 3.13750915961
# 127.0.0.1:8001 pong ireader 78
# 127.0.0.1:8001 pi_r 3.13756088123
# 127.0.0.1:8001 pong ireader 79
# 127.0.0.1:8001 pi_r 3.13761130904
# 127.0.0.1:8001 pong ireader 80
# 127.0.0.1:8001 pi_r 3.13766049098
# 127.0.0.1:8001 pong ireader 81
# 127.0.0.1:8001 pi_r 3.13770847267
# 127.0.0.1:8001 pong ireader 82
# 127.0.0.1:8001 pi_r 3.1377552975
# 127.0.0.1:8001 pong ireader 83
# 127.0.0.1:8001 pi_r 3.13780100683
# 127.0.0.1:8001 pong ireader 84
# 127.0.0.1:8001 pi_r 3.13784564004
# 127.0.0.1:8001 pong ireader 85
# 127.0.0.1:8001 pi_r 3.13788923469
# 127.0.0.1:8001 pong ireader 86
# 127.0.0.1:8001 pi_r 3.13793182661
# 127.0.0.1:8001 pong ireader 87
# 127.0.0.1:8001 pi_r 3.13797345
# 127.0.0.1:8001 pong ireader 88
# 127.0.0.1:8002 pi_r 3.13801413754
# 127.0.0.1:8001 pong ireader 89
# 127.0.0.1:8002 pi_r 3.13805392042
# 127.0.0.1:8001 pong ireader 90
# 127.0.0.1:8002 pi_r 3.1380928285
# 127.0.0.1:8002 pong ireader 91
# 127.0.0.1:8002 pi_r 3.1381308903
# 127.0.0.1:8001 pong ireader 92
# 127.0.0.1:8002 pi_r 3.13816813315
# 127.0.0.1:8001 pong ireader 93
# 127.0.0.1:8002 pi_r 3.1382045832
# 127.0.0.1:8001 pong ireader 94
# 127.0.0.1:8002 pi_r 3.13824026548
# 127.0.0.1:8002 pong ireader 95
# 127.0.0.1:8002 pi_r 3.13827520401
# 127.0.0.1:8001 pong ireader 96
# 127.0.0.1:8001 pi_r 3.13830942181
# 127.0.0.1:8002 pong ireader 97
# 127.0.0.1:8001 pi_r 3.13834294093
# 127.0.0.1:8001 pong ireader 98
# 127.0.0.1:8002 pi_r 3.13837578257
# 127.0.0.1:8002 pong ireader 99
# 127.0.0.1:8002 pi_r 3.13840796707
# [chapter16]#

# 删除 client.py 中重复代码的 output
# 127.0.0.1:8001 pong ireader 0
# 127.0.0.1:8001 pong ireader 1
# 127.0.0.1:8002 pong ireader 2
# 127.0.0.1:8002 pong ireader 3
# 127.0.0.1:8001 pong ireader 4
# 127.0.0.1:8002 pong ireader 5
# 127.0.0.1:8001 pong ireader 6
# 127.0.0.1:8001 pong ireader 7
# 127.0.0.1:8001 pong ireader 8
# 127.0.0.1:8001 pong ireader 9
# 127.0.0.1:8002 pong ireader 10
# 127.0.0.1:8002 pong ireader 11
# 127.0.0.1:8002 pong ireader 12
# 127.0.0.1:8002 pong ireader 13
# 127.0.0.1:8002 pong ireader 14
# 127.0.0.1:8001 pong ireader 15
# 127.0.0.1:8001 pong ireader 16
# 127.0.0.1:8002 pong ireader 17
# 127.0.0.1:8001 pong ireader 18
# 127.0.0.1:8001 pong ireader 19
# 127.0.0.1:8002 pong ireader 20
# 127.0.0.1:8002 pong ireader 21
# 127.0.0.1:8001 pong ireader 22
# 127.0.0.1:8002 pong ireader 23
# 127.0.0.1:8002 pong ireader 24
# 127.0.0.1:8001 pong ireader 25
# 127.0.0.1:8002 pong ireader 26
# 127.0.0.1:8002 pong ireader 27
# 127.0.0.1:8002 pong ireader 28
# 127.0.0.1:8001 pong ireader 29
# 127.0.0.1:8001 pong ireader 30
# 127.0.0.1:8001 pong ireader 31
# 127.0.0.1:8001 pong ireader 32
# 127.0.0.1:8002 pong ireader 33
# 127.0.0.1:8002 pong ireader 34
# 127.0.0.1:8001 pong ireader 35
# 127.0.0.1:8001 pong ireader 36
# 127.0.0.1:8001 pong ireader 37
# 127.0.0.1:8001 pong ireader 38
# 127.0.0.1:8001 pong ireader 39
# 127.0.0.1:8002 pong ireader 40
# 127.0.0.1:8001 pong ireader 41
# 127.0.0.1:8002 pong ireader 42
# 127.0.0.1:8001 pong ireader 43
# 127.0.0.1:8001 pong ireader 44
# 127.0.0.1:8002 pong ireader 45
# 127.0.0.1:8002 pong ireader 46
# 127.0.0.1:8002 pong ireader 47
# 127.0.0.1:8001 pong ireader 48
# 127.0.0.1:8002 pong ireader 49
# 127.0.0.1:8002 pong ireader 50
# 127.0.0.1:8002 pong ireader 51
# 127.0.0.1:8002 pong ireader 52
# 127.0.0.1:8002 pong ireader 53
# 127.0.0.1:8001 pong ireader 54
# 127.0.0.1:8001 pong ireader 55
# 127.0.0.1:8001 pong ireader 56
# 127.0.0.1:8001 pong ireader 57
# 127.0.0.1:8002 pong ireader 58
# 127.0.0.1:8001 pong ireader 59
# 127.0.0.1:8002 pong ireader 60
# 127.0.0.1:8001 pong ireader 61
# 127.0.0.1:8002 pong ireader 62
# 127.0.0.1:8002 pong ireader 63
# 127.0.0.1:8002 pong ireader 64
# 127.0.0.1:8002 pong ireader 65
# 127.0.0.1:8002 pong ireader 66
# 127.0.0.1:8001 pong ireader 67
# 127.0.0.1:8001 pong ireader 68
# 127.0.0.1:8002 pong ireader 69
# 127.0.0.1:8001 pong ireader 70
# 127.0.0.1:8001 pong ireader 71
# 127.0.0.1:8002 pong ireader 72
# 127.0.0.1:8002 pong ireader 73
# 127.0.0.1:8001 pong ireader 74
# 127.0.0.1:8001 pong ireader 75
# 127.0.0.1:8001 pong ireader 76
# 127.0.0.1:8001 pong ireader 77
# 127.0.0.1:8001 pong ireader 78
# 127.0.0.1:8001 pong ireader 79
# 127.0.0.1:8002 pong ireader 80
# 127.0.0.1:8001 pong ireader 81
# 127.0.0.1:8001 pong ireader 82
# 127.0.0.1:8001 pong ireader 83
# 127.0.0.1:8001 pong ireader 84
# 127.0.0.1:8002 pong ireader 85
# 127.0.0.1:8001 pong ireader 86
# 127.0.0.1:8002 pong ireader 87
# 127.0.0.1:8002 pong ireader 88
# 127.0.0.1:8002 pong ireader 89
# 127.0.0.1:8002 pong ireader 90
# 127.0.0.1:8001 pong ireader 91
# 127.0.0.1:8001 pong ireader 92
# 127.0.0.1:8001 pong ireader 93
# 127.0.0.1:8001 pong ireader 94
# 127.0.0.1:8001 pong ireader 95
# 127.0.0.1:8002 pong ireader 96
# 127.0.0.1:8001 pong ireader 97
# 127.0.0.1:8001 pong ireader 98
# 127.0.0.1:8002 pong ireader 99