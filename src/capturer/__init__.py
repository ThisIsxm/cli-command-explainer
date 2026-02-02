# -*- coding: utf-8 -*-
from .base import BaseCapturer, CaptureEvent
from .clipboard import ClipboardCapturer
from .hotkey import HotkeyManager, create_integrated_capturer

__all__ = [
    "BaseCapturer",
    "CaptureEvent",
    "ClipboardCapturer",
    "HotkeyManager",
    "create_integrated_capturer",
]