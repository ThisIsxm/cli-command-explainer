# -*- coding: utf-8 -*-
from typing import Callable, Optional
import keyboard
import threading

from .base import CaptureEvent


class HotkeyManager:
    """全局快捷键管理器

    监听系统全局快捷键，按下时触发回调。

    注意: 需要以管理员权限运行才能监听全局快捷键。

    使用方式：
        ```python
        manager = HotkeyManager()

        def on_hotkey():
            print("Hotkey pressed!")

        manager.register("ctrl+shift+e", on_hotkey)
        manager.start_listening()
        # ...
        manager.stop_listening()
        ```
    """

    def __init__(self) -> None:
        self._hotkey: Optional[str] = None
        self._callback: Optional[Callable[[], None]] = None
        self._is_listening = False
        self._thread: Optional[threading.Thread] = None

    def register(self, key_combo: str, callback: Callable[[], None]) -> None:
        """注册快捷键

        Args:
            key_combo: 快捷键组合，如 "ctrl+shift+e"
            callback: 按下快捷键时调用的函数
        """
        self._hotkey = key_combo
        self._callback = callback

    def start_listening(self) -> None:
        """开始监听快捷键"""
        if self._is_listening:
            raise RuntimeError("Hotkey manager is already listening")

        if not self._hotkey or not self._callback:
            raise ValueError("No hotkey registered")

        try:
            self._is_listening = True
            keyboard.add_hotkey(self._hotkey, self._callback)
        except Exception as e:
            self._is_listening = False
            raise RuntimeError(f"Failed to register hotkey: {e}")

    def stop_listening(self) -> None:
        """停止监听快捷键"""
        if self._is_listening and self._hotkey:
            try:
                keyboard.remove_hotkey(self._hotkey)
            except Exception:
                pass  # 忽略移除热键时的错误
        self._is_listening = False

    @property
    def is_listening(self) -> bool:
        """检查是否正在监听"""
        return self._is_listening

    @property
    def registered_hotkey(self) -> Optional[str]:
        """获取已注册的快捷键"""
        return self._hotkey

    def __enter__(self):
        """支持上下文管理器协议"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动停止监听"""
        self.stop_listening()
        return False

    def __repr__(self) -> str:
        return f"HotkeyManager(hotkey={self._hotkey!r}, listening={self._is_listening})"


def create_integrated_capturer(hotkey_combo: str, capturer_callback: Callable[[CaptureEvent], None]) -> tuple[HotkeyManager, Callable[[], None]]:
    """创建集成的快捷键+剪贴板捕获器

    Args:
        hotkey_combo: 快捷键组合
        capturer_callback: 捕获到命令时的回调函数

    Returns:
        (HotkeyManager实例, 快捷键触发函数)
    """
    from .clipboard import ClipboardCapturer

    clipboard_capturer = ClipboardCapturer()

    def on_hotkey():
        """热键回调函数

        捕获剪贴板内容并调用回调函数
        """
        try:
            # 如果没有运行，先启动（只会在第一次调用时启动）
            if not clipboard_capturer._is_running:
                clipboard_capturer.start(capturer_callback)

            # 捕获剪贴板内容并触发
            clipboard_capturer.capture_and_trigger()

        except Exception as e:
            import logging
            logging.error(f"热键回调出错: {e}")

    hotkey_manager = HotkeyManager()
    hotkey_manager.register(hotkey_combo, on_hotkey)

    return hotkey_manager, on_hotkey