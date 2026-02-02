# -*- coding: utf-8 -*-
from typing import Callable, Optional
import pyperclip

from .base import BaseCapturer, CaptureEvent


class ClipboardCapturer(BaseCapturer):
    """剪贴板捕获器

    从系统剪贴板读取内容并判断是否为命令。

    使用方式：
        ```python
        capturer = ClipboardCapturer()

        def on_capture(event: CaptureEvent):
            print(f"Got: {event.content}")

        capturer.start(on_capture)
        # 手动触发捕获
        capturer.capture_and_trigger()
        capturer.stop()
        ```
    """

    def __init__(self) -> None:
        super().__init__(name="clipboard")
        self._last_content: Optional[str] = None

    def start(self, callback: Callable[[CaptureEvent], None]) -> None:
        """启动剪贴板捕获

        Args:
            callback: 捕获到命令时的回调函数
        """
        if self._is_running:
            raise RuntimeError(f"{self.name} capturer is already running")

        self._callback = callback
        self._is_running = True

    def get_content(self) -> Optional[str]:
        """获取剪贴板内容

        Returns:
            剪贴板文本内容，如果获取失败返回 None
        """
        try:
            content = pyperclip.paste()
            if content and content.strip():
                return content.strip()
            return None
        except Exception as e:
            print(f"Error reading clipboard: {e}")
            return None

    def is_command(self, content: Optional[str]) -> bool:
        """判断内容是否为有效的命令

        改进点:
        1. 扩展命令列表以支持 ufw, systemctl 等常用命令
        2. 修复连字符检测逻辑，避免误判普通文本
        3. 添加更多命令特征检测

        Args:
            content: 要判断的内容

        Returns:
            如果内容看起来像一个命令返回 True
        """
        if not content:
            return False

        content = content.strip()

        # 过滤掉明显不是命令的内容
        if not content:
            return False

        # 包含换行符的多行文本通常不是单个命令
        if '\n' in content:
            return False

        # 分割第一个单词
        parts = content.split()
        if not parts:
            return False
        
        first_word = parts[0].lower()

        # === 1. 常见命令前缀检查（大幅扩展）===
        command_prefixes = [
            # 系统管理
            'sudo', 'su', 'doas',
            # 包管理
            'apt', 'apt-get', 'yum', 'dnf', 'pacman', 'zypper',
            'brew', 'choco', 'winget', 'scoop',
            # 开发工具
            'git', 'npm', 'yarn', 'pnpm', 'pip', 'pipenv', 'poetry',
            'cargo', 'go', 'rustc', 'gcc', 'clang', 'make', 'cmake',
            'docker', 'docker-compose', 'podman', 'kubectl', 'helm',
            'node', 'python', 'python3', 'ruby', 'php', 'java', 'javac',
            # 文件操作
            'ls', 'cd', 'pwd', 'cp', 'mv', 'rm', 'mkdir', 'rmdir',
            'cat', 'less', 'more', 'head', 'tail', 'touch', 'ln',
            'chmod', 'chown', 'chgrp',
            # 文本处理
            'grep', 'sed', 'awk', 'cut', 'sort', 'uniq', 'wc', 'tr',
            'find', 'locate', 'which', 'whereis',
            # 网络工具
            'curl', 'wget', 'ping', 'traceroute', 'netstat', 'ss',
            'ip', 'ifconfig', 'nslookup', 'dig', 'host',
            'ssh', 'scp', 'sftp', 'rsync', 'nc', 'telnet',
            # 系统信息
            'ps', 'top', 'htop', 'free', 'df', 'du', 'uname', 'hostname',
            'uptime', 'whoami', 'id', 'groups', 'last', 'w',
            # 压缩解压
            'tar', 'gzip', 'gunzip', 'zip', 'unzip', '7z', 'rar', 'unrar',
            # 防火墙/安全（修复：添加 ufw 等）
            'ufw', 'iptables', 'firewalld', 'firewall-cmd',
            'setenforce', 'getenforce', 'apparmor',
            # 服务管理（修复：添加 systemctl 等）
            'systemctl', 'service', 'systemd', 'journalctl',
            'rc-service', 'rc-update',
            # 无线网络
            'iwlist', 'iwconfig', 'iw', 'nmcli', 'nmtui',
            'wpa_supplicant', 'wpa_cli',
            # Windows命令
            'cmd', 'powershell', 'pwsh', 'wsl',
        ]

        # 检查第一个词是否是命令
        if first_word in command_prefixes:
            return True

        # === 2. 带空格的命令前缀（例如 'npm run'） ===
        command_starters_with_space = [
            'npm run', 'git commit', 'docker run', 'docker exec',
        ]
        for starter in command_starters_with_space:
            if content.startswith(starter):
                return True

        # === 3. 命令参数模式检查（更严格）===
        # 修复：只有当第二个词是参数时才认为可能是命令
        if len(parts) >= 2:
            second_word = parts[1]
            # 检查第二个词是否是标准参数格式
            if second_word.startswith('-') or second_word.startswith('--'):
                # 排除明显的非命令（如 "some-文本" 这种连字符分隔的普通文本）
                # 命令参数通常很短，且不含中文
                if len(second_word) <= 20 and not any('\u4e00' <= c <= '\u9fff' for c in second_word):
                    return True

        # === 4. 路径特征检查 ===
        # 包含 ./ 或 / 开头的可能是脚本
        if first_word.startswith('./') or first_word.startswith('/'):
            return True
        
        # Windows 路径
        if first_word.startswith('.\\') or (len(first_word) > 2 and first_word[1] == ':'):
            return True

        # === 5. 脚本文件扩展名 ===
        script_extensions = ['.sh', '.py', '.rb', '.pl', '.js', '.bat', '.cmd', '.ps1']
        if any(first_word.endswith(ext) for ext in script_extensions):
            return True

        return False

    def capture_and_trigger(self) -> bool:
        """捕获剪贴板内容并触发回调

        Returns:
            如果成功捕获并触发了回调返回 True
        """
        if not self._is_running or not self._callback:
            return False

        content = self.get_content()

        if content and self.is_command(content):
            # 避免重复捕获相同内容
            if content != self._last_content:
                self._last_content = content
                event = CaptureEvent(
                    content=content,
                    source=self.name,
                )
                self._callback(event)
                return True
            else:
                # 重复命令，给出提示
                from rich.console import Console
                console = Console()
                console.print(f"[dim]ℹ️  该命令已解释过: {content[:50]}...[/dim]" if len(content) > 50 else f"[dim]ℹ️  该命令已解释过: {content}[/dim]")
                console.print("[dim]💡 提示：如需重新解释，请复制其他内容后再复制此命令[/dim]\n")
        elif content:
            # 剪贴板内容不是命令，给出提示
            from rich.console import Console
            console = Console()
            console.print(f"[dim]ℹ️  剪贴板内容不像命令: {content[:50]}...[/dim]" if len(content) > 50 else f"[dim]ℹ️  剪贴板内容不像命令: {content}[/dim]")
            console.print("[dim]💡 提示：请确保复制的是命令文本，如 'ls -la' 或 'git status'[/dim]\n")

        return False

    def stop(self) -> None:
        """停止剪贴板捕获"""
        self._is_running = False
        self._callback = None
        self._last_content = None