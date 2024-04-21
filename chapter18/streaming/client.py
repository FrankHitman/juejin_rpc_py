# coding=utf-8
import grpc

import pi_pb2
import pi_pb2_grpc

# RPC 的输入参数是一个生成器
def generate_request():
    for i in range(1, 2):
        yield pi_pb2.PiRequest(n=i)


def main():
    channel = grpc.insecure_channel('localhost:8080')
    client = pi_pb2_grpc.PiCalculatorStub(channel)
    response_iterator = client.Calc(generate_request())
    # 输出是一个迭代器，这个跟服务器正好对应起来。
    for response in response_iterator:
        print "pi(%d) =" % response.n, response.value


if __name__ == '__main__':
    main()
