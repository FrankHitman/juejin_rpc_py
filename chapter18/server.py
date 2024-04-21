# coding=utf-8
import math
import grpc
import time
from concurrent import futures

import pi_pb2
import pi_pb2_grpc
import ping_pb2
import ping_pb2_grpc

class PiCalculatorServicer(pi_pb2_grpc.PiCalculatorServicer):

    def Calc(self, request, ctx):
        if request.n <= 0:
            ctx.set_code(grpc.StatusCode.INVALID_ARGUMENT)  # 参数错误，响应头帧里使用 Status 和 Status-Message 两个 header
            ctx.set_details("request number should be positive")  # 错误具体说明
            return pi_pb2.PiResponse()  # 注意即使发生错误了，也需要返回一个正常的空对象。
        s = 0.0
        for i in range(request.n):
            s += 1.0/(2*i+1)/(2*i+1)
        # # test the benchmark of multi thread
        # time.sleep(0.01)
        return pi_pb2.PiResponse(value=math.sqrt(8*s))

class PingServicer(ping_pb2_grpc.PingServicer):
    def Ping(self, request, context):
        # 注意返回的是一个响应对象
        return ping_pb2.PingResponse(output='pong for ' + request.input)


def main():
    # 多线程服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # 实例化圆周率服务类
    servicer = PiCalculatorServicer()
    servicer2 = PingServicer()
    # 注册本地服务
    pi_pb2_grpc.add_PiCalculatorServicer_to_server(servicer, server)
    ping_pb2_grpc.add_PingServicer_to_server(servicer2, server)
    # 监听端口
    server.add_insecure_port('localhost:8080')
    # 开始接收请求进行服务
    server.start()
    # 使用 ctrl+c 可以退出服务
    try:
        time.sleep(1000)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    main()
