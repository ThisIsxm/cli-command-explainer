# -*- coding: utf-8 -*-
"""AI 解释引擎"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# 尝试导入 LiteLLM，如果不可用则使用模拟模式
try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

from .prompts import PromptTemplate, get_prompt_template

logger = logging.getLogger(__name__)


class AIExplanation:
    """AI 解释结果"""

    def __init__(self, raw_response: str, parsed_data: Dict[str, Any]):
        """
        Args:
            raw_response: AI 原始响应
            parsed_data: 解析后的 JSON 数据
        """
        self.raw_response = raw_response
        self.summary = parsed_data.get("summary", "")
        self.description = parsed_data.get("description", "")
        self.purpose = parsed_data.get("purpose", "")
        self.parameters = parsed_data.get("parameters", [])
        self.examples = parsed_data.get("examples", [])
        self.warnings = parsed_data.get("warnings", [])
        self.alternatives = parsed_data.get("alternatives", [])
        self.risk_level = parsed_data.get("risk_level", "low")
        self.risk_score = parsed_data.get("risk_score", 0.0)
        self.recommendation = parsed_data.get("recommendation", "")

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
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "recommendation": self.recommendation,
        }


class AIExplainer:
    """AI 解释引擎

    使用 LiteLLM 统一接口支持多个 AI 服务提供商。

    支持的提供商：
    - OpenAI (GPT-4, GPT-3.5)
    - OpenRouter (多模型访问)
    - Ollama (本地模型)
    - 其他 LiteLLM 支持的提供商
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        language: str = "zh",
        timeout: int = 30,
        max_retries: int = 3,
        api_base: Optional[str] = None,
    ):
        """
        Args:
            api_key: API 密钥
            model: 模型名称（如 gpt-4, deepseek-chat, llama3.2）
            language: 语言设置
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            api_base: API 基础 URL（如 https://api.deepseek.com）
        """
        self.model = model
        self.language = language
        self.timeout = timeout
        self.max_retries = max_retries
        self.api_base = api_base
        self.api_key = api_key
        self.prompt_template = get_prompt_template(language)

        # 配置 LiteLLM

        if LITELLM_AVAILABLE:
            self._configure_litellm(api_key)
            self._available = True
        else:
            logger.warning("LiteLLM not available, running in mock mode")
            self._available = False

    def _configure_litellm(self, api_key: Optional[str]):
        """配置 LiteLLM"""
        if api_key:
            # 统一使用 OPENAI_API_KEY（兼容所有 OpenAI 格式的服务）
            os.environ["OPENAI_API_KEY"] = api_key
            litellm.api_key = api_key

        # 设置请求超时
        litellm.timeout = self.timeout

        # 设置日志级别
        litellm.set_verbose = False

    def is_available(self) -> bool:
        """检查 AI 服务是否可用"""
        return self._available

    def explain(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AIExplanation:
        """解释命令

        Args:
            command: 命令字符串
            context: 上下文信息

        Returns:
            AIExplanation 对象
        """
        if context is None:
            context = {}

        # 如果 AI 不可用，返回模拟结果
        if not self._available:
            return self._mock_explain(command, context)

        # 尝试调用 AI
        for attempt in range(self.max_retries):
            try:
                response = self._call_ai(command, context)
                explanation = self._parse_response(response)
                logger.info(f"Successfully explained command: {command[:30]}...")
                return explanation
            except Exception as e:
                logger.warning(f"AI call attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    # 最后一次尝试失败，返回模拟结果
                    logger.error("All AI attempts failed, using mock response")
                    return self._mock_explain(command, context)

        return self._mock_explain(command, context)

    def _call_ai(self, command: str, context: Dict[str, Any]) -> str:
        """调用 AI 服务

        Args:
            command: 命令字符串
            context: 上下文信息

        Returns:
            AI 响应字符串
        """
        system_prompt = self.prompt_template.get_system_prompt()
        user_prompt = self.prompt_template.get_user_prompt(command, context)

        # 构建调用参数
        call_params = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,  # 低温度以获得更稳定的输出
            "max_tokens": 1000,
        }

        # LiteLLM 使用 openai/model 格式兼容所有服务
        call_params["model"] = f"openai/{self.model}"

        # 如果设置了 api_base，使用自定义端点
        if self.api_base:
            call_params["api_base"] = self.api_base

        response = litellm.completion(**call_params)

        return response.choices[0].message.content

    def _parse_response(self, response: str) -> AIExplanation:
        """解析 AI 响应

        Args:
            response: AI 响应字符串

        Returns:
            AIExplanation 对象
        """
        # 尝试提取 JSON（处理可能的 markdown 包装）
        json_str = self._extract_json(response)

        try:
            parsed_data = json.loads(json_str)
            return AIExplanation(response, parsed_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            # 返回包含原始响应的模拟结果
            return AIExplanation(
                response,
                {
                    "summary": "解析失败",
                    "description": f"AI 返回了无效的 JSON 格式",
                    "purpose": "请检查 AI 响应",
                    "parameters": [],
                    "examples": [],
                    "warnings": ["AI 响应解析失败"],
                    "alternatives": [],
                    "risk_level": "low",
                    "risk_score": 0,
                    "recommendation": "请重试或检查 AI 配置",
                },
            )

    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON

        Args:
            text: 可能包含 JSON 的文本

        Returns:
            纯 JSON 字符串
        """
        # 检查是否有 markdown 代码块
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.rfind("```")
            if end > start:
                return text[start:end].strip()

        # 检查是否有普通代码块
        if "```" in text:
            start = text.find("```") + 3
            end = text.rfind("```")
            if end > start:
                return text[start:end].strip()

        # 尝试找到第一个 { 和最后一个 }
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return text[start : end + 1]

        # 如果找不到，返回原始文本
        return text

    def _mock_explain(self, command: str, context: Dict[str, Any]) -> AIExplanation:
        """模拟解释（当 AI 不可用时使用）

        Args:
            command: 命令字符串
            context: 上下文信息

        Returns:
            AIExplanation 对象
        """
        if self.language == "zh":
            mock_response = {
                "summary": f"执行 {command[:30]}...",
                "description": "这是一个命令行命令，需要根据具体参数进行解释。",
                "purpose": "执行系统命令",
                "parameters": [],
                "examples": [f"{command} --help"],
                "warnings": [
                    "AI 服务当前不可用，建议配置 AI API 或使用本地模型",
                    "请确保了解该命令的作用后再执行",
                ],
                "alternatives": [
                    "man 命令名  # 查看手册",
                    "命令名 --help  # 查看帮助",
                ],
                "risk_level": "low",
                "risk_score": 10.0,
                "recommendation": "请先查阅相关文档了解命令作用",
            }
        else:
            mock_response = {
                "summary": f"Execute {command[:30]}...",
                "description": "This is a command-line command that requires interpretation based on specific parameters.",
                "purpose": "Execute system command",
                "parameters": [],
                "examples": [f"{command} --help"],
                "warnings": [
                    "AI service currently unavailable, consider configuring AI API or using local models",
                    "Make sure you understand the command before execution",
                ],
                "alternatives": [
                    "man command_name  # View manual",
                    "command_name --help  # View help",
                ],
                "risk_level": "low",
                "risk_score": 10.0,
                "recommendation": "Please consult documentation first",
            }

        response_str = json.dumps(mock_response, ensure_ascii=False)
        return AIExplanation(response_str, mock_response)

    def set_language(self, language: str):
        """设置语言

        Args:
            language: 语言设置 ("zh" 或 "en")
        """
        self.language = language
        self.prompt_template = get_prompt_template(language)

    def set_model(self, model: str):
        """设置模型

        Args:
            model: 模型名称
        """
        self.model = model

    def set_provider(self, provider: str, api_key: Optional[str] = None):
        """设置提供商

        Args:
            provider: 服务提供商
            api_key: API 密钥
        """
        self.provider = provider
        if api_key:
            self._configure_litellm(api_key)


class ExplainerConfig:
    """解释器配置"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        language: str = "zh",
        timeout: int = 30,
        max_retries: int = 3,
        api_base: Optional[str] = None,
    ):
        self.api_key = api_key
        self.model = model
        self.language = language
        self.timeout = timeout
        self.max_retries = max_retries
        self.api_base = api_base

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "ExplainerConfig":
        """从字典创建配置

        Args:
            config: 配置字典

        Returns:
            ExplainerConfig 实例
        """
        ai_config = config.get("ai", {})
        display_config = config.get("display", {})

        return cls(
            api_key=ai_config.get("api_key"),
            model=ai_config.get("model", "gpt-4"),
            language=display_config.get("language", "zh"),
            timeout=ai_config.get("timeout", 30),
            max_retries=ai_config.get("max_retries", 3),
            api_base=ai_config.get("api_base"),
        )


def create_explainer(config: ExplainerConfig) -> AIExplainer:
    """创建解释器实例

    Args:
        config: 解释器配置

    Returns:
        AIExplainer 实例
    """
    return AIExplainer(
        api_key=config.api_key,
        model=config.model,
        language=config.language,
        timeout=config.timeout,
        max_retries=config.max_retries,
        api_base=config.api_base,
    )


def create_explainer_from_dict(config: Dict[str, Any]) -> AIExplainer:
    """从配置字典创建解释器

    Args:
        config: 配置字典

    Returns:
        AIExplainer 实例
    """
    explainer_config = ExplainerConfig.from_dict(config)
    return create_explainer(explainer_config)

