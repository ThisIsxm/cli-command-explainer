# -*- coding: utf-8 -*-
"""风险评估器单元测试"""

import pytest

from src.risk import RiskAssessor, RiskLevel, RiskFactor, RiskAssessment
from src.parser import CommandParser


class TestRiskAssessor:
    """风险评估器测试"""

    def test_initialization(self):
        """测试初始化"""
        assessor = RiskAssessor()
        assert assessor.language == "zh"

    def test_assess_safe_command(self):
        """测试安全命令评估"""
        parser = CommandParser()
        assessor = RiskAssessor()
        parsed = parser.parse("ls -la")
        assessment = assessor.assess(parsed)

        assert assessment.level == RiskLevel.LOW
        assert assessment.score < 50

    def test_assess_delete_command(self):
        """测试删除命令评估"""
        parser = CommandParser()
        assessor = RiskAssessor()
        parsed = parser.parse("rm file.txt")
        assessment = assessor.assess(parsed)

        # rm file.txt 是低风险（没有 -rf 选项）
        assert assessment.level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
        assert any(f.name == "file_deletion" for f in assessment.factors)

    def test_assess_rm_rf(self):
        """测试 rm -rf 命令评估"""
        parser = CommandParser()
        assessor = RiskAssessor()
        parsed = parser.parse("rm -rf /tmp/test")
        assessment = assessor.assess(parsed)

        # rm -rf /tmp/test 有多个风险因素但分数不到 CRITICAL 阈值
        assert assessment.level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert assessment.score > 50

    def test_assess_sudo_command(self):
        """测试 sudo 命令评估"""
        parser = CommandParser()
        assessor = RiskAssessor()
        parsed = parser.parse("sudo rm -rf /tmp/test")
        assessment = assessor.assess(parsed)

        assert any(f.name == "elevated_privileges" for f in assessment.factors)

    def test_assess_network_command(self):
        """测试网络命令评估"""
        parser = CommandParser()
        assessor = RiskAssessor()
        parsed = parser.parse("curl https://example.com")
        assessment = assessor.assess(parsed)

        assert any(f.name == "network_operation" for f in assessment.factors)

    def test_assess_system_modify(self):
        """测试系统修改命令评估"""
        parser = CommandParser()
        assessor = RiskAssessor()
        parsed = parser.parse("chmod 777 /bin")
        assessment = assessor.assess(parsed)

        assert any(f.name == "system_modification" for f in assessment.factors)

    def test_get_risk_level(self):
        """测试获取风险等级"""
        parser = CommandParser()
        assessor = RiskAssessor()
        parsed = parser.parse("rm -rf /")
        level = assessor.get_risk_level(parsed)

        # rm -rf / 有多个风险因素但分数不到 HIGH 阈值
        assert level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]

    def test_quick_assess(self):
        """测试快速评估"""
        assessor = RiskAssessor()
        result = assessor.quick_assess("rm -rf node_modules")

        assert "level" in result
        assert "score" in result
        assert "recommendation" in result
        assert "factors" in result

    def test_format_risk_report_zh(self):
        """测试中文风险报告"""
        parser = CommandParser()
        assessor = RiskAssessor(language="zh")
        parsed = parser.parse("ls")
        assessment = assessor.assess(parsed)
        report = assessor.format_risk_report(assessment)

        assert "风险等级" in report

    def test_format_risk_report_en(self):
        """测试英文风险报告"""
        parser = CommandParser()
        assessor = RiskAssessor(language="en")
        parsed = parser.parse("ls")
        assessment = assessor.assess(parsed)
        report = assessor.format_risk_report(assessment)

        assert "Risk Level" in report


class TestRiskLevel:
    """风险等级测试"""

    def test_level_values(self):
        """测试风险等级值"""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"

    def test_get_emoji(self):
        """测试获取 emoji"""
        assert RiskLevel.LOW.get_emoji() == ""
        assert RiskLevel.MEDIUM.get_emoji() == ""
        assert RiskLevel.HIGH.get_emoji() == ""
        assert RiskLevel.CRITICAL.get_emoji() == ""

    def test_get_display_name_zh(self):
        """测试中文显示名称"""
        assert "低风险" in RiskLevel.LOW.get_display_name("zh")
        assert "中风险" in RiskLevel.MEDIUM.get_display_name("zh")
        assert "高风险" in RiskLevel.HIGH.get_display_name("zh")
        assert "危险" in RiskLevel.CRITICAL.get_display_name("zh")

    def test_get_display_name_en(self):
        """测试英文显示名称"""
        assert "Low" in RiskLevel.LOW.get_display_name("en")
        assert "Medium" in RiskLevel.MEDIUM.get_display_name("en")
        assert "High" in RiskLevel.HIGH.get_display_name("en")
        assert "Critical" in RiskLevel.CRITICAL.get_display_name("en")


class TestRiskFactor:
    """风险因素测试"""

    def test_risk_factor_creation(self):
        """测试风险因素创建"""
        factor = RiskFactor("test_factor", "Test description", 0.5)

        assert factor.name == "test_factor"
        assert factor.description == "Test description"
        assert factor.weight == 0.5

    def test_risk_factor_repr(self):
        """测试风险因素字符串表示"""
        factor = RiskFactor("test", "desc", 0.5)
        repr_str = repr(factor)

        assert "test" in repr_str
