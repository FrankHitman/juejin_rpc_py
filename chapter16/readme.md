# Chapter 16 Notes

## Environment preparation

For chapter 16, it reports import error of `from cStringIO import StringIO`.
so rollback to Python 2.7.18.

```
From Python 3.0 changelog:

The StringIO and cStringIO modules are gone. 
Instead, import the io module and use io.StringIO or io.BytesIO for text and data respectively.
```

refer to

- [stackoverflow](https://stackoverflow.com/questions/28200366/python-3-x-importerror-no-module-named-cstringio)

## 源码阅读

### server.py

```python
class KazooClient(object):
    """An Apache Zookeeper Python client supporting alternate callback
    handlers and high-level functionality.

    Watch functions registered with this class will not get session
    events, unlike the default Zookeeper watches. They will also be
    called with a single argument, a
    :class:`~kazoo.protocol.states.WatchedEvent` instance.

    """

    def __init__(
            self,
            hosts="127.0.0.1:2181",
            timeout=10.0,
            client_id=None,
            handler=None,
            default_acl=None,
            auth_data=None,
            sasl_options=None,
            read_only=None,
            randomize_hosts=True,
            connection_retry=None,
            command_retry=None,
            logger=None,
            keyfile=None,
            keyfile_password=None,
            certfile=None,
            ca=None,
            use_ssl=False,
            verify_certs=True,
            **kwargs,
    ):
        """Create a :class:`KazooClient` instance. All time arguments
        are in seconds.

        :param hosts: Comma-separated list of hosts to connect to
                      (e.g. 127.0.0.1:2181,127.0.0.1:2182,[::1]:2183).
        :param timeout: The longest to wait for a Zookeeper connection.
        :param client_id: A Zookeeper client id, used when
                          re-establishing a prior session connection.
        :param handler: An instance of a class implementing the
                        :class:`~kazoo.interfaces.IHandler` interface
                        for callback handling.
        :param default_acl: A default ACL used on node creation.
        :param auth_data:
            A list of authentication credentials to use for the
            connection. Should be a list of (scheme, credential)
            tuples as :meth:`add_auth` takes.
        :param sasl_options:
            SASL options for the connection, if SASL support is to be used.
            Should be a dict of SASL options passed to the underlying
            `pure-sasl <https://pypi.org/project/pure-sasl>`_ library.

            For example using the DIGEST-MD5 mechnism:

            .. code-block:: python

                sasl_options = {
                    'mechanism': 'DIGEST-MD5',
                    'username': 'myusername',
                    'password': 'mypassword'
                }

            For GSSAPI, using the running process' ticket cache:

            .. code-block:: python

                sasl_options = {
                    'mechanism': 'GSSAPI',
                    'service': 'myzk',                  # optional
                    'principal': 'client@EXAMPLE.COM'   # optional
                }

        :param read_only: Allow connections to read only servers.
        :param randomize_hosts: By default randomize host selection.
        :param connection_retry:
            A :class:`kazoo.retry.KazooRetry` object to use for
            retrying the connection to Zookeeper. Also can be a dict of
            options which will be used for creating one.
        :param command_retry:
            A :class:`kazoo.retry.KazooRetry` object to use for
            the :meth:`KazooClient.retry` method. Also can be a dict of
            options which will be used for creating one.
        :param logger: A custom logger to use instead of the module
            global `log` instance.
        :param keyfile: SSL keyfile to use for authentication
        :param keyfile_password: SSL keyfile password
        :param certfile: SSL certfile to use for authentication
        :param ca: SSL CA file to use for authentication
        :param use_ssl: argument to control whether SSL is used or not
        :param verify_certs: when using SSL, argument to bypass
            certs verification

        Basic Example:

        .. code-block:: python

            zk = KazooClient()
            zk.start()
            children = zk.get_children('/')
            zk.stop()

        As a convenience all recipe classes are available as attributes
        and get automatically bound to the client. For example::

            zk = KazooClient()
            zk.start()
            lock = zk.Lock('/lock_path')

        .. versionadded:: 0.6
            The read_only option. Requires Zookeeper 3.4+

        .. versionadded:: 0.6
            The retry_max_delay option.

        .. versionadded:: 0.6
            The randomize_hosts option.

        .. versionchanged:: 0.8
            Removed the unused watcher argument (was second argument).

        .. versionadded:: 1.2
            The connection_retry, command_retry and logger options.

        .. versionadded:: 2.7
            The sasl_options option.

        """
```

ACL（Access Control List）访问控制列表是一种用于控制资源访问权限的机制。

```python
    def start(self, timeout=15):
        """Initiate connection to ZK.
    
        :param timeout: Time in seconds to wait for connection to
                        succeed.
        :raises: :attr:`~kazoo.interfaces.IHandler.timeout_exception`
                 if the connection wasn't established within `timeout`
                 seconds.
    
        """
        event = self.start_async()
        event.wait(timeout=timeout)
        if not self.connected:
            # We time-out, ensure we are disconnected
            self.stop()
            self.close()
            raise self.handler.timeout_exception("Connection time-out")
    
        if self.chroot and not self.exists("/"):
            warnings.warn(
                "No chroot path exists, the chroot path "
                "should be created before normal use."
            )
```

```python
    def ensure_path(self, path, acl=None):
        """Recursively create a path if it doesn't exist.
    
        :param path: Path of node.
        :param acl: Permissions for node.
    
        """
        return self.ensure_path_async(path, acl).get()

```

```python
    def create(
        self,
        path,
        value=b"",
        acl=None,
        ephemeral=False,
        sequence=False,
        makepath=False,
        include_data=False,
    ):
        """Create a node with the given value as its data. Optionally
        set an ACL on the node.
    
        The ephemeral and sequence arguments determine the type of the
        node.
    
        An ephemeral node will be automatically removed by ZooKeeper
        when the session associated with the creation of the node
        expires.
    
        A sequential node will be given the specified path plus a
        suffix `i` where i is the current sequential number of the
        node. The sequence number is always fixed length of 10 digits,
        0 padded. Once such a node is created, the sequential number
        will be incremented by one.
    
        If a node with the same actual path already exists in
        ZooKeeper, a NodeExistsError will be raised. Note that since a
        different actual path is used for each invocation of creating
        sequential nodes with the same path argument, the call will
        never raise NodeExistsError.
    
        If the parent node does not exist in ZooKeeper, a NoNodeError
        will be raised. Setting the optional `makepath` argument to
        `True` will create all missing parent nodes instead.
    
        An ephemeral node cannot have children. If the parent node of
        the given path is ephemeral, a NoChildrenForEphemeralsError
        will be raised.
    
        This operation, if successful, will trigger all the watches
        left on the node of the given path by :meth:`exists` and
        :meth:`get` API calls, and the watches left on the parent node
        by :meth:`get_children` API calls.
    
        The maximum allowable size of the node value is 1 MB. Values
        larger than this will cause a ZookeeperError to be raised.
    
        :param path: Path of node.
        :param value: Initial bytes value of node.
        :param acl: :class:`~kazoo.security.ACL` list.
        :param ephemeral: Boolean indicating whether node is ephemeral
                          (tied to this session).
        :param sequence: Boolean indicating whether path is suffixed
                         with a unique index.
        :param makepath: Whether the path should be created if it
                         doesn't exist.
        :param include_data:
            Include the :class:`~kazoo.protocol.states.ZnodeStat` of
            the node in addition to its real path. This option changes
            the return value to be a tuple of (path, stat).
    
        :returns: Real path of the new node, or tuple if `include_data`
                  is `True`
        :rtype: str
    
        :raises:
            :exc:`~kazoo.exceptions.NodeExistsError` if the node
            already exists.
    
            :exc:`~kazoo.exceptions.NoNodeError` if parent nodes are
            missing.
    
            :exc:`~kazoo.exceptions.NoChildrenForEphemeralsError` if
            the parent node is an ephemeral node.
    
            :exc:`~kazoo.exceptions.ZookeeperError` if the provided
            value is too large.
    
            :exc:`~kazoo.exceptions.ZookeeperError` if the server
            returns a non-zero error code.
    
        .. versionadded:: 1.1
            The `makepath` option.
        .. versionadded:: 2.7
            The `include_data` option.
        """
        acl = acl or self.default_acl
        return self.create_async(
            path,
            value,
            acl=acl,
            ephemeral=ephemeral,
            sequence=sequence,
            makepath=makepath,
            include_data=include_data,
        ).get()

```

ephemeral a.短暂的
临时节点不能有子节点

```python
    def stop(self):
        """Gracefully stop this Zookeeper session.
    
        This method can be called while a reconnection attempt is in
        progress, which will then be halted.
    
        Once the connection is closed, its session becomes invalid. All
        the ephemeral nodes in the ZooKeeper server associated with the
        session will be removed. The watches left on those nodes (and
        on their parents) will be triggered.
    
        """
        if self._stopped.is_set():
            return
    
        self._stopped.set()
        self._queue.append((CloseInstance, None))
        try:
            self._connection._write_sock.send(b"\0")
        finally:
            self._safe_close()

```

#### 关闭与收割子进程

本章的服务端代码优雅的展示了父进程如何通知子进程关闭和收割子进程

```python
        
        for pid in self.child_pids:
            print 'before kill'
            try:
                os.kill(pid, signal.SIGINT)  # 关闭子进程
                pids.append(pid)
            except OSError, ex:
                if ex.args[0] == errno.ECHILD:  # 目标子进程已经提前挂了
                    continue
                raise ex
            print 'after kill', pid
        for pid in pids:
            while True:
                try:
                    os.waitpid(pid, 0)  # 收割目标子进程
                    break
                except OSError, ex:
                    if ex.args[0] == errno.ECHILD:  # 子进程已经割过了
                        break
                    if ex.args[0] != errno.EINTR:
                        raise ex  # 被其它信号打断了，要重试
            print 'wait over', pid
```

```python
    def reap_child(self, sig, frame):
        print 'before reap'
        while True:
            try:
                info = os.waitpid(-1, os.WNOHANG)  # 收割任意子进程
                break
            except OSError, ex:
                if ex.args[0] == errno.ECHILD:
                    return  # 没有子进程可以收割
                if ex.args[0] != errno.EINTR:
                    raise ex  # 被其它信号打断要重试
        pid = info[0]
        try:
            self.child_pids.remove(pid)
        except ValueError:
            pass
        print 'after reap', pid

```

查阅 [Python 2.7 官方文档](https://docs.python.org/zh-cn/2.7/library/os.html?highlight=waitpid#os.waitpid)， waitpid
解释如下：

```
os.waitpid(pid, options)
本函数的细节在 Unix 和 Windows 上有不同之处。

在 Unix 上：等待进程号为 pid 的子进程执行完毕，返回一个元组，内含其进程 ID 和退出状态指示（编码与 wait() 相同）。
调用的语义受整数 options 的影响，常规操作下该值应为 0。

如果 pid 大于 0，则 waitpid() 会获取该指定进程的状态信息。
如果 pid 为 0，则获取当前进程所在进程组中的所有子进程的状态。
如果 pid 为 -1，则获取当前进程的子进程状态。
如果 pid 小于 -1，则获取进程组 -pid （ pid 的绝对值）中所有进程的状态。

当系统调用返回 -1 时，将抛出带有错误码的 OSError 异常。

在 Windows 上：等待句柄为 pid 的进程执行完毕，返回一个元组，内含 pid 以及左移 8 位后的退出状态（移位简化了跨平台使用本函数）。
小于或等于 0 的 pid 在 Windows 上没有特殊含义，且会抛出异常。整数值 options 无效。
pid 可以指向任何 ID 已知的进程，不一定是子进程。调用 spawn* 函数时传入 P_NOWAIT 将返回合适的进程句柄。
```

waitpid(pid, options) 中 options 枚举值的解释

```
os.WNOHANG
The option for waitpid() to return immediately if no child process status is available immediately. 
The function returns (0, 0) in this case.

Availability: Unix.
```

errno 中各个常量值的解释

```
errno.EPERM
Operation not permitted

errno.EINTR
Interrupted system call

errno.ECHILD
No child processes
```

refer to

- [Python Docs](https://docs.python.org/2.7/library/errno.html?highlight=errno)

signal 中信号量的解释

- SIGTERM is an alias for terminate().
- SIGINT is translated into a KeyboardInterrupt exception.
- SIGCHLD

### client.py

可以看到 client 客户端与服务端都是调用 `KazooClient(hosts="127.0.0.1:2181")`，都是作为 zookeeper 的客户端来使用。
zookeeper的服务端应该需要另外启动的一个组件。

get_children 获取一个路径上的所有子节点，返回的是子节点列表。

```python
    def get_children(self, path, watch=None, include_data=False):
        """Get a list of child nodes of a path.
    
        If a watch is provided it will be left on the node with the
        given path. The watch will be triggered by a successful
        operation that deletes the node of the given path or
        creates/deletes a child under the node.
    
        The list of children returned is not sorted and no guarantee is
        provided as to its natural or lexical order.
    
        :param path: Path of node to list.
        :param watch: Optional watch callback to set for future changes
                      to this path.
        :param include_data:
            Include the :class:`~kazoo.protocol.states.ZnodeStat` of
            the node in addition to the children. This option changes
            the return value to be a tuple of (children, stat).
    
        :returns: List of child node names, or tuple if `include_data`
                  is `True`.
        :rtype: list
    
        :raises:
            :exc:`~kazoo.exceptions.NoNodeError` if the node doesn't
            exist.
    
            :exc:`~kazoo.exceptions.ZookeeperError` if the server
            returns a non-zero error code.
    
        .. versionadded:: 0.5
            The `include_data` option.
    
        """
        return self.get_children_async(
            path, watch=watch, include_data=include_data
        ).get()

```

可以看到 watch 参数传的是回调函数，将来该节点发生变化的时候会调用。本例中传递的是闭包函数本身。

kazoo/client.py 的 get 获取节点上存储的值

```python
    def get(self, path, watch=None):
        """Get the value of a node.
    
        If a watch is provided, it will be left on the node with the
        given path. The watch will be triggered by a successful
        operation that sets data on the node, or deletes the node.
    
        :param path: Path of node.
        :param watch: Optional watch callback to set for future changes
                      to this path.
        :returns:
            Tuple (value, :class:`~kazoo.protocol.states.ZnodeStat`) of
            node.
        :rtype: tuple
    
        :raises:
            :exc:`~kazoo.exceptions.NoNodeError` if the node doesn't
            exist
    
            :exc:`~kazoo.exceptions.ZookeeperError` if the server
            returns a non-zero error code
    
        """
        return self.get_async(path, watch=watch).get()

```

可以看到以上同步方法是调用的异步方法的 get 来获取的，此 get 存在于 kazoo/interface.py 中

```python
    def get(self, block=True, timeout=None):
        """Return the stored value or raise the exception
    
        :param block: Whether this method should block or return
                      immediately.
        :type block: bool
        :param timeout: How long to wait for a value when `block` is
                        `True`.
        :type timeout: float
    
        If this instance already holds a value / an exception, return /
        raise it immediately. Otherwise, block until :meth:`set` or
        :meth:`set_exception` has been called or until the optional
        timeout occurs."""

```

```python
class AsyncResult(utils.AsyncResult):
    """A one-time event that stores a value or an exception"""

    def __init__(self, handler):
        super(AsyncResult, self).__init__(
            handler, threading.Condition, KazooTimeoutError
        )

```

大概看出是通过 线程间 condition 通信 来实现异步的。

```python

def Condition(*args, **kwargs):
    """Factory function that returns a new condition variable object.

    A condition variable allows one or more threads to wait until they are
    notified by another thread.

    If the lock argument is given and not None, it must be a Lock or RLock
    object, and it is used as the underlying lock. Otherwise, a new RLock object
    is created and used as the underlying lock.

    """
    return _Condition(*args, **kwargs)


class _Condition(_Verbose):
    """Condition variables allow one or more threads to wait until they are
       notified by another thread.
    """

    def __init__(self, lock=None, verbose=None):
        _Verbose.__init__(self, verbose)
        if lock is None:
            lock = RLock()
        self.__lock = lock
        # Export the lock's acquire() and release() methods
        self.acquire = lock.acquire
        self.release = lock.release
        # If the lock defines _release_save() and/or _acquire_restore(),
        # these override the default implementations (which just call
        # release() and acquire() on the lock).  Ditto for _is_owned().
        try:
            self._release_save = lock._release_save
        except AttributeError:
            pass
        try:
            self._acquire_restore = lock._acquire_restore
        except AttributeError:
            pass
        try:
            self._is_owned = lock._is_owned
        except AttributeError:
            pass
        self.__waiters = []

    def __enter__(self):
        return self.__lock.__enter__()

    def __exit__(self, *args):
        return self.__lock.__exit__(*args)

    def __repr__(self):
        return "<Condition(%s, %d)>" % (self.__lock, len(self.__waiters))

    def _release_save(self):
        self.__lock.release()  # No state to save

    def _acquire_restore(self, x):
        self.__lock.acquire()  # Ignore saved state

    def _is_owned(self):
        # Return True if lock is owned by current_thread.
        # This method is called only if __lock doesn't have _is_owned().
        if self.__lock.acquire(0):
            self.__lock.release()
            return False
        else:
            return True

    def wait(self, timeout=None):
        """Wait until notified or until a timeout occurs.

        If the calling thread has not acquired the lock when this method is
        called, a RuntimeError is raised.

        This method releases the underlying lock, and then blocks until it is
        awakened by a notify() or notifyAll() call for the same condition
        variable in another thread, or until the optional timeout occurs. Once
        awakened or timed out, it re-acquires the lock and returns.

        When the timeout argument is present and not None, it should be a
        floating point number specifying a timeout for the operation in seconds
        (or fractions thereof).

        When the underlying lock is an RLock, it is not released using its
        release() method, since this may not actually unlock the lock when it
        was acquired multiple times recursively. Instead, an internal interface
        of the RLock class is used, which really unlocks it even when it has
        been recursively acquired several times. Another internal interface is
        then used to restore the recursion level when the lock is reacquired.

        """
        if not self._is_owned():
            raise RuntimeError("cannot wait on un-acquired lock")
        waiter = _allocate_lock()
        waiter.acquire()
        self.__waiters.append(waiter)
        saved_state = self._release_save()
        try:  # restore state no matter what (e.g., KeyboardInterrupt)
            if timeout is None:
                waiter.acquire()
                if __debug__:
                    self._note("%s.wait(): got it", self)
            else:
                # Balancing act:  We can't afford a pure busy loop, so we
                # have to sleep; but if we sleep the whole timeout time,
                # we'll be unresponsive.  The scheme here sleeps very
                # little at first, longer as time goes on, but never longer
                # than 20 times per second (or the timeout time remaining).
                endtime = _time() + timeout
                delay = 0.0005  # 500 us -> initial delay of 1 ms
                while True:
                    gotit = waiter.acquire(0)
                    if gotit:
                        break
                    remaining = endtime - _time()
                    if remaining <= 0:
                        break
                    delay = min(delay * 2, remaining, .05)
                    _sleep(delay)
                if not gotit:
                    if __debug__:
                        self._note("%s.wait(%s): timed out", self, timeout)
                    try:
                        self.__waiters.remove(waiter)
                    except ValueError:
                        pass
                else:
                    if __debug__:
                        self._note("%s.wait(%s): got it", self, timeout)
        finally:
            self._acquire_restore(saved_state)

    def notify(self, n=1):
        """Wake up one or more threads waiting on this condition, if any.

        If the calling thread has not acquired the lock when this method is
        called, a RuntimeError is raised.

        This method wakes up at most n of the threads waiting for the condition
        variable; it is a no-op if no threads are waiting.

        """
        if not self._is_owned():
            raise RuntimeError("cannot notify on un-acquired lock")
        __waiters = self.__waiters
        waiters = __waiters[:n]
        if not waiters:
            if __debug__:
                self._note("%s.notify(): no waiters", self)
            return
        self._note("%s.notify(): notifying %d waiter%s", self, n,
                   n != 1 and "s" or "")
        for waiter in waiters:
            waiter.release()
            try:
                __waiters.remove(waiter)
            except ValueError:
                pass

    def notifyAll(self):
        """Wake up all threads waiting on this condition.

        If the calling thread has not acquired the lock when this method
        is called, a RuntimeError is raised.

        """
        self.notify(len(self.__waiters))

    notify_all = notifyAll

```

```python
    def get(self, block=True, timeout=None):
        """Return the stored value or raise the exception.
    
        If there is no value raises TimeoutError.
    
        """
        with self._condition:
            if self._exception is not _NONE:
                if self._exception is None:
                    return self.value
                raise self._exception
            elif block:
                self._condition.wait(timeout)
                if self._exception is not _NONE:
                    if self._exception is None:
                        return self.value
                    raise self._exception
    
            # if we get to this point we timeout
            raise self._timeout_factory()

```

#### 关于 threading 中 condition， Rlock 和 Lock 的使用

Gemini 生成的 condition 用于生产者消费者模型中

```python
import threading
import queue

# Shared queue for data
data_queue = queue.Queue()

# Condition variable for synchronization
condition = threading.Condition()


def producer():
    with condition:
        for item in data:
            data_queue.put(item)
            condition.notify()  # Notify consumer that data is available


def consumer():
    with condition:
        while True:
            item = data_queue.get()
            # Process the item
            condition.wait()  # Wait for producer to add data


# Create and start producer and consumer threads
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

# Wait for threads to finish (optional)
producer_thread.join()
consumer_thread.join()
```

例外一个 example： [play_condition](play_condition.py)

refer to

- [cn blog](https://www.cnblogs.com/yoyo1216/p/15740439.html)

Lock 不可重入锁:

A basic lock object.

- Not Reentrant: A thread cannot acquire the same lock it already holds. Attempting to do so leads to a deadlock.
- Use cases: Simple synchronization scenarios where a thread acquires the lock, performs a critical section of code,
  and then releases it.

Rlock 读锁，同一线程可重入锁:

- Reentrant: A thread can acquire the same lock it already holds multiple times. This allows for nested critical
  sections within the same thread.
- Use cases: Complex scenarios where a thread might need to acquire the same lock multiple times during its execution,
  or situations involving nested function calls and callbacks.

再来阅读 Condition 的源代码，发现类里面存储了两把锁，一把 `self.__lock`，
还有一把 `waiter = _allocate_lock()` 塞到了 self.__waiters 列表中用于 notify

我有一个困惑， `saved_state = self._release_save()` 是释放第一把锁，居然会有返回值，
然而 `release` 方法的注释说明了没有返回值！！！
并且以上返回值在 `self._acquire_restore(saved_state)` 中重新用到，用于再次加锁。

_Condition 类中定义的 _release_save
```python
    def _release_save(self):
        self.__lock.release()  # No state to save
                
```

RLock 类中定义的 release
```python
    def release(self):
        """Release a lock, decrementing the recursion level.
    
        If after the decrement it is zero, reset the lock to unlocked (not owned
        by any thread), and if any other threads are blocked waiting for the
        lock to become unlocked, allow exactly one of them to proceed. If after
        the decrement the recursion level is still nonzero, the lock remains
        locked and owned by the calling thread.
    
        Only call this method when the calling thread owns the lock. A
        RuntimeError is raised if this method is called when the lock is
        unlocked.
    
        There is no return value.
    
        """
        if self.__owner != _get_ident():
            raise RuntimeError("cannot release un-acquired lock")
        self.__count = count = self.__count - 1
        if not count:
            self.__owner = None
            self.__block.release()
            if __debug__:
                self._note("%s.release(): final release", self)
        else:
            if __debug__:
                self._note("%s.release(): non-final release", self)

```

```python
    def _acquire_restore(self, x):
        self.__lock.acquire()  # Ignore saved state
```

以上重新加锁代码可以看到传参 x 并没有被使用到，那么这个参数的作用是什么呢？

然而我又注意到 _Condition 类的初始化中有以下这一段描述

```python
        # If the lock defines _release_save() and/or _acquire_restore(),
        # these override the default implementations (which just call
        # release() and acquire() on the lock).  Ditto for _is_owned().
        try:
            self._release_save = lock._release_save
        except AttributeError:
            pass
        try:
            self._acquire_restore = lock._acquire_restore
        except AttributeError:
            pass
        try:
            self._is_owned = lock._is_owned
        except AttributeError:
            pass
```

因为默认用的是 RLock 类，而 RLock 类中定义了上面三个方法，
所以它们覆盖了 _Condition 类中定义的 _release_save， _acquire_restore， _is_owned

RLock 类的 _release_save， _acquire_restore， _is_owned 方法们

```python
    # Internal methods used by condition variables

    def _acquire_restore(self, count_owner):
        count, owner = count_owner
        self.__block.acquire()
        self.__count = count
        self.__owner = owner
        if __debug__:
            self._note("%s._acquire_restore()", self)
    
    
    def _release_save(self):
        if __debug__:
            self._note("%s._release_save()", self)
        count = self.__count
        self.__count = 0
        owner = self.__owner
        self.__owner = None
        self.__block.release()
        return (count, owner)
    
    
    def _is_owned(self):
        return self.__owner == _get_ident()

```

可以看到 _release_save 返回 (count, owner) 元组，该元组在 _acquire_restore 中用到。

ChatGPT 解释如下

In the Python 2.7 threading.py module, the _acquire_restore and _release_save functions are used in the implementation
of the RLock class, which is a reentrant lock.

_acquire_restore(state):
- This function is responsible for acquiring the lock while restoring the previous state of the lock.
- It first acquires the lock by calling the acquire() method on the lock object.
- After acquiring the lock, it restores the previous state of the lock by calling the _set_ident() method on the lock
object, passing the state argument.
- The purpose of this function is to ensure that the lock is acquired and restored in a thread-safe way, preventing race
conditions and other concurrency issues.

_release_save():
- This function is responsible for releasing the lock while saving the current state of the lock.
- It first saves the current state of the lock by calling the _get_ident() method on the lock object.
- After saving the state, it releases the lock by calling the release() method on the lock object.
- The purpose of this function is to ensure that the lock is released in a thread-safe way, allowing other threads to
acquire the lock if necessary.

These two functions are used internally by the RLock class to manage the state of the lock during acquisition and
release operations. They are not intended to be called directly by the user, as they are part of the implementation
details of the threading module.
The RLock class is a reentrant lock, which means that a thread can acquire the same lock multiple times without causing
a deadlock. The _acquire_restore and _release_save functions play a crucial role in maintaining the correct state of the
lock during these reentrant operations.

以上 GPT 解释 还有有点问题 源码中没有调用 _set_ident() 和 _get_ident() 的情况。

## 小册子内容
### 杀死子进程
- os.kill(pid, signal.SIGKILL) signal of kill 杀死
  - SIGKILL 信号比较暴力，对方进程会立即 crash，进程无法为 SIGKILL 信号设置处理函数。
  - SIGKILL 当你使用 kill -9 杀死进程时，进程会收到信号。此信号的处理函数无法覆盖，进程收到此信号会立即暴力退出。

- os.kill(pid, signal.SIGTERM) signal of terminate 终止
  - 通过 SIGTERM 信号温柔地通知对方退出，只要对方进程设置了信号处理函数，就可以在退出之前执行一些清理工作。
  - SIGTERM 当你使用不带参数的 kill 指令杀死进程时，进程会收到该信号。此信号默认行为也是退出进程，但是允许用户自定义信号处理函数。

- os.kill(pid, signal.SIGINT) signal of interrupt 打断 暂停
  - KeyboardInterrupt = ctrl+c
  - SIGINT 信号温柔地通知对方退出，只要对方进程设置了信号处理函数，就可以在退出之前执行一些清理工作。

- SIGCHLD signal of child 
  - 子进程退出时，父进程会收到此信号。
  - 当子进程退出后，父进程必须通过 waitpid 来收割子进程，否则子进程将成为僵尸进程，直到父进程也退出了，其资源才会彻底释放。

- SIGTSTP signal of stop
  - ctrl+z 

### 收割子进程
收割子进程使用os.waitpid(pid, options)系统调用，
- 可以提供具体 pid 来收割指定子进程，
- 也可以通过参数 pid=-1 来收割任意子进程。
- options 如果是 0，就表示阻塞等待子进程结束才会返回，
- options 如果是 WNOHANG 就表示非阻塞，有,就返回指定进程的 pid，没有,就返回 0。
- 如果指定 pid 进程不存在或者没有子进程可以收割，就会抛出 OSError(errno.ECHILD)
- 如果 waitpid 被其它信号打断，就会抛出 OSError(errno.EINTR)，这个时候可以选择重试。

### 信号连续打断
当我们正在执行一个信号处理函数时，可能又收到另外一个信号，该信号会打断当前正在执行的信号处理函数。

如果信号处理函数中 waitpid 正在执行，这个时候突然来了一个 SIGINT 信号，
那么待 SIGINT 信号处理函数执行完毕后返回到原来的 waitpid 调用时，waitpid 将会爆出 OSError 异常，
也就是 waitpid 调用被打断了。

我们通过检查异常对象里面的错误类型，来决定是否要继续重试。

- 如果异常类型是 errno.EINTR，就可以继续重试 waitpid，
- 如果是 errno.ECHILD，说明目标子进程已经结束了，
- 遇到其它类型应该向上抛出异常。至于什么是其它异常，这个是没有具体定义的，而且是不应该出现的。

### 错误码
```
errno.EPERM
Operation not permitted  # 操作不允许

errno.ENOENT
No such file or directory  # 文件没找到

errno.ESRCH
No such process  # 进程未找到

errno.EINTR
Interrupted system call  # 调用被打断

errno.EIO
I/O error  # I/O 错误

errno.ENXIO
No such device or address  # 设备未找到

errno.E2BIG
Arg list too long  # 调用参数太多

errno.ENOEXEC¶
Exec format error  # exec 调用二进制文件格式错误

errno.EBADF
Bad file number  # 文件描述符错误

errno.ECHILD
No child processes  # 子进程不存在， errno.ECHILD 在 waitpid 收割子进程时，目标进程不存在，就会有这样的错误。

errno.EAGAIN
Try again  # I/O 操作被打断，告知 I/O 操作重试

```

### 服务发现
ZooKeeper 的节点信息以树状结构存储在内存中。每个节点内部可以存储一个字节串，节点用于服务发现时存储服务器的地址信息。

#### 顺序节点
ZooKeeper 支持顺序节点 (sequence)，它可以在节点名称后面自动追加自增 id，避免节点名称重复。
在服务发现中会有多个子节点，使用顺序节点可以很方便地增加子节点。

#### 临时节点
ZooKeeper 支持临时节点 (ephemeral)，在会话结束时，临时节点会自动释放。
之所以会用到临时节点是因为 ZooKeeper 的会话支持连接断开重连。
短时间的连接断开并不会立即删除内存会话，而是有个过期时间，时间一到，会话会自动过期。
可以显式发送会话结束指令强制关闭会话，
如果客户端进程突然 crash 掉，来不及发送会话关闭指令，ZooKeeper 将通过会话自动过期机制关闭会话。

## 运行
在 CentOS 系统上 执行本章代码。
```
sudo yum install java -y
curl -o zookeeper-bin.tar.gz https://dlcdn.apache.org/zookeeper/zookeeper-3.8.4/apache-zookeeper-3.8.4-bin.tar.gz
tar -xf zookeeper-bin.tar.gz
mv apache-zookeeper-3.8.4-bin /opt/
cd /opt/apache-zookeeper-3.8.4-bin/
cd conf/
cp zoo_sample.cfg zoo.cfg
echo "export PATH=$PATH:/opt/apache-zookeeper-3.8.4-bin/bin" >> ~/.bashrc
cat ~/.bashrc 
source ~/.bashrc 
zkServer.sh start
ps -ef|grep zoo
zkServer.sh status
sudo pip install kazoo==2.7.0
python server.py 127.0.0.1 8001
python server.py 127.0.0.1 8002
python client.py
```
kazoo 最新版本(2.10.0)已经不支持 Python 2.7 运行会报语法错误。最后支持 Python 2.7 的是 kazoo 2.7 版本。

refer to 
- [kazoo release](https://github.com/python-zk/kazoo/releases)

