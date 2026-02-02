# -*- coding: utf-8 -*-
from typing import Optional, List, Dict
import re


class CommandPart:
    """命令的一个组成部分"""

    def __init__(self, value: str, part_type: str, raw: str):
        """
        Args:
            value: 解析后的值（去引号等）
            part_type: 类型 (command, option, argument, pipe, redirect)
            raw: 原始字符串
        """
        self.value = value
        self.type = part_type
        self.raw = raw

    def __repr__(self) -> str:
        return f"CommandPart(type={self.type!r}, value={self.value!r})"


class ParsedCommand:
    """解析后的命令对象"""

    def __init__(self, original: str):
        """
        Args:
            original: 原始命令字符串
        """
        self.original = original.strip()
        self.command: str = ""
        self.subcommand: Optional[str] = None
        self.options: List[str] = []
        self.arguments: List[str] = []
        self.parts: List[CommandPart] = []
        self.command_type: str = "unknown"
        self.is_dangerous: bool = False
        self.danger_patterns: List[str] = []

    def __repr__(self) -> str:
        return (f"ParsedCommand(command={self.command!r}, subcommand={self.subcommand!r}, "
                f"options={self.options!r}, arguments={self.arguments!r})")

    def get_full_command(self) -> str:
        """获取完整命令名（包含子命令）"""
        if self.subcommand:
            return f"{self.command} {self.subcommand}"
        return self.command

    def has_option(self, option: str) -> bool:
        """检查是否包含特定选项"""
        return any(opt in self.options for opt in [option, option.lstrip("-")])

    def get_argument_at(self, index: int) -> Optional[str]:
        """获取指定位置的参数"""
        if 0 <= index < len(self.arguments):
            return self.arguments[index]
        return None


class CommandParser:
    """命令解析器

    解析命令字符串，识别命令类型、参数、选项等。

    使用方式：
        ```python
        parser = CommandParser()
        parsed = parser.parse("npm install --save lodash")

        print(parsed.command)      # npm
        print(parsed.options)       # ['--save']
        print(parsed.arguments)      # ['lodash']
        print(parsed.command_type)   # npm
        ```
    """

    # 命令类型识别模式
    COMMAND_PATTERNS = {
        "git": re.compile(r"^\s*git\s"),
        "npm": re.compile(r"^\s*npm\s"),
        "yarn": re.compile(r"^\s*yarn\s"),
        "pnpm": re.compile(r"^\s*pnpm\s"),
        "pip": re.compile(r"^\s*pip\s+|^pip3\s+"),
        "pip3": re.compile(r"^\s*pip3\s+"),
        "python": re.compile(r"^\s*python\s+|^python3\s+"),
        "python3": re.compile(r"^\s*python3\s+"),
        "node": re.compile(r"^\s*node\s"),
        "docker": re.compile(r"^\s*docker\s"),
        "docker-compose": re.compile(r"^\s*docker-compose\s|^\s*docker\s+compose\s"),
        "kubectl": re.compile(r"^\s*kubectl\s"),
        "cargo": re.compile(r"^\s*cargo\s"),
        "go": re.compile(r"^\s*go\s"),
        "make": re.compile(r"^\s*make\s"),
        "cmake": re.compile(r"^\s*cmake\s"),
        "apt": re.compile(r"^\s*apt-get\s|^\s*apt\s"),
        "apt-get": re.compile(r"^\s*apt-get\s"),
        "yum": re.compile(r"^\s*yum\s"),
        "dnf": re.compile(r"^\s*dnf\s"),
        "curl": re.compile(r"^\s*curl\s"),
        "wget": re.compile(r"^\s*wget\s"),
        "tar": re.compile(r"^\s*tar\s"),
        "zip": re.compile(r"^\s*zip\s"),
        "unzip": re.compile(r"^\s*unzip\s"),
        "chmod": re.compile(r"^\s*chmod\s"),
        "chown": re.compile(r"^\s*chown\s"),
        "ls": re.compile(r"^\s*ls\s+|^ls$"),
        "cd": re.compile(r"^\s*cd\s+|^cd$"),
        "cp": re.compile(r"^\s*cp\s"),
        "mv": re.compile(r"^\s*mv\s"),
        "rm": re.compile(r"^\s*rm\s"),
        "mkdir": re.compile(r"^\s*mkdir\s"),
        "rmdir": re.compile(r"^\s*rmdir\s"),
        "cat": re.compile(r"^\s*cat\s"),
        "grep": re.compile(r"^\s*grep\s"),
        "find": re.compile(r"^\s*find\s"),
        "sed": re.compile(r"^\s*sed\s"),
        "awk": re.compile(r"^\s*awk\s"),
        "touch": re.compile(r"^\s*touch\s"),
        "ln": re.compile(r"^\s*ln\s"),
        "sudo": re.compile(r"^\s*sudo\s"),
    }

    # Shell 内置命令
    SHELL_COMMANDS = {"ls", "cd", "pwd", "clear", "exit", "history", "echo", "cat",
                     "grep", "find", "sed", "awk", "sort", "uniq", "wc", "head", "tail"}

    def __init__(self):
        pass

    def parse(self, command_str: str) -> ParsedCommand:
        """解析命令字符串

        Args:
            command_str: 要解析的命令字符串

        Returns:
            ParsedCommand 对象
        """
        result = ParsedCommand(command_str)
        command_str = command_str.strip()

        if not command_str:
            return result

        # 识别命令类型
        result.command_type = self._identify_type(command_str)

        # 解析命令各部分
        self._parse_parts(command_str, result)

        # 提取命令和子命令
        self._extract_command_and_subcommand(result)

        return result

    def _identify_type(self, command: str) -> str:
        """识别命令类型

        Args:
            command: 命令字符串

        Returns:
            命令类型标识符 (git, npm, pip, shell 等)
        """
        command = command.strip()

        # 首先检查 sudo
        if command.startswith("sudo "):
            rest = command[5:].strip()
            return self._identify_type(rest)

        for cmd_type, pattern in self.COMMAND_PATTERNS.items():
            if pattern.match(command):
                return cmd_type

        return "unknown"

    def _parse_parts(self, command: str, result: ParsedCommand) -> None:
        """解析命令的各个部分

        Args:
            command: 命令字符串
            result: ParsedCommand 对象（修改此对象）
        """
        # 简化的解析逻辑
        parts = shlex_split(command)

        for part in parts:
            if part.startswith("--"):
                # 长选项
                result.parts.append(CommandPart(part, "option", part))
                result.options.append(part)
            elif part.startswith("-"):
                # 短选项（可能组合）
                result.parts.append(CommandPart(part, "option", part))
                result.options.append(part)
            elif part in ["|", ">", ">>", "<", "&&", "||", ";"]:
                # 管道或重定向
                result.parts.append(CommandPart(part, "operator", part))
            else:
                # 参数或命令
                result.parts.append(CommandPart(part, "argument", part))
                result.arguments.append(part)

    def _extract_command_and_subcommand(self, result: ParsedCommand) -> None:
        """从 parts 中提取主命令和子命令

        Args:
            result: ParsedCommand 对象（修改此对象）
        """
        # 重置 arguments 列表
        result.arguments = []

        # 第一遍：提取主命令
        for part in result.parts:
            if part.type == "argument":
                if not result.command:
                    result.command = part.value
                    result.arguments.append(part.value)
                break  # 主命令找到，停止

        # 第二遍：提取子命令和剩余参数
        found_subcommand = False
        for part in result.parts:
            if part.type == "argument":
                if not result.subcommand and part.value not in [result.command]:
                    # 检查是否是子命令（不以 - 开头且不是文件路径）
                    if not part.value.startswith("/") and not part.value.startswith("-"):
                        result.subcommand = part.value
                        found_subcommand = True
                elif not found_subcommand:
                    # 子命令已找到后的参数
                    result.arguments.append(part.value)

        # 如果没有找到子命令，把主命令从 arguments 中移除
        if not result.subcommand and result.command in result.arguments:
            idx = result.arguments.index(result.command)
            result.arguments.pop(idx)

    def extract_args(self, command: str) -> Dict[str, List[str]]:
        """提取命令参数

        Args:
            command: 命令字符串

        Returns:
            包含 options 和 arguments 的字典
        """
        parsed = self.parse(command)
        return {
            "options": parsed.options,
            "arguments": parsed.arguments,
            "command": parsed.command,
            "subcommand": parsed.subcommand,
        }

    def is_shell_command(self, command: str) -> bool:
        """检查是否为 shell 内置命令

        Args:
            command: 命令字符串

        Returns:
            如果是 shell 命令返回 True
        """
        cmd_type = self._identify_type(command)
        return cmd_type in self.SHELL_COMMANDS


def shlex_split(s: str) -> List[str]:
    """简单的命令行分割函数

    处理引号和转义，类似 shlex.split() 的简化版本。

    Args:
        s: 要分割的字符串

    Returns:
        分割后的字符串列表
    """
    parts = []
    current = []
    in_quote = None  # None, ', "
    in_escape = False

    for char in s:
        if in_escape:
            current.append(char)
            in_escape = False
        elif char == "\\":
            in_escape = True
        elif in_quote:
            if char == in_quote:
                in_quote = None
                parts.append("".join(current))
                current = []
        elif char in ("\"", "'"):
            in_quote = char
        elif char.isspace():
            if current:
                parts.append("".join(current))
                current = []
        else:
            current.append(char)

    if current:
        parts.append("".join(current))

    return parts
