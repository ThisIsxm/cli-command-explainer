# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Callable, Optional, Any
import time

class CaptureEvent:
    def __init__(self, content: str, source: str, timestamp: float = None):
        self.content = content
        self.source = source
        self.timestamp = timestamp or time.time()

    def __repr__(self) -> str:
        return f"CaptureEvent(content={self.content!r}, source={self.source!r})"

class BaseCapturer(ABC):
    def __init__(self, name: str = "base") -> None:
        self.name = name
        self._is_running = False
        self._callback: Optional[Callable[[CaptureEvent], None]] = None

    @property
    def is_running(self) -> bool:
        return self._is_running

    @abstractmethod
    def start(self, callback: Callable[[CaptureEvent], None]) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False