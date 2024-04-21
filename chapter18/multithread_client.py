import grpc

import pi_pb2
import pi_pb2_grpc

from concurrent import futures


def pi(client, k):
    result = client.Calc(pi_pb2.PiRequest(n=k)).value
    # print "pi(%d) =" % k, result
    return result

def main():
    channel = grpc.insecure_channel('localhost:8080')
    client = pi_pb2_grpc.PiCalculatorStub(channel)
    pool = futures.ThreadPoolExecutor(max_workers=10)
    results = []
    for i in range(1, 1000):
        results.append((i, pool.submit(pi, client, i)))
    pool.shutdown()

if __name__ == '__main__':
    main()

# output
# pi(542) = 3.14100531124
# pi(544) = 3.14100747079pi(545) = 3.14100854462
#
# pi(546) = 3.14100961451
# pi(547) = 3.14101068049
# pi(548) = 3.14101174259
# pi(549) = 3.14101280081
# pi(550) = 3.14101385518

# pi(572) = 3.14103611862
# pi(573) = 3.14103708997
# pi(574) = 3.14103805794
# pi(576) = 3.14103998379pi(577) = 3.1410409417
#
# pi(575) = 3.14103902254
# pi(578) = 3.1410418963

# pi(667) = 3.14111539121
# pi(670) = 3.14111752837
# pi(674) = 3.14112034831
#  pi(665) = 3.14111395573
# pi(666) =pi(669) = 3.14111681811 3.14111467455
#
# pi(668) = 3.14111610573
# pi(671) = 3.14111823651
# pi(672) = 3.14111894254
# pi(673) = 3.14111964647