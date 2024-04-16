# Chapter 14 Notes

## Nginx 并发模型
Nginx 的并发模型是一个多进程并发模型，
它的 Master 进程在绑定监听地址端口后 fork 出了多个 Slave 进程共同竞争处理这个服务端套接字接收到的很多客户端连接。

这多个 Slave 进程会共享同一个处于操作系统内核态的套接字队列，操作系统的网络模块在处理完三次握手后就会将套接字塞进这个队列。

这是一个生产者消费者模型，
- 生产者是操作系统的网络模块，
- 消费者是多个 Slave 进程，
- 队列中的对象是客户端套接字。

### 缺点
这种模型在负载均衡上有一个缺点，那就是套接字分配不均匀。

这是因为当多个进程竞争同一个套接字队列时，操作系统采用了 LIFO 的策略，最后一个来 accept 的进程最优先拿到 套接字。
越是繁忙的进程越是有更多的机会调用 accept，它能拿到的套接字也就越多。

## Node Cluster 并发模型
Master 进程会 fork 出多个子进程来处理客户端套接字。
但是不存在竞争问题，因为负责 accept 套接字的只能是 Master 进程，Slave 进程只负责处理客户端套接字请求。

### 问题
那就存在一个问题，Master 进程拿到的客户端套接字如何传递给 Slave 进程。

- sendmsg 会搭乘一个特殊的「管道」将 Master 进程的套接字描述符传递到 Slave 进程，
- Slave 进程通过 recvmsg 系统调用从这个「管道」中将描述符取出来。

这个「管道」比较特殊，它是 Unix 域套接字。
- 普通的套接字可以跨机器传输消息，
- Unix 域套接字只能在同一个机器的不同进程之间传递消息。

Unix 域套接字也分为有名套接字和无名套接字，
- 有名套接字会在文件系统指定一个路径名，无关进程之间都可以通过这个路径来访问 Unix 域套接字。
- 而无名套接字一般用于父子进程之间，父进程会通过 socketpair 调用来创建套接字，然后 fork 出来子进程，这样子进程也会同时持有这个套接字的引用。
后续父子进程就可以通过这个套接字互相通信。

注意这里的传递描述符，本质上不是传递，而是复制。
父进程的描述符并不会在 sendmsg 自动关闭自动消失，子进程收到的描述符和父进程的描述符也不是同一个整数值。
但是父子进程的描述符都会指向同一个内核套接字对象。

有了描述符的传递能力，父进程就可以将 accept 到的客户端套接字轮流传递给多个 Slave 进程，负载均衡的目标就可以顺利实现了。

sendmsg 和 recvmsg 方法到了 Python3.5 才内置进来

### 在 Pycharm 生成的 _socket.py 中 sendmsg 的代码说明如下所示：
```python
    def sendmsg(self, buffers, ancdata=None, flags=None, address=None): # real signature unknown; restored from __doc__
        """
        sendmsg(buffers[, ancdata[, flags[, address]]]) -> count
        
        Send normal and ancillary 辅助的 data to the socket, gathering the
        non-ancillary data from a series of buffers and concatenating 联系起来 it into
        a single message.  The buffers argument specifies the non-ancillary
        data as an iterable of bytes-like objects (e.g. bytes objects).
        The ancdata argument specifies the ancillary data (control messages)
        as an iterable of zero or more tuples (cmsg_level, cmsg_type,
        cmsg_data), where cmsg_level and cmsg_type are integers specifying the
        protocol level and protocol-specific type respectively, and cmsg_data
        is a bytes-like object holding the associated data.  The flags
        argument defaults to 0 and has the same meaning as for send().  If
        address is supplied and not None, it sets a destination address for
        the message.  The return value is the number of bytes of non-ancillary
        data sent.
        """
        pass
```
- 描述符是通过ancdata 参数传递的，它的意思是 「辅助数据」，
- 而 buffers 表示需要传递的消息内容，因为消息内容这里没有意义，所以这个字段可以任意填写，但是必须要有内容，如果没有内容，sendmsg 方法就是一个空调用。
```python
import socket, struct

def send_fds(sock, fd):
    return sock.sendmsg([b'x'], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, struct.pack("i", fd))])
    
# ancdata 参数是一个三元组的列表，
# 三元组的第一个参数表示网络协议栈级别 level，
# 第二个参数表示辅助数据的类型 type，
# 第三个参数才是携带的数据，
# level=SOL_SOCKET 表示传递的数据处于 TCP 协议层级，
# type=SCM_RIGHTS 就表示携带的数据是文件描述符。
# 我们传递的描述符 fd 是一个整数，需要使用 struct 包将它序列化成二进制。
```

### 在 Pycharm 生成的 _socket.py 中 recvmsg 的代码说明如下所示：
```python
    def recvmsg(self, bufsize, ancbufsize=None, flags=None): # real signature unknown; restored from __doc__
        """
        recvmsg(bufsize[, ancbufsize[, flags]]) -> (data, ancdata, msg_flags, address)
        
        Receive normal data (up to bufsize bytes) and ancillary data from the
        socket.  The ancbufsize argument sets the size in bytes of the
        internal buffer used to receive the ancillary data; it defaults to 0,
        meaning that no ancillary data will be received.  Appropriate 合适的 buffer
        sizes for ancillary data can be calculated using CMSG_SPACE() or
        CMSG_LEN(), and items which do not fit into the buffer might be
        truncated 截断 or discarded 丢弃.  The flags argument defaults to 0 and has the
        same meaning as for recv().
        
        The return value is a 4-tuple: (data, ancdata, msg_flags, address).
        The data item is a bytes object holding the non-ancillary data
        received.  The ancdata item is a list of zero or more tuples
        (cmsg_level, cmsg_type, cmsg_data) representing the ancillary data
        (control messages) received: cmsg_level and cmsg_type are integers
        specifying the protocol level and protocol-specific type respectively,
        and cmsg_data is a bytes object holding the associated data.  The
        msg_flags item is the bitwise 位操作符 OR of various flags indicating
        conditions on the received message; see your system documentation for
        details.  If the receiving socket is unconnected, address is the
        address of the sending socket, if available; otherwise, its value is
        unspecified.
        
        If recvmsg() raises an exception after the system call returns, it
        will first attempt to close any file descriptors received via the
        SCM_RIGHTS mechanism.
        """
        pass
```
recvmsg 返回 四个参数 (data, ancdata, msg_flags, address)
- data 存储收到的非附属的数据
- ancdata 是一个元组，存储附属数据，元组中每一个元素由三个元组组成：
  - cmsg_level, 协议级别
  - cmsg_type, 协议类型
  - cmsg_data 存储数据，字节类型
- msg_flags 位操作符 OR
- address 发送端 socket 地址，只有当 socket 断开的时候才有值。

- 本例中返回的 ancdata 数据，它里面包含了我们需要的文件描述符。
- 但是需要提供消息体的长度和辅助数据的长度参数。辅助数据的长度比较特殊，需要使用 CMSG_LEN 方法来计算，因为辅助数据里面还有我们看不到的额外的头部信息。
```python
import socket, struct

bufsize = 1  # 消息内容的长度
ancbufsize = socket.CMSG_LEN(struct.calcsize('i'))  # 辅助数据的长度
msg, ancdata, flags, addr = socket.recvmsg(bufsize, ancbufsize) # 收取消息
level, type, fd_bytes = ancdata[0] # 取第一个元祖，注意发送消息时我们传递的是一个三元组的列表
fd = struct.unpack('i', fd_bytes) # 反序列化
```

`struct.calcsize('i')` 为什么传 'i'？

检查 Pycharm 生成的 _struct.py 源码
```python
"""
The remaining chars indicate types of args and must match exactly;
these can be preceded by a decimal repeat count:
  x: pad byte (no data); c:char; b:signed byte; B:unsigned byte;
  ?: _Bool (requires C99; if not available, char is used instead)
  h:short; H:unsigned short; i:int; I:unsigned int;
  l:long; L:unsigned long; f:float; d:double; e:half-float.
Special cases (preceding decimal count indicates length):
  s:string (array of char); p: pascal string (with count byte).
Special cases (only available in native format):
  n:ssize_t; N:size_t;
  P:an integer type that is wide enough to hold a pointer.
Special case (not in native mode unless 'long long' in platform C):
  q:long long; Q:unsigned long long
Whitespace between formats is ignored.
"""


def calcsize(fmt):  # known case of _struct.calcsize
    """ Return size in bytes of the struct described by the format string. """
    return 0


def unpack(fmt, string):  # known case of _struct.unpack
    """
    Return a tuple containing values unpacked according to the format string.
    
    The buffer's size in bytes must be calcsize(format).
    
    See help(struct) for more on format strings.
    """
    pass


def pack(fmt, *args):  # known case of _struct.pack
    """
    pack(format, v1, v2, ...) -> bytes
    
    Return a bytes object containing the values v1, v2, ... packed according
    to the format string.  See help(struct) for more on format strings.
    """
    return b""
```
'i' 代表 integer 类型。前面有提到 "传递的描述符 fd 是一个整数，需要使用 struct 包将它序列化成二进制"
'I' 代表 unsigned integer


### socketpair 在 socket.py 文件中

```python

if hasattr(_socket, "socketpair"):

    def socketpair(family=None, type=SOCK_STREAM, proto=0):
        """socketpair([family[, type[, proto]]]) -> (socket object, socket object)

        Create a pair of socket objects from the sockets returned by the platform
        socketpair() function.
        The arguments are the same as for socket() except the default family is
        AF_UNIX if defined on the platform; otherwise, the default is AF_INET.
        """
        if family is None:
            try:
                family = AF_UNIX
            except NameError:
                family = AF_INET
        a, b = _socket.socketpair(family, type, proto)
        a = socket(family, type, proto, a.detach())
        b = socket(family, type, proto, b.detach())
        return a, b

else:

    # Origin: https://gist.github.com/4325783, by Geert Jansen.  Public domain.
    def socketpair(family=AF_INET, type=SOCK_STREAM, proto=0):
        if family == AF_INET:
            host = _LOCALHOST
        elif family == AF_INET6:
            host = _LOCALHOST_V6
        else:
            raise ValueError("Only AF_INET and AF_INET6 socket address families "
                             "are supported")
        if type != SOCK_STREAM:
            raise ValueError("Only SOCK_STREAM socket type is supported")
        if proto != 0:
            raise ValueError("Only protocol zero is supported")

        # We create a connected TCP socket. Note the trick with
        # setblocking(False) that prevents us from having to create a thread.
        lsock = socket(family, type, proto)
        try:
            lsock.bind((host, 0))
            lsock.listen()
            # On IPv6, ignore flow_info and scope_id
            addr, port = lsock.getsockname()[:2]
            csock = socket(family, type, proto)
            try:
                csock.setblocking(False)
                try:
                    csock.connect((addr, port))
                except (BlockingIOError, InterruptedError):
                    pass
                csock.setblocking(True)
                ssock, _ = lsock.accept()
            except:
                csock.close()
                raise
        finally:
            lsock.close()
        return (ssock, csock)
    __all__.append("socketpair")

socketpair.__doc__ = """socketpair([family[, type[, proto]]]) -> (socket object, socket object)
Create a pair of socket objects from the sockets returned by the platform
socketpair() function.
The arguments are the same as for socket() except the default family is AF_UNIX
if defined on the platform; otherwise, the default is AF_INET.
"""

```

父进程使用 fork 调用创建了多个子进程，然后又使用 socketpair 调用为每一个子进程都创建一个无名套接字用来传递描述符。
父进程使用 round robin 策略平均分配接收到的客户端套接字。
子进程接收到的是一个描述符整数，需要将描述符包装成套接字对象后方可读写


