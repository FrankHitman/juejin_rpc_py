# Chapter 12 Notes
## 非阻塞 IO
操作系统提供的文件读写操作默认都是同步的，它必须等到数据就绪后才能返回，如果数据没有就绪，它就会阻塞当前的线程，其它的事什么都干不了

为了解决这个问题，操作系统给文件读写提供了非阻塞选项。当我们读写文件时，提供一个 O_NONBLOCK 选项，读写操作就不会阻塞。

内核套接字的 ReadBuffer 有多少字节，read 操作就返回多少字节。
内核套接字的 WriteBuffer 有多少剩余字节空间，write 操作就写多少字节。
我们通过读写的返回值就可以知道读写了多少数据。接下来线程就可以继续干别的事去了，稍后再继续进行读写。

```python
socket = socket.socket()
socket.setblocking(0)  # 开启非阻塞模式
socket.read()  # 有多少读多少
socket.write()  # 能写多少是多少
```

## 事件轮询
非阻塞 IO 看起来很有用，但是有个问题，我们该如何知道某个套接字可读可写呢？

如果我们反复去使用 read 和 write 去轮询 IO，这似乎挺费劲的，
假设一个套接字长期闲置没有消息到来，结果还要调用成千上万次的 read，这是明显的在浪费 CPU 嘛。

### 如何应对这种困境呢？
操作系统提供了事件轮询的 API。我们使用这个 API 来查询相关套接字是否有相应的读写事件，
- 如果有的话该 API 会立即携带事件列表返回，
- 如果没有事件，该 API 会阻塞，阻塞多长时间可以通过参数设置。

调用事件轮询 API 拿到读写事件后，就可以接着对事件相关的套接字进行读写操作了，这个时候读写操作都是正常进行的，而不会浪费 CPU 空读空写。

这句话我有个疑问，如果套接字 socket 上面有读写事件在进行中，
那么 "就可以接着对事件相关的套接字进行读写操作了" 这个指的是新的线程，新的读写事件？
还是已有的线程，已有的事件进行读写操作？

```python
read_events, write_events = select.select(read_fds, write_fds, timeout)
for event in read_events:
    handle_read(event)
for event in write_events:
    handle_write(event)
```

现代操作系统往往都提供了多种事件轮询 API，从古典的 select 和 poll 系统调用进化到如今的 epoll 和 kqueue 系统调用。
古典的使用简单，性能差，现代的使用复杂，性能超好。
- select, poll
- epoll, kqueue

Nginx/Redis/Java NIO 和各种 Web 服务器都使用了事件轮询 API，它是高性能高并发的关键技术之一。

select 是轮训文件描述列表，大小是1024，O(n)的事件复杂度。

epoll 事件复杂度可以提高到 O(1)，使用红黑树(RB-tree) 数据结构来跟踪当前正在监视的所有文件描述符。

refer to 
- [io_multiplexing](https://nima101.github.io/io_multiplexing).
- [select poll epoll kqueue 区别](https://juejin.cn/post/7071118804855554061)

## StringIO
将字符串当成一个文件一样使用，具备和文件一样的 read 和 write 操作
```python
from StringIO import StringIO  # 纯 python 的实现
from cStringIO import StringIO  # C 实现

s = StringIO()
s.write("hello, ireader")
s.seek(0)
s.read(1024)
```
在查询cStringIO源码的时候，会发现方法的实现只是pass，其实是这些源码是 Pycharm 根据 docstring 自动生成的，
其具体 c 语言实现还得看 https://github.com/python/cpython/blob/main/Modules/_io/stringio.c
```
Usage:

  from cStringIO import StringIO

  an_output_stream=StringIO()
  an_output_stream.write(some_stuff)
  ...
  value=an_output_stream.getvalue()

  an_input_stream=StringIO(a_string)
  spam=an_input_stream.readline()
  spam=an_input_stream.read(5)
  an_input_stream.seek(0)           # OK, start over
  spam=an_input_stream.read()       # and read it all
  
```
refer to [why-do-some-built-in-python-functions-only-have-pass](https://stackoverflow.com/questions/38384206/why-do-some-built-in-python-functions-only-have-pass)


## 源码分析 asyncore.py
asyncore.py 在标准库中。本章 
- `RPCHandler` 继承了 `dispatcher_with_send`，
- `RPCServer` 继承了 `dispatcher`。
- 而 `dispatcher_with_send` 本身继承了 `dispatcher`

作者提到 
- 读缓冲区由用户代码维护，
- 写缓冲区由asyncore内部提供
```python
        self.rbuf = StringIO()  # 读缓冲区由用户代码维护，写缓冲区由asyncore内部提供
```

以下是写操作，缓冲区的控制由 dispatcher_with_send 执行，buffer 是 512 。

```python

class dispatcher_with_send(dispatcher):

    def __init__(self, sock=None, map=None):
        dispatcher.__init__(self, sock, map)
        self.out_buffer = ''

    def initiate_send(self):
        num_sent = 0
        num_sent = dispatcher.send(self, self.out_buffer[:512])
        self.out_buffer = self.out_buffer[num_sent:]

    def handle_write(self):
        self.initiate_send()

    def writable(self):
        return (not self.connected) or len(self.out_buffer)

    def send(self, data):
        if self.debug:
            self.log_info('sending %s' % repr(data))
        self.out_buffer = self.out_buffer + data
        self.initiate_send()

```

用户控制读的 buffer 是 1024。我有点疑问为什么设置为 1024？
```python
            content = self.recv(1024)
```

Base class `dispatcher`
```python
class dispatcher:

    debug = False
    connected = False
    accepting = False
    connecting = False
    closing = False
    addr = None
    ignore_log_types = frozenset(['warning'])

    def __init__(self, sock=None, map=None):
        if map is None:
            self._map = socket_map
        else:
            self._map = map

        self._fileno = None

        if sock:
            # Set to nonblocking just to make sure for cases where we
            # get a socket from a blocking source.
            sock.setblocking(0)
            self.set_socket(sock, map)
            self.connected = True
            # The constructor no longer requires that the socket
            # passed be connected.
            try:
                self.addr = sock.getpeername()
            except socket.error, err:
                if err.args[0] in (ENOTCONN, EINVAL):
                    # To handle the case where we got an unconnected
                    # socket.
                    self.connected = False
                else:
                    # The socket is broken in some unknown way, alert
                    # the user and remove it from the map (to prevent
                    # polling of broken sockets).
                    self.del_channel(map)
                    raise
        else:
            self.socket = None

    def __repr__(self):
        status = [self.__class__.__module__+"."+self.__class__.__name__]
        if self.accepting and self.addr:
            status.append('listening')
        elif self.connected:
            status.append('connected')
        if self.addr is not None:
            try:
                status.append('%s:%d' % self.addr)
            except TypeError:
                status.append(repr(self.addr))
        return '<%s at %#x>' % (' '.join(status), id(self))

    __str__ = __repr__

    def add_channel(self, map=None):
        #self.log_info('adding channel %s' % self)
        if map is None:
            map = self._map
        map[self._fileno] = self

    def del_channel(self, map=None):
        fd = self._fileno
        if map is None:
            map = self._map
        if fd in map:
            #self.log_info('closing channel %d:%s' % (fd, self))
            del map[fd]
        self._fileno = None

    def create_socket(self, family, type):
        self.family_and_type = family, type
        sock = socket.socket(family, type)
        sock.setblocking(0)
        self.set_socket(sock)

    def set_socket(self, sock, map=None):
        self.socket = sock
##        self.__dict__['socket'] = sock
        self._fileno = sock.fileno()
        self.add_channel(map)

    def set_reuse_addr(self):
        # try to re-use a server port if possible
        try:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
                )
        except socket.error:
            pass

    # ==================================================
    # predicates for select()
    # these are used as filters for the lists of sockets
    # to pass to select().
    # ==================================================

    def readable(self):
        return True

    def writable(self):
        return True

    # ==================================================
    # socket object methods.
    # ==================================================

    def listen(self, num):
        self.accepting = True
        if os.name == 'nt' and num > 5:
            num = 5
        return self.socket.listen(num)

    def bind(self, addr):
        self.addr = addr
        return self.socket.bind(addr)

    def connect(self, address):
        self.connected = False
        self.connecting = True
        err = self.socket.connect_ex(address)
        if err in (EINPROGRESS, EALREADY, EWOULDBLOCK) \
        or err == EINVAL and os.name in ('nt', 'ce'):
            self.addr = address
            return
        if err in (0, EISCONN):
            self.addr = address
            self.handle_connect_event()
        else:
            raise socket.error(err, errorcode[err])

    def accept(self):
        # XXX can return either an address pair or None
        try:
            conn, addr = self.socket.accept()
        except TypeError:
            return None
        except socket.error as why:
            if why.args[0] in (EWOULDBLOCK, ECONNABORTED, EAGAIN):
                return None
            else:
                raise
        else:
            return conn, addr

    def send(self, data):
        try:
            result = self.socket.send(data)
            return result
        except socket.error, why:
            if why.args[0] == EWOULDBLOCK:
                return 0
            elif why.args[0] in _DISCONNECTED:
                self.handle_close()
                return 0
            else:
                raise

    def recv(self, buffer_size):
        try:
            data = self.socket.recv(buffer_size)
            if not data:
                # a closed connection is indicated by signaling
                # a read condition, and having recv() return 0.
                self.handle_close()
                return ''
            else:
                return data
        except socket.error, why:
            # winsock sometimes raises ENOTCONN
            if why.args[0] in _DISCONNECTED:
                self.handle_close()
                return ''
            else:
                raise

    def close(self):
        self.connected = False
        self.accepting = False
        self.connecting = False
        self.del_channel()
        try:
            self.socket.close()
        except socket.error, why:
            if why.args[0] not in (ENOTCONN, EBADF):
                raise

    # cheap inheritance, used to pass all other attribute
    # references to the underlying socket object.
    def __getattr__(self, attr):
        try:
            retattr = getattr(self.socket, attr)
        except AttributeError:
            raise AttributeError("%s instance has no attribute '%s'"
                                 %(self.__class__.__name__, attr))
        else:
            msg = "%(me)s.%(attr)s is deprecated. Use %(me)s.socket.%(attr)s " \
                  "instead." % {'me': self.__class__.__name__, 'attr':attr}
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return retattr

    # log and log_info may be overridden to provide more sophisticated
    # logging and warning methods. In general, log is for 'hit' logging
    # and 'log_info' is for informational, warning and error logging.

    def log(self, message):
        sys.stderr.write('log: %s\n' % str(message))

    def log_info(self, message, type='info'):
        if type not in self.ignore_log_types:
            print '%s: %s' % (type, message)

    def handle_read_event(self):
        if self.accepting:
            # accepting sockets are never connected, they "spawn" new
            # sockets that are connected
            self.handle_accept()
        elif not self.connected:
            if self.connecting:
                self.handle_connect_event()
            self.handle_read()
        else:
            self.handle_read()

    def handle_connect_event(self):
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            raise socket.error(err, _strerror(err))
        self.handle_connect()
        self.connected = True
        self.connecting = False

    def handle_write_event(self):
        if self.accepting:
            # Accepting sockets shouldn't get a write event.
            # We will pretend it didn't happen.
            return

        if not self.connected:
            if self.connecting:
                self.handle_connect_event()
        self.handle_write()

    def handle_expt_event(self):
        # handle_expt_event() is called if there might be an error on the
        # socket, or if there is OOB data
        # check for the error condition first
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            # we can get here when select.select() says that there is an
            # exceptional condition on the socket
            # since there is an error, we'll go ahead and close the socket
            # like we would in a subclassed handle_read() that received no
            # data
            self.handle_close()
        else:
            self.handle_expt()

    def handle_error(self):
        nil, t, v, tbinfo = compact_traceback()

        # sometimes a user repr method will crash.
        try:
            self_repr = repr(self)
        except:
            self_repr = '<__repr__(self) failed for object at %0x>' % id(self)

        self.log_info(
            'uncaptured python exception, closing channel %s (%s:%s %s)' % (
                self_repr,
                t,
                v,
                tbinfo
                ),
            'error'
            )
        self.handle_close()

    def handle_expt(self):
        self.log_info('unhandled incoming priority event', 'warning')

    def handle_read(self):
        self.log_info('unhandled read event', 'warning')

    def handle_write(self):
        self.log_info('unhandled write event', 'warning')

    def handle_connect(self):
        self.log_info('unhandled connect event', 'warning')

    def handle_accept(self):
        self.log_info('unhandled accept event', 'warning')

    def handle_close(self):
        self.log_info('unhandled close event', 'warning')
        self.close()

```
可以看到例子 async_single.py `RPCHandler` 中在接受到消息 handle read 时候调用了基类 `dispatcher_with_send` 的 `send` 方法来回复消息：
`handle_read -> handle_rpc -> handler(params) -> ping -> send_result -> send`

`RPCHandler` 覆写了它的基类的基类 `dispatcher` 的回调方法：
- `handle_connect`, 
- `handle_close`, 
- `handle_read`。

其中 `handle_read` 由 `handle_read_event` 调用， 
`handle_read_event` 由 select 调用。详细见如下代码段：

```python
import select
import socket

def readwrite(obj, flags):
    try:
        if flags & select.POLLIN:
            obj.handle_read_event()
        if flags & select.POLLOUT:
            obj.handle_write_event()
        if flags & select.POLLPRI:
            obj.handle_expt_event()
        if flags & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
            obj.handle_close()
    except socket.error, e:
        if e.args[0] not in _DISCONNECTED:
            obj.handle_error()
        else:
            obj.handle_close()
    except _reraised_exceptions:
        raise
    except:
        obj.handle_error()

```

设置服务器端口的重利用
```python
    def set_reuse_addr(self):
        # try to re-use a server port if possible
        try:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
                )
        except socket.error:
            pass

    # ==================================================
    # predicates for select()
    # these are used as filters for the lists of sockets
    # to pass to select().
    # ==================================================

```

这一段代码比较有意思，返回的是tuple，居然可以用一个变量表示。
```python
    pair = self.accept()
        if pair is not None:
            sock, addr = pair
            RPCHandler(sock, addr)
```
源代码如下所示：
```python
    def accept(self):
        # XXX can return either an address pair or None
        try:
            conn, addr = self.socket.accept()
        except TypeError:
            return None
        except socket.error as why:
            if why.args[0] in (EWOULDBLOCK, ECONNABORTED, EAGAIN):
                return None
            else:
                raise
        else:
            return conn, addr
```

本例中 `asyncore.loop()` 应该走的是 `poll(30.0, socket_map)`
```python
def loop(timeout=30.0, use_poll=False, map=None, count=None):
    if map is None:
        map = socket_map

    if use_poll and hasattr(select, 'poll'):
        poll_fun = poll2
    else:
        poll_fun = poll

    if count is None:
        while map:
            poll_fun(timeout, map)

    else:
        while map and count > 0:
            poll_fun(timeout, map)
            count = count - 1
```
相应的 poll 源代码如下所示：
```python
def poll(timeout=0.0, map=None):
    if map is None:
        map = socket_map
    if map:
        r = []; w = []; e = []
        for fd, obj in map.items():
            is_r = obj.readable()
            is_w = obj.writable()
            if is_r:
                r.append(fd)
            # accepting sockets should not be writable
            if is_w and not obj.accepting:
                w.append(fd)
            if is_r or is_w:
                e.append(fd)
        if [] == r == w == e:
            time.sleep(timeout)
            return

        try:
            r, w, e = select.select(r, w, e, timeout)
        except select.error, err:
            if err.args[0] != EINTR:
                raise
            else:
                return

        for fd in r:
            obj = map.get(fd)
            if obj is None:
                continue
            read(obj)

        for fd in w:
            obj = map.get(fd)
            if obj is None:
                continue
            write(obj)

        for fd in e:
            obj = map.get(fd)
            if obj is None:
                continue
            _exception(obj)

```
可以看到以上是维护的 read write exception 的三个列表，通过 select 来通知事件发生。

Pycharm 生成的 select 源代码如下
```python
def select(rlist, wlist, xlist, timeout=None): # real signature unknown; restored from __doc__
    """
    select(rlist, wlist, xlist[, timeout]) -> (rlist, wlist, xlist)
    
    Wait until one or more file descriptors are ready for some kind of I/O.
    The first three arguments are sequences of file descriptors to be waited for:
    rlist -- wait until ready for reading
    wlist -- wait until ready for writing
    xlist -- wait for an ``exceptional condition''
    If only one kind of condition is required, pass [] for the other lists.
    A file descriptor is either a socket or file object, or a small integer
    gotten from a fileno() method call on one of those.
    
    The optional 4th argument specifies a timeout in seconds; it may be
    a floating point number to specify fractions of seconds.  If it is absent
    or None, the call will never time out.
    
    The return value is a tuple of three lists corresponding to the first three
    arguments; each contains the subset of the corresponding file descriptors
    that are ready.
    
    *** IMPORTANT NOTICE ***
    On Windows and OpenVMS, only sockets are supported; on Unix, all file
    descriptors can be used.
    """
    pass
```

