# Chapter 9 Notes
## Question

### What are the differences between block mode and multithread mode
Convert blocking single mode to multithread mode, 
The only difference is adding 
`thread.start_new_thread(handle_conn, (conn, addr, handlers))  # 开启新线程进行处理，就这行代码不一样`

标准库中 thread.py 解释
```python

def start_new_thread(function, args, kwargs=None): # real signature unknown; restored from __doc__
    """
    start_new_thread(function, args[, kwargs])
    (start_new() is an obsolete synonym)
    
    Start a new thread and return its identifier.  The thread will call the
    function with positional arguments from the tuple args and keyword arguments
    taken from the optional dictionary kwargs.  The thread exits when the
    function returns; the return value is ignored.  The thread will also exit
    when the function raises an unhandled exception; a stack trace will be
    printed unless the exception is SystemExit.
    """
    pass
```

- 开始新线程，并返回它的 id
- 新线程中的方法正常return，或者 raise 异常时候 会退出
- 返回的值（id）会被忽略

### Complement
如果多个线程竞争读写一个 IO 资源的话，会产生数据错乱的问题，所以需要引入线程锁的概念
```python
def allocate_lock(): # real signature unknown; restored from __doc__
    """
    allocate_lock() -> lock object
    (allocate() is an obsolete synonym)
    
    Create a new lock object.  See help(LockType) for information about locks.
    """
    pass

class LockType(object):
    """
    A lock object is a synchronization primitive.  To create a lock,
    call the PyThread_allocate_lock() function.  Methods are:
    
    acquire() -- lock the lock, possibly blocking until it can be obtained
    release() -- unlock of the lock
    locked() -- test whether the lock is currently locked
    
    A lock is not owned by the thread that locked it; another thread may
    unlock it.  A thread attempting to lock a lock that it has already locked
    will block until another thread unlocks it.  Deadlocks may ensue.
    """
    def acquire(self, wait=None): # real signature unknown; restored from __doc__
        """
        acquire([wait]) -> bool
        (acquire_lock() is an obsolete synonym)
        
        Lock the lock.  Without argument, this blocks if the lock is already
        locked (even by the same thread), waiting for another thread to release
        the lock, and return True once the lock is acquired.
        With an argument, this will only block if the argument is true,
        and the return value reflects whether the lock is acquired.
        The blocking operation is not interruptible.
        """
        return False
    
    def release(self): # real signature unknown; restored from __doc__
        """
        release()
        (release_lock() is an obsolete synonym)
        
        Release the lock, allowing another thread that is blocked waiting for
        the lock to acquire the lock.  The lock must be in the locked state,
        but it needn't be locked by the same thread that unlocks it.
        """
        pass
    
    def __enter__(self, *args, **kwargs): # real signature unknown
        """
        acquire([wait]) -> bool
        (acquire_lock() is an obsolete synonym)
        
        Lock the lock.  Without argument, this blocks if the lock is already
        locked (even by the same thread), waiting for another thread to release
        the lock, and return True once the lock is acquired.
        With an argument, this will only block if the argument is true,
        and the return value reflects whether the lock is acquired.
        The blocking operation is not interruptible.
        """
        pass

    def __exit__(self, *args, **kwargs): # real signature unknown
        """
        release()
        (release_lock() is an obsolete synonym)
        
        Release the lock, allowing another thread that is blocked waiting for
        the lock to acquire the lock.  The lock must be in the locked state,
        but it needn't be locked by the same thread that unlocks it.
        """
        pass

```

- 为什么 `A lock is not owned by the thread that locked it`？
难道就是因为锁不是由锁住它的那个线程独有，所以其他线程才可以访问它，并且可以解锁，方便线程间通信/同步。

- 同一个线程重复给同一个锁加锁，会block住，更加有可能给自己弄成死锁，所以加锁时候要注意时序，数量，和临界区。

- `lock.acquire(wait=True)` wait=True 的时候这个线程会卡在这里直到锁被获取到，
  `lock.acquire()`不阻塞，当即获取不到锁就返回 False。

- `but it needn't be locked by the same thread that unlocks it.` 意思是解锁的线程自己可能白忙活，
解锁之后，锁被其他线程抢走。

- LockType 声明了 `__enter__` 与 `__exit__`方法，代表其支持 context 的 `with`写法，避免忘记释放锁而导致阻塞等问题。

```python
import thread

lock = thread.allocate_lock()
with lock:
    # codes that need to be embraced by lock
    # ...
    pass
```
- threading.py 与 thread.py 的区别是什么？
thread.py 是基于方法的，而 threading.py 是基于类的，threading.py 调用了 thread.py 中的方法。
```python
# in threading.py
try:
    import thread
except ImportError:
    del _sys.modules[__name__]
    raise

_start_new_thread = thread.start_new_thread
_allocate_lock = thread.allocate_lock
_get_ident = thread.get_ident
ThreadError = thread.error
del thread
```

