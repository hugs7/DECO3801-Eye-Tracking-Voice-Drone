"""
Extends Queue to allow peeking at elements
without removing them from the queue.
Hugo Burton
11/10/2024
"""

from typing import Any, Optional
import time
from queue import Queue, Empty


class PeekableQueue(Queue):
    def peek(self, index: int = 0, block=True, timeout=None):
        """
        Peek at the next item in the queue without removing it.

        Args:
            index (int): The index of the item to peek at. Default is 0.
            block (bool): If True, block until an item is available.
            timeout (float or None): If block is True, wait for this amount of time.

        Returns:
            Any: The next item in the queue without removing it.

        Raises:
            Empty: If the queue is empty.
        """
        with self.not_empty:
            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time.time() + timeout
                while not self._qsize():
                    remaining = endtime - time.time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)

            item = self.queue[index]
            return item
