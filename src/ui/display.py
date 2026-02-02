# -*- coding: utf-8 -*-
"""结果展示模块"""

import sys
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import box

from ..risk import RiskLevel, RiskAssessment


class ResultDisplay:
    """结果展示器

    使用 Rich 库进行格式化输出。
    """

    def __init__(self, language: str = "zh", show_emoji: bool = True):
        """
        Args:
            language: 语言设置 ("zh" 或 "en")
            show_emoji: 是否显示 emoji
        """
        # Windows 控制台强制使用 UTF-8
        if sys.platform == 'win32':
            import io
            self.console = Console(file=io.TextIOWrapper(
                sys.stdout.buffer, encoding='utf-8', errors='replace'
            ), legacy_windows=False, force_terminal=True)
            self.show_emoji = False
        else:
            self.console = Console()
            self.show_emoji = show_emoji

        self.language = language

    def display_explanation(
        self,
        command: str,
        explanation: Dict[str, Any],
        risk_assessment: Optional[RiskAssessment] = None,
    ):
        """展示命令解释结果

        Args:
            command: 命令字符串
            explanation: 解释结果字典
            risk_assessment: 风险评估结果（可选）
        """
        self.console.print()  # 空行

        # 标题
        title = self._get_text("command_explanation", "命令解释", "Command Explanation")
        self.console.print(f"[bold cyan]{title}[/bold cyan]")
        self.console.print()

        # 命令
        command_panel = Panel(
            f"[yellow]{command}[/yellow]",
            title=self._get_text("command", "命令", "Command"),
            border_style="yellow",
        )
        self.console.print(command_panel)
        self.console.print()

        # 概要
        if explanation.get("summary"):
            self.console.print(f"[bold]{self._get_text('summary', '概要', 'Summary')}:[/bold]")
            self.console.print(f"  {explanation['summary']}")
            self.console.print()

        # 详细说明
        if explanation.get("description"):
            self.console.print(f"[bold]{self._get_text('description', '详细说明', 'Description')}:[/bold]")
            self.console.print(f"  {explanation['description']}")
            self.console.print()

        # 用途
        if explanation.get("purpose"):
            self.console.print(f"[bold]{self._get_text('purpose', '用途', 'Purpose')}:[/bold]")
            self.console.print(f"  {explanation['purpose']}")
            self.console.print()

        # 参数说明
        if explanation.get("parameters"):
            self._display_parameters(explanation["parameters"])

        # 示例
        if explanation.get("examples"):
            self._display_examples(explanation["examples"])

        # 警告
        if explanation.get("warnings"):
            self._display_warnings(explanation["warnings"])

        # 替代方案
        if explanation.get("alternatives"):
            self._display_alternatives(explanation["alternatives"])

        # 风险评估
        if risk_assessment:
            self._display_risk_assessment(risk_assessment)
        elif explanation.get("risk_level"):
            self._display_risk_level(
                explanation.get("risk_level", "low"),
                explanation.get("risk_score", 0),
                explanation.get("recommendation", ""),
            )

    def _display_parameters(self, parameters: list):
        """展示参数说明"""
        self.console.print(
            f"[bold]{self._get_text('parameters', '参数说明', 'Parameters')}:[/bold]"
        )
        for param in parameters:
            if isinstance(param, dict):
                name = param.get("name", "")
                desc = param.get("description", "")
                self.console.print(f"  • [cyan]{name}[/cyan]: {desc}")
            else:
                self.console.print(f"  • {param}")
        self.console.print()

    def _display_examples(self, examples: list):
        """展示示例"""
        self.console.print(f"[bold]{self._get_text('examples', '示例', 'Examples')}:[/bold]")
        for example in examples:
            self.console.print(f"  [dim]$[/dim] [green]{example}[/green]")
        self.console.print()

    def _display_warnings(self, warnings: list):
        """展示警告"""
        warning_title = self._get_text('warnings', '警告', 'Warnings')
        if self.show_emoji:
            warning_title = f"⚠️  {warning_title}"
        self.console.print(f"[bold red]{warning_title}:[/bold red]")
        for warning in warnings:
            self.console.print(f"  • [yellow]{warning}[/yellow]")
        self.console.print()

    def _display_alternatives(self, alternatives: list):
        """展示替代方案"""
        self.console.print(
            f"[bold]{self._get_text('alternatives', '替代方案', 'Alternatives')}:[/bold]"
        )
        for alt in alternatives:
            self.console.print(f"  • [cyan]{alt}[/cyan]")
        self.console.print()

    def _display_risk_level(self, risk_level: str, risk_score: float, recommendation: str):
        """展示风险等级"""
        # 风险等级映射
        level_map = {
            "low": (RiskLevel.LOW, "green"),
            "medium": (RiskLevel.MEDIUM, "yellow"),
            "high": (RiskLevel.HIGH, "orange"),
            "critical": (RiskLevel.CRITICAL, "red"),
        }

        level, color = level_map.get(risk_level, (RiskLevel.LOW, "green"))
        emoji = level.get_emoji() if self.show_emoji else ""
        level_name = level.get_display_name(self.language)

        # 风险信息面板
        risk_text = f"{emoji} {level_name}\n"
        risk_text += f"{self._get_text('score', '评分', 'Score')}: {risk_score:.1f}/100\n"
        if recommendation:
            risk_text += f"\n{self._get_text('recommendation', '建议', 'Recommendation')}: {recommendation}"

        risk_panel = Panel(
            risk_text,
            title=self._get_text("risk_assessment", "风险评估", "Risk Assessment"),
            border_style=color,
            box=box.ROUNDED,
        )
        self.console.print(risk_panel)
        self.console.print()

    def _display_risk_assessment(self, assessment: RiskAssessment):
        """展示完整风险评估"""
        emoji = assessment.level.get_emoji() if self.show_emoji else ""
        level_name = assessment.level.get_display_name(self.language)

        # 颜色映射
        color_map = {
            RiskLevel.LOW: "green",
            RiskLevel.MEDIUM: "yellow",
            RiskLevel.HIGH: "orange",
            RiskLevel.CRITICAL: "red",
        }
        color = color_map.get(assessment.level, "green")

        # 风险信息
        risk_text = f"{emoji} {level_name}\n"
        risk_text += f"{self._get_text('score', '评分', 'Score')}: {assessment.score:.1f}/100\n"

        # 风险因素
        if assessment.factors:
            risk_text += f"\n{self._get_text('risk_factors', '风险因素', 'Risk Factors')}:\n"
            for factor in assessment.factors:
                risk_text += f"  • {factor.description} (权重: {factor.weight:.1f})\n"

        # 建议
        if assessment.recommendation:
            risk_text += f"\n{self._get_text('recommendation', '建议', 'Recommendation')}: {assessment.recommendation}"

        risk_panel = Panel(
            risk_text.rstrip(),
            title=self._get_text("risk_assessment", "风险评估", "Risk Assessment"),
            border_style=color,
            box=box.ROUNDED,
        )
        self.console.print(risk_panel)
        self.console.print()

    def display_error(self, error_msg: str):
        """展示错误信息"""
        error_panel = Panel(
            f"[red]{error_msg}[/red]",
            title=self._get_text("error", "错误", "Error"),
            border_style="red",
        )
        self.console.print(error_panel)

    def display_info(self, message: str):
        """展示提示信息"""
        self.console.print(f"[blue]ℹ[/blue] {message}")

    def display_success(self, message: str):
        """展示成功信息"""
        self.console.print(f"[green]✓[/green] {message}")

    def _get_text(self, key: str, zh: str, en: str) -> str:
        """根据语言获取文本

        Args:
            key: 文本键
            zh: 中文文本
            en: 英文文本

        Returns:
            对应语言的文本
        """
        return zh if self.language == "zh" else en


def create_display(language: str = "zh", show_emoji: bool = True) -> ResultDisplay:
    """创建展示器实例

    Args:
        language: 语言设置
        show_emoji: 是否显示 emoji

    Returns:
        ResultDisplay 实例
    """
    return ResultDisplay(language, show_emoji)
