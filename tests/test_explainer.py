# -*- coding: utf-8 -*-
"""解释器单元测试"""

import pytest

from src.explainer import CommandExplainer, CommandExplanation, AIExplainer, AIExplanation
from src.explainer.engine import ExplainerConfig
from src.parser import CommandParser


class TestCommandExplainer:
    """命令解释器测试"""

    def test_initialization(self):
        """测试初始化"""
        explainer = CommandExplainer()
        assert explainer.language == "zh"

        explainer_en = CommandExplainer(language="en")
        assert explainer_en.language == "en"

    def test_explain_known_command(self):
        """测试解释已知命令"""
        parser = CommandParser()
        explainer = CommandExplainer()
        parsed = parser.parse("ls -la")
        explanation = explainer.explain(parsed)

        assert isinstance(explanation, CommandExplanation)
        assert explanation.summary != ""
        assert explanation.purpose != ""

    def test_explain_unknown_command(self):
        """测试解释未知命令"""
        parser = CommandParser()
        explainer = CommandExplainer()
        parsed = parser.parse("customcmd --opt value")
        explanation = explainer.explain(parsed)

        assert isinstance(explanation, CommandExplanation)
        assert "外部命令" in explanation.description or "External" in explanation.description

    def test_explain_rm_command(self):
        """测试解释 rm 命令"""
        parser = CommandParser()
        explainer = CommandExplainer()
        parsed = parser.parse("rm -rf node_modules")
        explanation = explainer.explain(parsed)

        assert "删除" in explanation.description or "Remove" in explanation.description
        assert len(explanation.warnings) > 0

    def test_format_report(self):
        """测试格式化报告"""
        parser = CommandParser()
        explainer = CommandExplainer()
        parsed = parser.parse("ls -la")
        explanation = explainer.explain(parsed)
        report = explainer.format_report(explanation)

        assert "命令解释" in report or "Command Explanation" in report
        assert explanation.summary in report

    def test_generate_parameters(self):
        """测试生成参数说明"""
        parser = CommandParser()
        explainer = CommandExplainer()
        parsed = parser.parse("ls -la")
        explanation = explainer.explain(parsed)

        assert len(explanation.parameters) > 0

    def test_generate_examples(self):
        """测试生成示例"""
        parser = CommandParser()
        explainer = CommandExplainer()
        parsed = parser.parse("ls")
        explanation = explainer.explain(parsed)

        assert len(explanation.examples) > 0

    def test_explanation_to_dict(self):
        """测试转换为字典"""
        parser = CommandParser()
        explainer = CommandExplainer()
        parsed = parser.parse("ls")
        explanation = explainer.explain(parsed)
        data = explanation.to_dict()

        assert "summary" in data
        assert "description" in data
        assert "purpose" in data
        assert "parameters" in data
        assert "examples" in data

    def test_quick_explain(self):
        """测试快速解释"""
        explainer = CommandExplainer()
        result = explainer.quick_explain("ls -la")

        assert "summary" in result
        assert "purpose" in result
        assert "risk_level" in result


class TestAIExplainer:
    """AI 解释引擎测试"""

    def test_initialization(self):
        """测试初始化"""
        explainer = AIExplainer()
        assert explainer.language == "zh"
        assert explainer.model == "gpt-4"
        assert explainer.provider == "openai"

    def test_is_available_without_litellm(self):
        """测试没有 LiteLLM 时的可用性"""
        # 这个测试假设没有安装 LiteLLM
        explainer = AIExplainer()
        # AIExplainer 会优雅降级到模拟模式
        assert isinstance(explainer, AIExplainer)

    def test_explain_command(self):
        """测试解释命令"""
        explainer = AIExplainer()
        explanation = explainer.explain("ls -la")

        assert isinstance(explanation, AIExplanation)
        assert explanation.summary != ""

    def test_mock_explain_without_ai(self):
        """测试没有 AI 时的模拟解释"""
        explainer = AIExplainer()
        explanation = explainer.explain("ls -la")

        assert explanation.risk_score > 0
        assert explanation.risk_level in ["low", "medium", "high", "critical"]

    def test_set_language(self):
        """测试设置语言"""
        explainer = AIExplainer()
        explainer.set_language("en")

        assert explainer.language == "en"

    def test_set_model(self):
        """测试设置模型"""
        explainer = AIExplainer()
        explainer.set_model("gpt-3.5-turbo")

        assert explainer.model == "gpt-3.5-turbo"

    def test_explanation_to_dict(self):
        """测试 AI 解释转换为字典"""
        explainer = AIExplainer()
        explanation = explainer.explain("ls -la")
        data = explanation.to_dict()

        assert "summary" in data
        assert "description" in data
        assert "purpose" in data
        assert "risk_level" in data
        assert "risk_score" in data


class TestExplainerConfig:
    """解释器配置测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = ExplainerConfig()

        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.language == "zh"

    def test_custom_config(self):
        """测试自定义配置"""
        config = ExplainerConfig(
            provider="ollama",
            model="llama2",
            language="en",
            timeout=60,
        )

        assert config.provider == "ollama"
        assert config.model == "llama2"
        assert config.language == "en"
        assert config.timeout == 60

    def test_from_dict(self):
        """测试从字典创建配置"""
        config_dict = {
            "ai": {
                "provider": "openrouter",
                "model": "gpt-4",
            },
            "display": {
                "language": "zh",
            },
        }
        config = ExplainerConfig.from_dict(config_dict)

        assert config.provider == "openrouter"
        assert config.language == "zh"


class TestAIExplanation:
    """AI 解释结果测试"""

    def test_ai_explanation_creation(self):
        """测试 AI 解释结果创建"""
        parsed_data = {
            "summary": "Execute ls -la",
            "description": "List all files with details",
            "purpose": "Display directory contents",
            "parameters": [],
            "examples": [],
            "warnings": [],
            "alternatives": [],
            "risk_level": "low",
            "risk_score": 10.0,
            "recommendation": "Safe to execute",
        }
        explanation = AIExplanation("mock_response", parsed_data)

        assert explanation.summary == "Execute ls -la"
        assert explanation.risk_score == 10.0
        assert explanation.risk_level == "low"

    def test_ai_explanation_to_dict(self):
        """测试转换为字典"""
        parsed_data = {
            "summary": "Test",
            "description": "Test desc",
            "purpose": "Test purpose",
            "parameters": [],
            "examples": [],
            "warnings": [],
            "alternatives": [],
            "risk_level": "low",
            "risk_score": 10.0,
            "recommendation": "Test",
        }
        explanation = AIExplanation("response", parsed_data)
        data = explanation.to_dict()

        assert "summary" in data
        assert "risk_score" in data
