# coding=utf-8
import math
import grpc
import time
import random
from concurrent import futures

import pi_pb2
import pi_pb2_grpc


class PiCalculatorServicer(pi_pb2_grpc.PiCalculatorServicer):

    def Calc(self, request_iterator, ctx):
        # request 是一个迭代器参数，对应的是一个 stream 请求
        for request in request_iterator:
            # 同时为了体现输入输出不是一对一的效果，我们按 50% 的概率对请求予以响应。
            if random.randint(0, 1) == 1:
                continue
            s = 0.0
            for i in range(request.n):
                s += 1.0/(2*i+1)/(2*i+1)
            # 响应是一个生成器，一个响应对应对应一个请求
            # 输出消息增加了一个参数，这个参数 n 就是输入的参数 n。
            yield pi_pb2.PiResponse(n=i, value=math.sqrt(8*s))


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = PiCalculatorServicer()
    pi_pb2_grpc.add_PiCalculatorServicer_to_server(servicer, server)
    server.add_insecure_port('localhost:8080')
    server.start()
    try:
        time.sleep(1000)
    except KeyboardInterrupt:
        server.stop(0)  # 0 是 timeout 参数，用于关闭时候等待超时 shutdown_event.wait(timeout=grace)


if __name__ == '__main__':
    main()
