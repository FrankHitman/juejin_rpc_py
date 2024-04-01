# coding=utf-8
import os
import time

if __name__ == '__main__':
    pid = os.fork()
    if pid > 0:
        print('we are in parent process, the child process pid is ', pid)
        print 'parent process: I will sleep for 3 seconds'
        time.sleep(3)
        print 'parent process: I have slept for 3 seconds'
        os.waitpid(pid, 0)
        # print 'parent process: I will sleep for 5 seconds'
        # time.sleep(5)
        # print 'parent process: I have slept for 5 seconds'
    if pid == 0:
        print 'child process: we are in child process, child process pid is ', os.getpid()
        print 'child process: I will sleep for 1 second'
        time.sleep(1)
        print 'child process: I have slept for 1 second'
        print 'child process: I will sleep for 2 seconds for the second time'
        time.sleep(2)
        print 'child process: I have slept for 2 seconds for the second time'
        # 增加以下 sleep，让子进程 sleep 时长大于父进程
        print 'child process: I will sleep for 2 seconds for the third time'
        time.sleep(2)
        print 'child process: I have slept for 2 seconds for the third time'
    if pid < 0:
        print 'fork error'

# 如果父进程sleep 的时长大于等于子进程的 sleep 时长，父进程可以正常收割子进程。
# 可以看到多进程中，父进程的 I/O 并不会 block 子进程的执行。
# output
# (.venv) Franks-Mac:chapter10 frank$ python playFork.py
# we are in parent process
# parent process: I will sleep for 3 seconds
# child process: we are in child process
# child process: I will sleep for 1 second
# child process: I have slept for 1 second
# child process: I will sleep for 2 seconds for the second time
# child process: I have slept for 2 seconds for the second time
# parent process: I have slept for 3 seconds

# 如果子进程执行时长大于父进程，那么子进程就不会正常结束，terminal 中会一致等待子进程结束，直到按下回车键。
# output
# (.venv) Franks-Mac:chapter10 frank$ python playFork.py
# we are in parent process
# parent process: I will sleep for 3 seconds
# child process: we are in child process
# child process: I will sleep for 1 second
# child process: I have slept for 1 second
# child process: I will sleep for 2 seconds for the second time
# child process: I have slept for 2 seconds for the second time
# child process: I will sleep for 2 seconds for the third time
# parent process: I have slept for 3 seconds
# (.venv) Franks-Mac:chapter10 frank$ child process: I have slept for 2 seconds for the third time
#
# (.venv) Franks-Mac:chapter10 frank$

# 简单增加 os.waitpid(pid=pid, options=0) 此处 waitpid执行出错，是因为 os.waitpid(pid=pid, options=0)
# 不支持 key-value 形式的参数传递。
# output
# (.venv) Franks-Mac:chapter10 frank$ python playFork.py
# ('we are in parent process, the child process pid is ', 28011)
# parent process: I will sleep for 3 seconds
# child process: we are in child process, child process pid is  28011
# child process: I will sleep for 1 second
# child process: I have slept for 1 second
# child process: I will sleep for 2 seconds for the second time
# child process: I have slept for 2 seconds for the second time
# child process: I will sleep for 2 seconds for the third time
# parent process: I have slept for 3 seconds
# Traceback (most recent call last):
#   File "playFork.py", line 12, in <module>
#     os.waitpid(pid=pid, options=0)
# TypeError: waitpid() takes no keyword arguments
# (.venv) Franks-Mac:chapter10 frank$ child process: I have slept for 2 seconds for the third time
#
# (.venv) Franks-Mac:chapter10 frank$

# 简单增加 os.waitpid(pid, 0) 在父进程中会正常收割子进程，父进程会一直等待子进程执行完毕，即使父进程 sleep 提前结束了
# output
# (.venv) Franks-Mac:chapter10 frank$ python playFork.py
# ('we are in parent process, the child process pid is ', 28172)
# parent process: I will sleep for 3 seconds
# child process: we are in child process, child process pid is  28172
# child process: I will sleep for 1 second
# child process: I have slept for 1 second
# child process: I will sleep for 2 seconds for the second time
# child process: I have slept for 2 seconds for the second time
# child process: I will sleep for 2 seconds for the third time
# parent process: I have slept for 3 seconds
# child process: I have slept for 2 seconds for the third time
# (.venv) Franks-Mac:chapter10 frank$
