# -*- coding: utf-8 -*-
import re
from typing import List, Tuple


class PatternMatcher:
    """命令模式匹配器

    用于识别危险命令模式和高风险操作。

    使用方式：
        ```python
        matcher = PatternMatcher()

        result = matcher.match("rm -rf /")
        print(result.is_dangerous)  # True
        print(result.risk_level)      # "critical"
        print(result.matched_patterns)  # ["rm -rf .*"]
        ```
    """

    # 危险命令模式（按风险等级分类）
    CRITICAL_PATTERNS = [
        r"rm\s+-rf\s+\/",           # rm -rf / （删除根目录）
        r"rm\s+-rf\s+\.",           # rm -rf . （删除当前目录）
        r":\(;\)\s*:(){ :\|:&\s*};:", # fork bomb
        r"dd\s+if=/dev/zero",       # dd 写零到磁盘
        r"mkfs\.",                  # 格式化文件系统
        r"chmod\s+777\s+\/",        # chmod 777 根目录
        r"chmod\s+777\s+-R",        # 递归 chmod 777
        r"chown\s+-R",              # 递归 chown
        r"sudo\s+rm\s+-rf",         # sudo 删除
        r"format\s+[a-zA-Z]:",      # Windows format 命令
        r"del\s+\/[s/q]",          # Windows 递归删除
        r"shutdown\s+\/[sft]",      # Windows 关机
    ]

    HIGH_RISK_PATTERNS = [
        r"rm\s+-rf",               # rm -rf
        r"rm\s+-r",                # rm -r
        r"sudo\s+rm",              # sudo 删除
        r"rm\s+\/",                # 删除根目录下内容
        r"dd\s+",                  # dd 命令
        r"chmod\s+777",            # chmod 777
        r"chmod\s+000",            # chmod 000
        r">\s+\/dev/",            # 直接写入设备文件
        r"DROP\s+TABLE",           # SQL 删除表
        r"DELETE\s+FROM",           # SQL 删除数据
        r"TRUNCATE\s+TABLE",       # SQL 清空表
        r"UPDATE\s+.*\s+SET\s+.*\s+WHERE",  # SQL 更新（可能批量修改）
        r"git\s+push\s+--force",   # git force push
        r"git\s+reset\s+--hard",   # git hard reset
        r"docker\s+rm\s+-f",       # docker 强制删除容器
        r"docker\s+rmi\s+-f",      # docker 强制删除镜像
        r"pip\s+install\s+.*\s+--force-reinstall",  # pip 强制重装
        r"npm\s+install\s+.*\s+--force",  # npm 强制安装
    ]

    MEDIUM_RISK_PATTERNS = [
        r"rm\s+",                  # rm 删除命令
        r"mv\s+",                  # mv 移动命令
        r"cp\s+",                  # cp 复制命令
        r"mkdir\s+",               # mkdir 创建目录
        r"rmdir\s+",               # rmdir 删除空目录
        r"touch\s+",               # touch 创建文件
        r"chmod\s+",               # chmod 修改权限
        r"chown\s+",               # chown 修改所有者
        r"ln\s+-[sf]",            # ln 创建软/硬链接
        r"sudo\s+(apt|yum|dnf)\s+(install|remove|upgrade)",  # 包管理器操作
        r"pip\s+install\s+",       # pip 安装包
        r"pip\s+uninstall\s+",     # pip 卸载包
        r"npm\s+install\s+-g",     # npm 全局安装
        r"npm\s+uninstall\s+",    # npm 卸载包
        r"yarn\s+install\s+-g",    # yarn 全局安装
        r"docker\s+run\s+--privileged",  # docker 特权模式
        r"kubectl\s+delete\s+",    # kubectl 删除资源
        r"kubectl\s+apply\s+",     # kubectl 应用配置
        r"curl\s+\|\s+sh",        # curl | sh（直接执行远程脚本）
        r"wget\s+\|\s+sh",        # wget | sh
    ]

    # 危险关键词
    DANGEROUS_KEYWORDS = {
        "critical": [
            "rf", "force", "fork-bomb", "format", "dd", "mkfs",
            "777", "recursive", "shutdown",
        ],
        "high": [
            "rm", "drop", "truncate", "delete", "force",
            "reset", "hard", "purge", "autoremove",
        ],
        "medium": [
            "sudo", "chmod", "chown", "mv", "cp", "mkdir",
            "install", "uninstall", "upgrade", "apply",
        ],
    }

    # 敏感路径
    SENSITIVE_PATHS = [
        "/", "/root", "/home", "/etc", "/usr", "/var",
        "/boot", "/sys", "/proc", "/dev",
        r"C:\\", r"C:\\Windows", r"C:\\Program Files",
    ]

    # 网络操作关键词
    NETWORK_KEYWORDS = [
        "http://", "https://", "ftp://", "curl", "wget",
        "ssh", "scp", "rsync", "git", "clone",
    ]

    def __init__(self):
        # 编译正则表达式
        self._compiled_critical = [re.compile(p, re.IGNORECASE) for p in self.CRITICAL_PATTERNS]
        self._compiled_high = [re.compile(p, re.IGNORECASE) for p in self.HIGH_RISK_PATTERNS]
        self._compiled_medium = [re.compile(p, re.IGNORECASE) for p in self.MEDIUM_RISK_PATTERNS]
        self._compiled_sensitive = [re.compile(p, re.IGNORECASE) for p in self.SENSITIVE_PATHS]

    class MatchResult:
        """模式匹配结果"""

        def __init__(self):
            self.is_dangerous = False
            self.risk_level = "low"  # low, medium, high, critical
            self.matched_patterns: List[str] = []
            self.risk_factors: List[str] = []

        def __repr__(self) -> str:
            return (f"MatchResult(dangerous={self.is_dangerous}, "
                    f"level={self.risk_level}, patterns={len(self.matched_patterns)})")

    def match(self, command: str) -> "PatternMatcher.MatchResult":
        """匹配命令的模式

        Args:
            command: 命令字符串

        Returns:
            MatchResult 对象
        """
        result = self.MatchResult()

        # 检查各风险等级的模式
        for pattern in self._compiled_critical:
            if pattern.search(command):
                result.is_dangerous = True
                result.risk_level = "critical"
                result.matched_patterns.append(pattern.pattern)
                result.risk_factors.append("包含严重危险操作模式")

        if result.risk_level != "critical":
            for pattern in self._compiled_high:
                if pattern.search(command):
                    result.is_dangerous = True
                    result.risk_level = "high"
                    result.matched_patterns.append(pattern.pattern)
                    result.risk_factors.append("包含高风险操作")

        if result.risk_level not in ["critical", "high"]:
            for pattern in self._compiled_medium:
                if pattern.search(command):
                    result.is_dangerous = True
                    if result.risk_level == "low":
                        result.risk_level = "medium"
                    result.matched_patterns.append(pattern.pattern)
                    result.risk_factors.append("包含中风险操作")

        # 检查敏感路径
        if self._has_sensitive_path(command):
            result.is_dangerous = True
            if result.risk_level == "low":
                result.risk_level = "medium"
            result.risk_factors.append("涉及系统敏感路径")

        # 检查网络操作
        if self._has_network_operation(command):
            result.risk_factors.append("涉及网络操作")

        return result

    def get_risk_level(self, command: str) -> str:
        """获取命令的风险等级

        Args:
            command: 命令字符串

        Returns:
            风险等级: "low", "medium", "high", "critical"
        """
        result = self.match(command)
        return result.risk_level

    def _has_sensitive_path(self, command: str) -> bool:
        """检查命令是否包含敏感路径

        Args:
            command: 命令字符串

        Returns:
            如果包含敏感路径返回 True
        """
        for pattern in self._compiled_sensitive:
            if pattern.search(command):
                return True
        return False

    def _has_network_operation(self, command: str) -> bool:
        """检查命令是否包含网络操作

        Args:
            command: 命令字符串

        Returns:
            如果包含网络操作返回 True
        """
        for keyword in self.NETWORK_KEYWORDS:
            if keyword in command:
                return True
        return False

    def is_dangerous(self, command: str) -> bool:
        """快速检查命令是否危险

        Args:
            command: 命令字符串

        Returns:
            如果命令危险返回 True
        """
        result = self.match(command)
        return result.is_dangerous

    def get_command_categories(self, command: str) -> List[str]:
        """获取命令的分类

        Args:
            command: 命令字符串

        Returns:
            命令分类列表
        """
        categories = []

        if any(p in command for p in ["rm ", "rm\n", "rmdir"]):
            categories.append("delete")
        if any(p in command for p in ["cp ", "cp\n", "mv "]):
            categories.append("modify")
        if any(p in command for p in ["git"]):
            categories.append("version_control")
        if any(p in command for p in ["npm", "pip", "yarn", "cargo"]):
            categories.append("package_manager")
        if any(p in command for p in ["docker", "kubectl"]):
            categories.append("container")
        if "sudo" in command:
            categories.append("elevated")
        if any(p in command for p in ["http://", "https://", "curl", "wget"]):
            categories.append("network")

        if not categories:
            categories.append("other")

        return categories