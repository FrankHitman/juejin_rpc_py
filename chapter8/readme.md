# Chapter 8 Notes

## Questions

### 为什么设置 buffer size 为 4？
服务端和客户端都是先读取消息前缀的长度， `length_prefix = sock.recv(4)  # 响应长度前缀，为什么设置 buffer size 为4？`

消息前缀存储着消息体的长度。

因为 struct.pack方法返回的就是4个字节的长度的字符串
```commandline
value_in_bytes = struct.pack("I", 1024)  # 将一个整数编码成 4 个字节的字符串
value, = struct.unpack("I", value_in_bytes)  # 将一个 4 字节的字符串解码成一个整数
```

### socket
标准库 socket.py 调用的是 _socket.py，方法sendall recv 的实现都在 _socket.py 里面

in socket.py
```python
_realsocket = socket
```
in _socket.py
```python

socket = SocketType

    def recv(self, buffersize, flags=None): # real signature unknown; restored from __doc__
        """
        recv(buffersize[, flags]) -> data
        
        Receive up to buffersize bytes from the socket.  For the optional flags
        argument, see the Unix manual.  When no data is available, block until
        at least one byte is available or until the remote end is closed.  When
        the remote end is closed and all data is read, return the empty string.
        """
        pass

    def send(self, data, flags=None): # real signature unknown; restored from __doc__
        """
        send(data[, flags]) -> count
        
        Send a data string to the socket.  For the optional flags
        argument, see the Unix manual.  Return the number of bytes
        sent; this may be less than len(data) if the network is busy.
        """
        pass

    def sendall(self, data, flags=None): # real signature unknown; restored from __doc__
        """
        sendall(data[, flags])
        
        Send a data string to the socket.  For the optional flags
        argument, see the Unix manual.  This calls send() repeatedly
        until all data is sent.  If an error occurs, it's impossible
        to tell how much data has been sent.
        """
        pass
```
