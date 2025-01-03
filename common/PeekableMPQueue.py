"""
Extends Multiprocessing Queue to allow peeking at elements
without removing them from the queue.
Hugo Burton
11/10/2024
"""

from typing import Any, Optional
import time
from multiprocessing import Queue as MPQueue, context, Manager
from queue import Empty

_ForkingPickler = context.reduction.ForkingPickler


class PeekableMPQueue:
    def __init__(self, manager=None):
        """
        Initialize a manager and a queue.

        Args:
            manager (Optional[Manager]): An optional Manager instance.
        """
        self.manager = manager if manager is not None else Manager()
        self.queue = self.manager.Queue()

    def __getattr__(self, name):
        """
        Delegate attribute access to the internal queue object,
        unless the attribute is 'peek'.
        """
        if name == "peek":
            return self.peek
        return getattr(self.queue, name)

    def peek(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        """
        Peek at the next item in the queue without removing it.

        Args:
            block (bool): If True, blocks until an item is available.
            timeout (Optional[float]): If block is True, specifies the
                                       maximum time to wait.

        Returns:
            Any: The next item in the queue without removing it.

        Raises:
            Empty: If the queue is empty.
        """
        if self._closed:
            raise ValueError(f"Queue {self!r} is closed.")

        if block and timeout is None:
            with self._rlock:
                res = self._recv_bytes()
        else:
            if block:
                deadline = time.monotonic() + timeout
            if not self._rlock.acquire(block, timeout):
                raise Empty
            try:
                if block:
                    timeout = deadline - time.monotonic()
                    if not self._poll(timeout):
                        raise Empty
                elif not self._poll():
                    raise Empty

                res = self._recv_bytes()
            finally:
                self._rlock.release()

        # Unserialize the data after releasing the lock
        return _ForkingPickler.loads(res)
