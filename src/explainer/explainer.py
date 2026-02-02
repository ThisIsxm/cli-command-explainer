# -*- coding: utf-8 -*-
from typing import List, Dict, Any, Optional

from ..parser import ParsedCommand
from ..risk import RiskAssessment, RiskLevel


class CommandExplanation:
    """命令解释结果"""

    def __init__(self):
        self.summary: str = ""
        self.description: str = ""
        self.purpose: str = ""
        self.parameters: List[str] = []
        self.examples: List[str] = []
        self.warnings: List[str] = []
        self.alternatives: List[str] = []
        self.language: str = "zh"

    def __repr__(self) -> str:
        return f"CommandExplanation(summary={self.summary[:50]}...)"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "summary": self.summary,
            "description": self.description,
            "purpose": self.purpose,
            "parameters": self.parameters,
            "examples": self.examples,
            "warnings": self.warnings,
            "alternatives": self.alternatives,
            "language": self.language,
        }


class CommandExplainer:
    """命令解释器

    生成命令的详细解释和说明。

    使用方式：
        ```python
        explainer = CommandExplainer()
        parser = CommandParser()
        parsed = parser.parse("rm -rf node_modules")
        explanation = explainer.explain(parsed)
        ```
    """

    def __init__(self, language: str = "zh"):
        """
        Args:
            language: 语言设置 ("zh" 或 "en")
        """
        self.language = language
        self._command_database = self._get_command_database()

    def explain(self, parsed: ParsedCommand,
                risk_assessment: Optional[RiskAssessment] = None) -> CommandExplanation:
        """解释命令

        Args:
            parsed: 解析后的命令
            risk_assessment: 可选的风险评估结果

        Returns:
            CommandExplanation 对象
        """
        explanation = CommandExplanation()
        explanation.language = self.language

        # 获取命令的基础信息
        cmd_info = self._get_command_info(parsed.command)

        # 生成摘要
        explanation.summary = self._generate_summary(parsed, cmd_info)

        # 生成描述
        explanation.description = self._generate_description(parsed, cmd_info)

        # 生成用途
        explanation.purpose = self._generate_purpose(parsed, cmd_info)

        # 生成参数说明
        explanation.parameters = self._generate_parameters(parsed, cmd_info)

        # 生成示例
        explanation.examples = self._generate_examples(parsed, cmd_info)

        # 生成警告
        explanation.warnings = self._generate_warnings(parsed, cmd_info, risk_assessment)

        # 生成替代方案
        explanation.alternatives = self._generate_alternatives(parsed, cmd_info)

        return explanation

    def format_report(self, explanation: CommandExplanation,
                      risk_assessment: Optional[RiskAssessment] = None) -> str:
        """格式化完整报告

        Args:
            explanation: 解释结果
            risk_assessment: 可选的风险评估

        Returns:
            格式化的报告字符串
        """
        lines = []

        # 标题
        if self.language == "zh":
            lines.append("=" * 60)
            lines.append(f"命令解释: {explanation.summary}")
            lines.append("=" * 60)
        else:
            lines.append("=" * 60)
            lines.append(f"Command Explanation: {explanation.summary}")
            lines.append("=" * 60)

        lines.append("")

        # 用途
        if explanation.purpose:
            lines.append(explanation.purpose)
            lines.append("")

        # 详细描述
        if explanation.description:
            if self.language == "zh":
                lines.append("说明:")
            else:
                lines.append("Description:")
            for desc in explanation.description.split("\n"):
                lines.append(f"  {desc}")
            lines.append("")

        # 参数
        if explanation.parameters:
            if self.language == "zh":
                lines.append("参数:")
            else:
                lines.append("Parameters:")
            for param in explanation.parameters:
                lines.append(f"  {param}")
            lines.append("")

        # 风险警告
        if risk_assessment:
            emoji = risk_assessment.level.get_emoji()
            level_name = risk_assessment.level.get_display_name(self.language)
            if self.language == "zh":
                lines.append(f"{emoji} 风险等级: {level_name}")
            else:
                lines.append(f"{emoji} Risk Level: {level_name}")
            lines.append("")

        # 警告信息
        if explanation.warnings:
            if self.language == "zh":
                lines.append("警告:")
            else:
                lines.append("Warnings:")
            for warning in explanation.warnings:
                lines.append(f"  {warning}")
            lines.append("")

        # 示例
        if explanation.examples:
            if self.language == "zh":
                lines.append("示例:")
            else:
                lines.append("Examples:")
            for example in explanation.examples:
                lines.append(f"  {example}")
            lines.append("")

        # 替代方案
        if explanation.alternatives:
            if self.language == "zh":
                lines.append("替代方案:")
            else:
                lines.append("Alternatives:")
            for alt in explanation.alternatives:
                lines.append(f"  {alt}")
            lines.append("")

        return "\n".join(lines)

    def _get_command_info(self, command: str) -> Dict:
        """获取命令的基础信息

        Args:
            command: 命令名称

        Returns:
            命令信息字典
        """
        return self._command_database.get(command, self._get_generic_info(command))

    def _get_generic_info(self, command: str) -> Dict:
        """获取通用命令信息（未知命令时使用）

        Args:
            command: 命令名称

        Returns:
            通用命令信息字典
        """
        if self.language == "zh":
            return {
                "name": command,
                "description": f"这是一个外部命令或自定义脚本: {command}",
                "purpose": "执行特定的系统操作或程序",
                "options": {},
                "examples": [],
                "warnings": ["请确保了解该命令的具体用途"],
                "alternatives": [f"{command} --help 查看所有选项"],
            }
        else:
            return {
                "name": command,
                "description": f"External command or script: {command}",
                "purpose": "Execute specific system operations or programs",
                "options": {},
                "examples": [],
                "warnings": ["Make sure you understand the command"],
                "alternatives": [f"{command} --help to view all options"],
            }

    def _generate_summary(self, parsed: ParsedCommand, cmd_info: Dict) -> str:
        """生成命令摘要

        Args:
            parsed: 解析后的命令
            cmd_info: 命令信息

        Returns:
            摘要字符串
        """
        full_cmd = parsed.get_full_command()
        if self.language == "zh":
            return f"执行 {full_cmd} - {cmd_info.get('description', '')}"
        else:
            return f"Execute {full_cmd} - {cmd_info.get('description', '')}"

    def _generate_description(self, parsed: ParsedCommand, cmd_info: Dict) -> str:
        """生成详细描述

        Args:
            parsed: 解析后的命令
            cmd_info: 命令信息

        Returns:
            描述字符串
        """
        desc = cmd_info.get("description", "")
        if not desc:
            return ""
        return desc

    def _generate_purpose(self, parsed: ParsedCommand, cmd_info: Dict) -> str:
        """生成用途

        Args:
            parsed: 解析后的命令
            cmd_info: 命令信息

        Returns:
            用途字符串
        """
        return cmd_info.get("purpose", "")

    def _generate_parameters(self, parsed: ParsedCommand, cmd_info: Dict) -> List[str]:
        """生成参数说明

        Args:
            parsed: 解析后的命令
            cmd_info: 命令信息

        Returns:
            参数列表
        """
        params = []

        # 选项
        for opt in parsed.options:
            opt_info = cmd_info.get("options", {}).get(opt, {})
            if opt_info:
                long_name = opt_info.get("long", "")
                desc = opt_info.get("desc", "")
                if self.language == "zh":
                    params.append(f"-{opt} (--{long_name}): {desc}")
                else:
                    params.append(f"-{opt} (--{long_name}): {desc}")
            else:
                if self.language == "zh":
                    params.append(f"-{opt}: 选项")
                else:
                    params.append(f"-{opt}: Option")

        # 参数
        for arg in parsed.arguments:
            if not arg.startswith("-"):
                if self.language == "zh":
                    params.append(f"<{arg}>: 参数")
                else:
                    params.append(f"<{arg}>: Parameter")

        return params

    def _generate_examples(self, parsed: ParsedCommand, cmd_info: Dict) -> List[str]:
        """生成示例

        Args:
            parsed: 解析后的命令
            cmd_info: 命令信息

        Returns:
            示例列表
        """
        examples = []
        cmd_examples = cmd_info.get("examples", [])
        if cmd_examples:
            examples.extend(cmd_examples)
        else:
            # 通用示例
            if self.language == "zh":
                examples.append(f"{parsed.command} --help # 查看帮助")
            else:
                examples.append(f"{parsed.command} --help # View help")

        return examples

    def _generate_warnings(self, parsed: ParsedCommand, cmd_info: Dict,
                         risk_assessment: Optional[RiskAssessment]) -> List[str]:
        """生成警告

        Args:
            parsed: 解析后的命令
            cmd_info: 命令信息
            risk_assessment: 风险评估

        Returns:
            警告列表
        """
        warnings = []
        cmd_warnings = cmd_info.get("warnings", [])
        if cmd_warnings:
            warnings.extend(cmd_warnings)

        # 添加风险相关警告
        if risk_assessment:
            if risk_assessment.level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                if self.language == "zh":
                    warnings.append("此命令可能造成数据丢失或系统损坏！")
                else:
                    warnings.append("This command may cause data loss or system damage!")

            for factor in risk_assessment.factors:
                if factor.weight > 0.7:
                    warnings.append(factor.description)

        return warnings

    def _generate_alternatives(self, parsed: ParsedCommand, cmd_info: Dict) -> List[str]:
        """生成替代方案

        Args:
            parsed: 解析后的命令
            cmd_info: 命令信息

        Returns:
            替代方案列表
        """
        alternatives = []
        cmd_alternatives = cmd_info.get("alternatives", [])
        if cmd_alternatives:
            alternatives.extend(cmd_alternatives)
        else:
            # 通用替代方案
            if self.language == "zh":
                alternatives.append("先在测试环境验证命令")
            else:
                alternatives.append("Test the command in a safe environment first")

        return alternatives

    def _get_command_database(self) -> Dict:
        """获取命令数据库

        Returns:
            命令信息字典
        """
        if self.language == "zh":
            db = {
                # 文件操作
                "rm": {
                    "name": "rm",
                    "description": "删除文件或目录",
                    "purpose": "永久删除指定的文件或目录",
                    "options": {
                        "r": {"long": "recursive", "desc": "递归删除目录及其内容"},
                        "f": {"long": "force", "desc": "强制删除，不提示确认"},
                        "i": {"long": "interactive", "desc": "删除前逐一询问确认"},
                        "v": {"long": "verbose", "desc": "显示删除过程"},
                    },
                    "examples": [
                        "rm file.txt  # 删除文件",
                        "rm -rf directory  # 递归强制删除目录",
                        "rm -i file.txt  # 删除前确认",
                    ],
                    "warnings": [
                        "删除操作不可逆！",
                        "使用 -r 选项时请特别小心",
                        "建议先用 -i 选项确认",
                    ],
                    "alternatives": [
                        "使用 trash 命令移动到回收站",
                        "先用 ls 确认要删除的文件",
                    ],
                },
                "cp": {
                    "name": "cp",
                    "description": "复制文件或目录",
                    "purpose": "将文件或目录复制到指定位置",
                    "options": {
                        "r": {"long": "recursive", "desc": "递归复制目录"},
                        "v": {"long": "verbose", "desc": "显示复制过程"},
                        "i": {"long": "interactive", "desc": "覆盖前询问确认"},
                    },
                    "examples": [
                        "cp src.txt dest.txt  # 复制文件",
                        "cp -r src_dir dest_dir  # 递归复制目录",
                    ],
                    "warnings": ["目标文件存在时会被覆盖"],
                    "alternatives": [],
                },
                "mv": {
                    "name": "mv",
                    "description": "移动或重命名文件",
                    "purpose": "将文件移动到新位置或重命名",
                    "options": {
                        "v": {"long": "verbose", "desc": "显示移动过程"},
                        "i": {"long": "interactive", "desc": "覆盖前询问确认"},
                    },
                    "examples": [
                        "mv old.txt new.txt  # 重命名",
                        "mv file.txt /path/to/dest/  # 移动文件",
                    ],
                    "warnings": ["目标文件存在时会被覆盖"],
                    "alternatives": [],
                },
                "ls": {
                    "name": "ls",
                    "description": "列出目录内容",
                    "purpose": "显示当前目录下的文件和文件夹",
                    "options": {
                        "l": {"long": "long", "desc": "显示详细信息"},
                        "a": {"long": "all", "desc": "显示隐藏文件"},
                        "h": {"long": "human-readable", "desc": "以人类可读格式显示大小"},
                    },
                    "examples": [
                        "ls  # 列出当前目录",
                        "ls -la  # 显示所有文件的详细信息",
                        "ls -lh  # 显示文件大小",
                    ],
                    "warnings": [],
                    "alternatives": [],
                },
                "cat": {
                    "name": "cat",
                    "description": "显示文件内容",
                    "purpose": "在终端中输出文件内容",
                    "options": {
                        "n": {"long": "number", "desc": "显示行号"},
                    },
                    "examples": [
                        "cat file.txt  # 显示文件内容",
                        "cat -n file.txt  # 显示带行号的内容",
                    ],
                    "warnings": [],
                    "alternatives": [
                        "使用 less 命令分页查看大文件",
                        "使用 head/tail 查看文件开头/结尾",
                    ],
                },
                "chmod": {
                    "name": "chmod",
                    "description": "修改文件权限",
                    "purpose": "更改文件或目录的访问权限",
                    "examples": [
                        "chmod 755 script.sh  # 设置执行权限",
                        "chmod +x script.sh  # 添加执行权限",
                        "chmod -R 644 dir/  # 递归设置目录权限",
                    ],
                    "warnings": [
                        "修改系统文件权限可能导致系统异常",
                        "使用 -R 时请特别小心",
                    ],
                    "alternatives": [],
                },
                "chown": {
                    "name": "chown",
                    "description": "修改文件所有者",
                    "purpose": "更改文件或目录的所有者和组",
                    "examples": [
                        "chown user file.txt  # 修改所有者",
                        "chown -R user:group dir/  # 递归修改",
                    ],
                    "warnings": [
                        "需要管理员权限",
                        "修改系统文件可能引发问题",
                    ],
                    "alternatives": [],
                },
                "apt": {
                    "name": "apt",
                    "description": "Debian/Ubuntu 包管理器",
                    "purpose": "管理软件包的安装、更新和删除",
                    "options": {
                        "y": {"long": "yes", "desc": "自动确认"},
                    },
                    "examples": [
                        "apt update  # 更新软件源",
                        "apt install package  # 安装软件",
                        "apt remove package  # 卸载软件",
                    ],
                    "warnings": ["卸载软件可能影响依赖它的其他软件"],
                    "alternatives": [],
                },
                "yum": {
                    "name": "yum",
                    "description": "RHEL/CentOS 包管理器",
                    "purpose": "管理软件包的安装、更新和删除",
                    "examples": [
                        "yum update  # 更新所有软件",
                        "yum install package  # 安装软件",
                        "yum remove package  # 卸载软件",
                    ],
                    "warnings": ["需要管理员权限"],
                    "alternatives": [],
                },
                "curl": {
                    "name": "curl",
                    "description": "网络数据传输工具",
                    "purpose": "从服务器下载或上传数据",
                    "examples": [
                        "curl https://example.com  # 获取网页内容",
                        "curl -O https://example.com/file  # 下载文件",
                        "curl -X POST https://api.com/data  # POST 请求",
                    ],
                    "warnings": ["从网络下载文件可能包含恶意内容"],
                    "alternatives": [],
                },
                "wget": {
                    "name": "wget",
                    "description": "网络文件下载工具",
                    "purpose": "从网络下载文件",
                    "examples": [
                        "wget https://example.com/file.zip  # 下载文件",
                        "wget -c url  # 断点续传",
                        "wget -r url  # 递归下载",
                    ],
                    "warnings": [
                        "递归下载可能消耗大量带宽",
                        "下载文件前请验证来源",
                    ],
                    "alternatives": ["使用 curl 作为替代"],
                },
                "git": {
                    "name": "git",
                    "description": "分布式版本控制系统",
                    "purpose": "管理代码版本和协作开发",
                    "examples": [
                        "git clone url  # 克隆仓库",
                        "git pull  # 拉取更新",
                        "git push  # 推送更改",
                        "git commit -am 'message'  # 提交更改",
                    ],
                    "warnings": ["强制推送会覆盖远程历史"],
                    "alternatives": [],
                },
                "mkdir": {
                    "name": "mkdir",
                    "description": "创建目录",
                    "purpose": "创建新的目录",
                    "options": {
                        "p": {"long": "parents", "desc": "创建父目录"},
                        "v": {"long": "verbose", "desc": "显示创建过程"},
                    },
                    "examples": [
                        "mkdir newdir  # 创建目录",
                        "mkdir -p path/to/dir  # 创建多级目录",
                    ],
                    "warnings": [],
                    "alternatives": [],
                },
                "rmdir": {
                    "name": "rmdir",
                    "description": "删除空目录",
                    "purpose": "删除指定的空目录",
                    "examples": ["rmdir emptydir  # 删除空目录"],
                    "warnings": ["只能删除空目录"],
                    "alternatives": [],
                },
                "touch": {
                    "name": "touch",
                    "description": "创建空文件或更新时间戳",
                    "purpose": "创建新文件或更新文件访问时间",
                    "examples": ["touch newfile.txt  # 创建空文件"],
                    "warnings": [],
                    "alternatives": [],
                },
                "ln": {
                    "name": "ln",
                    "description": "创建链接",
                    "purpose": "创建文件或目录的链接",
                    "examples": [
                        "ln -s target link  # 创建符号链接",
                        "ln target hardlink  # 创建硬链接",
                    ],
                    "warnings": ["符号链接指向的文件被删除后链接会失效"],
                    "alternatives": [],
                },
            }
        else:
            db = {
                # File operations
                "r": {
                    "name": "rm",
                    "description": "Remove files or directories",
                    "purpose": "Permanently delete specified files or directories",
                    "options": {
                        "r": {"long": "recursive", "desc": "Remove directories and their contents recursively"},
                        "f": {"long": "force", "desc": "Force removal without confirmation"},
                        "i": {"long": "interactive", "desc": "Prompt before each removal"},
                        "v": {"long": "verbose", "desc": "Explain what is being done"},
                    },
                    "examples": [
                        "rm file.txt  # Remove a file",
                        "rm -rf directory  # Remove directory recursively and force",
                        "rm -i file.txt  # Confirm before removal",
                    ],
                    "warnings": [
                        "Deletion is irreversible!",
                        "Be careful with -r option",
                        "Consider using -i option to confirm",
                    ],
                    "alternatives": [
                        "Use trash command to move to recycle bin",
                        "Verify files with ls first",
                    ],
                },
                "cp": {
                    "name": "cp",
                    "description": "Copy files or directories",
                    "purpose": "Copy files or directories to a specified location",
                    "options": {
                        "r": {"long": "recursive", "desc": "Copy directories recursively"},
                        "v": {"long": "verbose", "desc": "Verbose output"},
                        "i": {"long": "interactive", "desc": "Prompt before overwrite"},
                    },
                    "examples": [
                        "cp src.txt dest.txt  # Copy a file",
                        "cp -r src_dir dest_dir  # Copy directory recursively",
                    ],
                    "warnings": ["Existing destination files will be overwritten"],
                    "alternatives": [],
                },
                "mv": {
                    "name": "mv",
                    "description": "Move or rename files",
                    "purpose": "Move files to new location or rename them",
                    "options": {
                        "v": {"long": "verbose", "desc": "Verbose output"},
                        "i": {"long": "interactive", "desc": "Prompt before overwrite"},
                    },
                    "examples": [
                        "mv old.txt new.txt  # Rename file",
                        "mv file.txt /path/to/dest/  # Move file",
                    ],
                    "warnings": ["Existing destination files will be overwritten overwritten"],
                    "alternatives": [],
                },
                "ls": {
                    "name": "ls",
                    "description": "List directory contents",
                    "purpose": "Display files and folders in current directory",
                    "options": {
                        "l": {"long": "long", "desc": "Long format with details"},
                        "a": {"long": "all", "desc": "Show hidden files"},
                        "h": {"long": "human-readable", "desc": "Human readable file sizes"},
                    },
                    "examples": [
                        "ls  # List current directory",
                        "ls -la  # List all files with details",
                        "ls -lh  # List with human readable sizes",
                    ],
                    "warnings": [],
                    "alternatives": [],
                },
                "cat": {
                    "name": "cat",
                    "description": "Display file contents",
                    "purpose": "Output file contents to terminal",
                    "options": {
                        "n": {"long": "number", "desc": "Number output lines"},
                    },
                    "examples": [
                        "cat file.txt  # Display file contents",
                        "cat -n file.txt  # Display with line numbers",
                    ],
                    "warnings": [],
                    "alternatives": [
                        "Use less command to page through large files",
                        "Use head/tail to view beginning/end",
                    ],
                },
                "chmod": {
                    "name": "chmod",
                    "description": "Change file permissions",
                    "purpose": "Change access permissions for files or directories",
                    "examples": [
                        "chmod 755 script.sh  # Set execute permission",
                        "chmod +x script.sh  # Add execute permission",
                        "chmod -R 644 dir/  # Set directory permissions recursively",
                    ],
                    "warnings": [
                        "Modifying system file permissions may cause issues",
                        "Be careful with -R option",
                    ],
                    "alternatives": [],
                },
                "chown": {
                    "name": "chown",
                    "description": "Change file owner",
                    "purpose": "Change owner and group of files or directories",
                    "examples": [
                        "chown user file.txt  # Change owner",
                        "chown -R user:group dir/  # Change recursively",
                    ],
                    "warnings": [
                        "Requires admin privileges",
                        "Modifying system files may cause problems",
                    ],
                    "alternatives": [],
                },
                "apt": {
                    "name": "apt",
                    "description": "Debian/Ubuntu package manager",
                    "purpose": "Manage package installation, updates, and removal",
                    "options": {
                        "y": {"long": "yes", "desc": "Auto-confirm"},
                    },
                    "examples": [
                        "apt update  # Update package list",
                        "apt install package  # Install software",
                        "apt remove package  # Remove software",
                    ],
                    "warnings": ["Removing packages may affect dependent software"],
                    "alternatives": [],
                },
                "yum": {
                    "name": "yum",
                    "description": "RHEL/CentOS package manager",
                    "purpose": "Manage package installation, updates, and removal",
                    "examples": [
                        "yum update  # Update all packages",
                        "yum install package  # Install software",
                        "yum remove package  # Remove software",
                    ],
                    "warnings": ["Requires admin privileges"],
                    "alternatives": [],
                },
                "curl": {
                    "name": "curl",
                    "description": "Network data transfer tool",
                    "purpose": "Download or upload data from/to servers",
                    "examples": [
                        "curl https://example.com  # Get web page content",
                        "curl -O https://example.com/file  # Download file",
                        "curl -X POST https://api.com/data  # POST request",
                    ],
                    "warnings": ["Downloaded files may contain malicious content"],
                    "alternatives": [],
                },
                "wget": {
                    "name": "wget",
                    "description": "Network file downloader",
                    "purpose": "Download files from the web",
                    "examples": [
                        "wget https://example.com/file.zip  # Download file",
                        "wget -c url  # Continue interrupted download",
                        "wget -r url  # Recursive download",
                    ],
                    "warnings": [
                        "Recursive download may consume lots of bandwidth",
                        "Verify source before downloading",
                    ],
                    "alternatives": ["Use curl as alternative"],
                },
                "git": {
                    "name": "git",
                    "description": "Distributed version control system",
                    "purpose": "Manage code versions and collaborative development",
                    "examples": [
                        "git clone url  # Clone repository",
                        "git pull  # Pull updates",
                        "git push  # Push changes",
                        "git commit -am 'message'  # Commit changes",
                    ],
                    "warnings": ["Force push will overwrite remote history"],
                    "alternatives": [],
                },
                "mkdir": {
                    "name": "mkdir",
                    "description": "Create directories",
                    "purpose": "Create new directories",
                    "options": {
                        "p": {"long": "parents", "desc": "Create parent directories"},
                        "v": {"long": "verbose", "desc": "Verbose output"},
                    },
                    "examples": [
                        "mkdir newdir  # Create directory",
                        "mkdir -p path/to/dir  # Create nested directories",
                    ],
                    "warnings": [],
                    "alternatives": [],
                },
                "rmdir": {
                    "name": "rmdir",
                    "description": "Remove empty directories",
                    "purpose": "Remove specified empty directories",
                    "examples": ["rmdir emptydir  # Remove empty directory"],
                    "warnings": ["Only works on empty directories"],
                    "alternatives": [],
                },
                "touch": {
                    "name": "touch",
                    "description": "Create empty files or update timestamps",
                    "purpose": "Create new files or update file access time",
                    "examples": ["touch newfile.txt  # Create empty file"],
                    "warnings": [],
                    "alternatives": [],
                },
                "ln": {
                    "name": "ln",
                    "description": "Create links",
                    "purpose": "Create links to files or directories",
                    "examples": [
                        "ln -s target link  # Create symbolic link",
                        "ln target hardlink  # Create hard link",
                    ],
                    "warnings": ["Symbolic links become invalid if target is deleted"],
                    "alternatives": [],
                },
            }
        return db

    def quick_explain(self, command: str) -> Dict:
        """快速解释命令（便捷方法）

        Args:
            command: 命令字符串

        Returns:
            包含解释信息的字典
        """
        from ..parser import CommandParser
        from ..risk import RiskAssessor

        parser = CommandParser()
        parsed = parser.parse(command)
        assessor = RiskAssessor(self.language)
        assessment = assessor.assess(parsed)
        explanation = self.explain(parsed, assessment)

        return {
            "summary": explanation.summary,
            "purpose": explanation.purpose,
            "risk_level": assessment.level.value,
            "risk_score": assessment.score,
            "recommendation": assessment.recommendation,
        }
