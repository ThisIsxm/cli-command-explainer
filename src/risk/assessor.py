# -*- coding: utf-8 -*-
from typing import List, Dict, Optional
from enum import Enum

from ..parser import ParsedCommand


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def get_emoji(self) -> str:
        """获取对应的 emoji"""
        emoji_map = {
            self.LOW: "",
            self.MEDIUM: "",
            self.HIGH: "",
            self.CRITICAL: "",
        }
        return emoji_map[self]

    def get_display_name(self, language: str = "zh") -> str:
        """获取显示名称"""
        names = {
            "zh": {
                "low": "低风险",
                "medium": "中风险",
                "high": "高风险",
                "critical": "危险",
            },
            "en": {
                "low": "Low Risk",
                "medium": "Medium Risk",
                "high": "High Risk",
                "critical": "Critical",
            },
        }
        return names.get(language, names["zh"]).get(self.value, self.value)


class RiskFactor:
    """风险因素"""

    def __init__(self, name: str, description: str, weight: float = 1.0):
        """
        Args:
            name: 风险因素名称
            description: 描述
            weight: 权重 (0-1)
        """
        self.name = name
        self.description = description
        self.weight = weight

    def __repr__(self) -> str:
        return f"RiskFactor(name={self.name!r}, weight={self.weight})"


class RiskAssessment:
    """风险评估结果"""

    def __init__(self):
        self.level: RiskLevel = RiskLevel.LOW
        self.factors: List[RiskFactor] = []
        self.score: float = 0.0
        self.max_score: float = 100.0
        self.recommendation: str = ""
        self.detailed_analysis: str = ""

    def __repr__(self) -> str:
        return (f"RiskAssessment(level={self.level}, "
                f"score={self.score}, factors={len(self.factors)})")


class RiskAssessor:
    """风险评估器

    综合评估命令的风险等级。

    使用方式：
        ```python
        assessor = RiskAssessor()
        parser = CommandParser()
        parsed = parser.parse("rm -rf node_modules")
        assessment = assessor.assess(parsed)

        print(assessment.level)  # RiskLevel.HIGH
        print(assessment.score)  # 75.0
        ```
    """

    # 风险等级阈值
    RISK_THRESHOLDS = {
        RiskLevel.LOW: 25,
        RiskLevel.MEDIUM: 50,
        RiskLevel.HIGH: 75,
        RiskLevel.CRITICAL: 90,
    }

    # 风险因素权重
    RISK_WEIGHTS = {
        "file_deletion": 0.8,
        "system_modification": 0.7,
        "network_operation": 0.3,
        "elevated_privileges": 0.6,
        "irreversible": 0.9,
        "batch_operation": 0.7,
        "sensitive_path": 0.6,
    }

    def __init__(self, language: str = "zh"):
        """
        Args:
            language: 语言设置 ("zh" 或 "en")
        """
        self.language = language

    def assess(self, parsed: ParsedCommand) -> RiskAssessment:
        """评估命令风险

        Args:
            parsed: 解析后的命令

        Returns:
            RiskAssessment 对象
        """
        assessment = RiskAssessment()
        assessment.factors = self._get_risk_factors(parsed)

        # 计算总分
        total_weight = sum(f.weight * self.RISK_WEIGHTS.get(f.name, 0.5)
                          for f in assessment.factors)

        if assessment.factors:
            # 归一化到 0-100
            assessment.score = min(100.0, total_weight * 30)
        else:
            assessment.score = 0.0

        # 确定风险等级
        assessment.level = self._calculate_risk_level(assessment.score)

        # 生成建议
        assessment.recommendation = self._get_recommendation(assessment.level.value)

        # 生成详细分析
        factors_desc = "\n".join([f"  - {f.description}" for f in assessment.factors])
        if self.language == "zh":
            assessment.detailed_analysis = (
                f"风险分数: {assessment.score:.1f}/100\n"
                f"风险因素:\n{factors_desc if factors_desc else '  无'}\n"
                f"建议: {assessment.recommendation}"
            )
        else:
            assessment.detailed_analysis = (
                f"Risk Score: {assessment.score:.1f}/100\n"
                f"Risk Factors:\n{factors_desc if factors_desc else '  None'}\n"
                f"Recommendation: {assessment.recommendation}"
            )

        return assessment

    def _calculate_risk_level(self, score: float) -> RiskLevel:
        """根据分数计算风险等级

        Args:
            score: 风险分数

        Returns:
            RiskLevel 枚举值
        """
        if score >= self.RISK_THRESHOLDS[RiskLevel.CRITICAL]:
            return RiskLevel.CRITICAL
        elif score >= self.RISK_THRESHOLDS[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        elif score >= self.RISK_THRESHOLDS[RiskLevel.MEDIUM]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _get_recommendation(self, level: str) -> str:
        """获取执行建议

        Args:
            level: 风险等级

        Returns:
            建议文本
        """
        recommendations = {
            "zh": {
                "low": "此命令是只读操作，可以安全执行。",
                "medium": "此命令会修改文件或系统，建议先检查参数。",
                "high": "此命令存在较高风险，请仔细确认后再执行。",
                "critical": "此命令可能导致严重后果，强烈建议不要执行！",
            },
            "en": {
                "low": "This is a read-only operation, safe to execute.",
                "medium": "This command modifies files or system, review parameters first.",
                "high": "This command has significant risk, confirm carefully before execution.",
                "critical": "This command may cause serious damage, do NOT execute!",
            },
        }
        return recommendations.get(self.language, recommendations["zh"]).get(
            level, "Please review carefully."
        )

    def _get_risk_factors(self, parsed: ParsedCommand) -> List[RiskFactor]:
        """获取命令的风险因素

        Args:
            parsed: 解析后的命令

        Returns:
            RiskFactor 列表
        """
        factors = []
        cmd = parsed.command
        full_cmd = parsed.get_full_command()

        # 检查文件删除
        if self._has_file_deletion(parsed):
            weight = 0.9 if "-rf" in parsed.original or "-r" in parsed.options else 0.6
            factors.append(RiskFactor(
                "file_deletion",
                "包含文件删除操作",
                weight
            ))

        # 检查系统修改
        if self._has_system_modification(cmd):
            factors.append(RiskFactor(
                "system_modification",
                "修改系统配置或权限",
                0.7
            ))

        # 检查网络操作
        if self._has_network_operation(parsed):
            factors.append(RiskFactor(
                "network_operation",
                "涉及网络操作，可能下载外部资源",
                0.3
            ))

        # 检查特权操作
        if self._has_elevated_privileges(parsed.original):
            factors.append(RiskFactor(
                "elevated_privileges",
                "使用管理员权限执行",
                0.6
            ))

        # 检查不可逆操作
        if self._is_irreversible(parsed):
            factors.append(RiskFactor(
                "irreversible",
                "操作不可逆或难以恢复",
                0.9
            ))

        # 检查批量操作
        if self._is_batch_operation(parsed):
            factors.append(RiskFactor(
                "batch_operation",
                "影响多个文件或对象",
                0.7
            ))

        # 检查敏感路径
        if self._has_sensitive_path(parsed.original):
            factors.append(RiskFactor(
                "sensitive_path",
                "涉及系统敏感路径",
                0.6
            ))

        return factors

    def _has_file_deletion(self, parsed: ParsedCommand) -> bool:
        """检查是否包含文件删除操作"""
        delete_commands = ["rm", "rmdir", "del", "erase"]
        return parsed.command in delete_commands

    def _has_system_modification(self, command: str) -> bool:
        """检查是否修改系统"""
        mod_commands = ["chmod", "chown", "mv", "cp", "mkdir", "ln",
                       "apt", "apt-get", "yum", "dnf", "pacman"]
        return command in mod_commands

    def _has_network_operation(self, parsed: ParsedCommand) -> bool:
        """检查是否包含网络操作"""
        net_commands = ["curl", "wget", "git", "ssh", "scp", "rsync", "npm", "pip"]
        if parsed.command in net_commands:
            return True
        # 检查参数中的 URL
        for arg in parsed.arguments:
            if arg.startswith("http://") or arg.startswith("https://"):
                return True
        return False

    def _has_elevated_privileges(self, original: str) -> bool:
        """检查是否使用特权"""
        elevated_patterns = ["sudo", "--sudo", "-S", "--admin", "--privileged"]
        return any(p in original for p in elevated_patterns)

    def _is_irreversible(self, parsed: ParsedCommand) -> bool:
        """检查是否不可逆"""
        if parsed.command == "rm":
            return True
        irreversible_options = ["--force", "-f", "--purge", "--delete"]
        return any(opt in parsed.options for opt in irreversible_options)

    def _is_batch_operation(self, parsed: ParsedCommand) -> bool:
        """检查是否批量操作"""
        batch_options = ["-r", "-R", "--recursive", "-f", "--force"]
        return any(opt in parsed.options for opt in batch_options)

    def _has_sensitive_path(self, original: str) -> bool:
        """检查是否涉及敏感路径"""
        sensitive_paths = [
            "/", "/root", "/home", "/etc", "/usr", "/var",
            "C:\\", "C:\\Windows", "C:\\Program Files",
        ]
        return any(path in original for path in sensitive_paths)

    def get_risk_level(self, parsed: ParsedCommand) -> RiskLevel:
        """获取风险等级（便捷方法）

        Args:
            parsed: 解析后的命令

        Returns:
            RiskLevel 枚举值
        """
        assessment = self.assess(parsed)
        return assessment.level

    def get_risk_factors(self, parsed: ParsedCommand) -> List[RiskFactor]:
        """获取命令的风险因素

        Args:
            parsed: 解析后的命令

        Returns:
            RiskFactor 列表
        """
        assessment = self.assess(parsed)
        return assessment.factors

    def format_risk_report(self, assessment: RiskAssessment) -> str:
        """格式化风险报告

        Args:
            assessment: 风险评估结果

        Returns:
            格式化的报告字符串
        """
        emoji = assessment.level.get_emoji()
        level_name = assessment.level.get_display_name(self.language)

        if self.language == "zh":
            return f"{emoji} 风险等级: {level_name}\n{assessment.detailed_analysis}"
        else:
            return f"{emoji} Risk Level: {level_name}\n{assessment.detailed_analysis}"

    def quick_assess(self, command: str) -> Dict:
        """快速评估命令（便捷方法）

        Args:
            command: 命令字符串

        Returns:
            包含风险信息的字典
        """
        from ..parser import CommandParser

        parser = CommandParser()
        parsed = parser.parse(command)
        assessment = self.assess(parsed)

        return {
            "level": assessment.level.value,
            "score": assessment.score,
            "recommendation": assessment.recommendation,
            "factors": [{"name": f.name, "description": f.description} for f in assessment.factors],
        }
