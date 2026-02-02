# -*- coding: utf-8 -*-
"""命令解析器单元测试"""

import pytest

from src.parser import CommandParser, ParsedCommand, CommandPart


class TestCommandParser:
    """命令解析器测试"""

    def test_parse_simple_command(self):
        """测试简单命令解析"""
        parser = CommandParser()
        parsed = parser.parse("ls")

        assert parsed.command == "ls"
        assert len(parsed.options) == 0
        assert len(parsed.arguments) == 0
        assert parsed.original == "ls"

    def test_parse_command_with_combined_options(self):
        """测试带组合选项的命令解析（如 -la）"""
        parser = CommandParser()
        parsed = parser.parse("ls -la")

        assert parsed.command == "ls"
        # -la 被视为一个组合选项
        assert parsed.options == ["-la"]
        assert len(parsed.arguments) == 0

    def test_parse_command_with_separate_options(self):
        """测试带独立选项的命令解析"""
        parser = CommandParser()
        parsed = parser.parse("ls -l -a")

        assert parsed.command == "ls"
        assert parsed.options == ["-l", "-a"]
        assert len(parsed.arguments) == 0

    def test_parse_command_with_arguments(self):
        """测试带参数的命令解析"""
        parser = CommandParser()
        parsed = parser.parse("ls /home/user")

        assert parsed.command == "ls"
        assert len(parsed.options) == 0
        assert parsed.arguments == ["/home/user"]

    def test_parse_rm_rf(self):
        """测试 rm -rf 命令"""
        parser = CommandParser()
        parsed = parser.parse("rm -rf /tmp/test")

        assert parsed.command == "rm"
        assert parsed.options == ["-rf"]
        assert parsed.arguments == ["/tmp/test"]

    def test_parse_git_command(self):
        """测试 git 命令"""
        parser = CommandParser()
        parsed = parser.parse("git commit -am 'fix bug'")

        assert parsed.command == "git"
        assert parsed.options == ["-am"]
        assert parsed.arguments == ["fix bug"]

    def test_parse_npm_command(self):
        """测试 npm 命令"""
        parser = CommandParser()
        parsed = parser.parse("npm install lodash")

        assert parsed.command == "npm"
        assert parsed.options == []
        assert parsed.arguments == ["install", "lodash"]

    def test_parse_with_quotes(self):
        """测试带引号的参数"""
        parser = CommandParser()
        parsed = parser.parse('echo "hello world"')

        assert parsed.command == "echo"
        assert parsed.arguments == ["hello world"]

    def test_parse_with_long_option(self):
        """测试长选项"""
        parser = CommandParser()
        parsed = parser.parse("npm install --save lodash")

        assert parsed.command == "npm"
        assert parsed.options == ["--save"]
        assert parsed.arguments == ["install", "lodash"]

    def test_get_full_command(self):
        """测试获取完整命令"""
        parser = CommandParser()
        parsed = parser.parse("rm -rf /tmp/test")

        full = parsed.get_full_command()
        assert full == "rm -rf /tmp/test"

    def test_empty_command(self):
        """测试空命令"""
        parser = CommandParser()
        parsed = parser.parse("")

        assert parsed.command == ""
        assert len(parsed.options) == 0
        assert len(parsed.arguments) == 0

    def test_has_option(self):
        """测试检查选项是否存在"""
        parser = CommandParser()
        parsed = parser.parse("rm -rf /tmp")

        assert parsed.has_option("-rf") == True
        assert parsed.has_option("-r") == True
        assert parsed.has_option("-f") == True
        assert parsed.has_option("-a") == False

    def test_get_argument_at(self):
        """测试获取指定位置的参数"""
        parser = CommandParser()
        parsed = parser.parse("npm install lodash")

        assert parsed.get_argument_at(0) == "install"
        assert parsed.get_argument_at(1) == "lodash"
        assert parsed.get_argument_at(2) == None


class TestCommandPart:
    """命令组成部分测试"""

    def test_command_part_creation(self):
        """测试命令部分创建"""
        part = CommandPart("ls", "command", "ls")

        assert part.value == "ls"
        assert part.type == "command"
        assert part.raw == "ls"

    def test_option_part_creation(self):
        """测试选项部分创建"""
        part = CommandPart("l", "option", "-l")

        assert part.value == "l"
        assert part.type == "option"
        assert part.raw == "-l"


class TestParsedCommands:
    """解析后命令对象测试"""

    def test_subcommand_extraction(self):
        """测试子命令提取"""
        parser = CommandParser()
        parsed = parser.parse("npm install lodash")

        assert parsed.command == "npm"
        assert parsed.subcommand == "install"
