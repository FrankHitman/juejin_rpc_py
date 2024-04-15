# Chapter 13 Notes
## PreForking
本章就是多了初始化 RPCServer 时候的 `self.prefork(10)  # 开辟10个子进程` 
由操作系统来调度 11 个进程来监听 socket 和处理请求。

例外，以下代码是用 Gemini 生成的父进程优雅退出方案，在退出时候收割子进程。
```python
import os


def prefork(self, n):
    child_pids = []
    for i in range(n):
        pid = os.fork()
        if pid < 0:  # fork error
            return
        if pid > 0:  # parent process
            child_pids.append(pid)  # Store child process ID
            continue
        if pid == 0:
            # Child process code goes here
            break  # child process

    # Parent process: Wait for all child processes to finish
    for pid in child_pids:
        os.waitpid(pid, 0)  # Wait for specific child process (pid)

    # Parent process continues after all children finish

```
相关实验代码参考 [Chapter 11](../chapter11/readme.md)
[prefork2](../chapter11/prefork2.py)


根据 [小册子评论](https://juejin.cn/book/6844733722936377351/section/6844733723141750791?enter_from=course_center&utm_source=course_center) 这种方式会产生惊群问题：

不会出现多个进程处理同一个请求的情况，但是这种设计会造成惊群的作用。
就是当一个连接到来之后，所有进程都会去争夺这个链接。
nginx 中的设计就是设置一把锁，当连接到来时多个进程先抢锁，抢到的执行这个处理，没抢到锁的就去做别的事。