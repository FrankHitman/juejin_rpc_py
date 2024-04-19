# coding=utf-8

import time
import signal


def ignore(sig, frame):  # 啥也不干，就忽略信号
    pass


def play_sigint():
    signal.signal(signal.SIGINT, ignore)
    while True:
        print "hello"
        time.sleep(1)


def handle_sigterm(signum, frame):
    print('Received SIGTSTP')


def play_sigtstp():
    signal.signal(signal.SIGTSTP, handle_sigterm)
    while True:
        print "hello"
        time.sleep(1)


if __name__ == '__main__':
    # play_sigint()
    play_sigtstp()

# output for play_sigint()
# (.venv) Franks-Mac:chapter16 frank$ python play_signal.py
# hello
# hello
# hello
# ^Chello
# ^Chello
# ^Chello
# ^Chello
# ^Chello
# hello
# hello
# hello
# ^Z
# [1]+  Stopped                 python play_signal.py
# 你试试狂按 ctrl+c，进程依旧打转，只是这 hello 输出的要比平时快一点，似乎不再受到 sleep 的影响。
# 为什么呢？因为 sleep 函数总是要被 SIGINT 信号打断的，不管你有没有设置信号处理函数，只不过因为有 while True 循环在保护着。

# output for play_sigtstp
# (.venv) Franks-Mac:chapter16 frank$ python play_signal.py
# hello
# hello
# hello
# hello
# ^ZReceived SIGTSTP
# hello
# ^ZReceived SIGTSTP
# hello
# ^ZReceived SIGTSTP
# hello
# ^ZReceived SIGTSTP
# hello
# ^ZReceived SIGTSTP
# hello
# ^ZReceived SIGTSTP
# hello
# hello
# hello
# hello
# hello
# ^CTraceback (most recent call last):
#   File "play_signal.py", line 31, in <module>
#     play_sigtstp()
#   File "play_signal.py", line 26, in play_sigtstp
#     time.sleep(1)
# KeyboardInterrupt
# (.venv) Franks-Mac:chapter16 frank$
# 狂按 ctrl+z 进程也是不退出，并且输出 hello 更快了。


