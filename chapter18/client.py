# coding=utf-8
import grpc

import pi_pb2
import pi_pb2_grpc
import ping_pb2
import ping_pb2_grpc

from grpc._cython.cygrpc import CompressionAlgorithm
from grpc._cython.cygrpc import CompressionLevel

# 客户端可以在 channel 的选项中指定压缩算法属性，在请求的头部会携带压缩算法的参数传递给服务器。
# 可惜的是目前只支持客户端压缩，Python 版本的 gRPC 服务器版本没有提供压缩选项。
chan_ops = [('grpc.default_compression_algorithm', CompressionAlgorithm.gzip),
            ('grpc.grpc.default_compression_level', CompressionLevel.high)]


def main():
    channel = grpc.insecure_channel('localhost:8080', chan_ops)
    client = pi_pb2_grpc.PiCalculatorStub(channel)
    client2 = ping_pb2_grpc.PingStub(channel)
    for i in range(1000):
        try:
            res = client.Calc(pi_pb2.PiRequest(n=i))
            print "pi(%d) =" % i, res.value
        except grpc.RpcError as e:
            print e.code(), e.details()  # 从异常对象中提取 code 和 details 两个字段就知道具体发生的错误原因了。

        # invoke ping
        try:
            resp = client2.Ping(ping_pb2.PingRequest(input=str(i)))
            print "ping(%d) = " % i, resp.output
        except grpc.RpcError as e:
            print e.code(), e.details()


if __name__ == '__main__':
    main()


# output
# (.venv) Franks-Mac:chapter18 frank$ python client.py
# StatusCode.INVALID_ARGUMENT request number should be positive
# ping(0) =  pong for 0
# pi(1) = 2.82842712475
# ping(1) =  pong for 1
# pi(2) = 2.98142397
# ping(2) =  pong for 2
# pi(3) = 3.0346151138
# ping(3) =  pong for 3
# pi(4) = 3.0613974252
# ping(4) =  pong for 4
# pi(5) = 3.07748592639
# ping(5) =  pong for 5
# pi(6) = 3.08820908126
# ping(6) =  pong for 6
# pi(7) = 3.09586379024
# ping(7) =  pong for 7
# pi(8) = 3.10160090328
# ping(8) =  pong for 8
# pi(9) = 3.10606017716
# ping(9) =  pong for 9
# (.venv) Franks-Mac:chapter18 frank$