# -*- coding: utf-8 -*-
"""AI 解释器 Prompt 模板"""

from typing import Dict, Any


class PromptTemplate:
    """Prompt 模板基类"""

    def __init__(self, language: str = "zh"):
        """
        Args:
            language: 语言设置 ("zh" 或 "en")
        """
        self.language = language

    def get_system_prompt(self) -> str:
        """获取系统 Prompt"""
        return self._get_system_prompt()

    def get_user_prompt(self, command: str, context: Dict[str, Any] = None) -> str:
        """获取用户 Prompt

        Args:
            command: 命令字符串
            context: 上下文信息
        """
        if context is None:
            context = {}
        return self._get_user_prompt(command, context)

    def _get_system_prompt(self) -> str:
        """实现具体的系统 Prompt"""
        if self.language == "zh":
            return self._system_prompt_zh()
        return self._system_prompt_en()

    def _get_user_prompt(self, command: str, context: Dict[str, Any]) -> str:
        """实现具体的用户 Prompt"""
        if self.language == "zh":
            return self._user_prompt_zh(command, context)
        return self._user_prompt_en(command, context)

    def _system_prompt_zh(self) -> str:
        """中文系统 Prompt"""
        return """你是一个专业的命令行（CLI）命令解释专家。你的任务是分析命令并给出清晰的解释和风险评估。

输出格式要求：
1. 必须使用 JSON 格式输出
2. JSON 必须包含以下字段：
   - summary: 命令的一行摘要（不超过50字）
   - description: 详细说明（分点列出主要功能）
   - purpose: 命令的用途（一句话）
   - parameters: 参数说明列表
   - examples: 常见用法示例列表
   - warnings: 警告信息列表
   - alternatives: 替代方案列表
   - risk_level: 风险等级（low/medium/high/critical）
   - risk_score: 风险分数（0-100）
   - recommendation: 执行建议

风险等级定义：
- low: 只读操作，安全执行
- medium: 修改文件或系统，建议检查参数
- high: 较高风险，请仔细确认
- critical: 危险，强烈建议不要执行

注意事项：
- 只输出 JSON，不要包含其他文字
- 解释要简洁明了
- 必须包含风险评估
- 遇到未知命令时，说明这是外部命令或脚本"""

    def _system_prompt_en(self) -> str:
        """英文系统 Prompt"""
        return """You are an expert in command-line (CLI) command interpretation. Your task is to analyze commands and provide clear explanations with risk assessment.

Output format requirements:
1. Must use JSON format
2. JSON must contain the following fields:
   - summary: One-line summary (max 50 characters)
   - description: Detailed explanation (list key features)
   - purpose: Purpose of the command (one sentence)
   - parameters: Parameter descriptions list
   - examples: Common usage examples list
   - warnings: Warning messages list
   - alternatives: Alternative solutions list
   - risk_level: Risk level (low/medium/high/critical)
   - risk_score: Risk score (0-100)
   - recommendation: Execution recommendation

Risk level definitions:
- low: Read-only operation, safe to execute
- medium: Modifies files or system, review parameters
- high: Significant risk, confirm carefully
- critical: Dangerous, strongly advise against execution

Notes:
- Output only JSON, no additional text
- Keep explanations concise and clear
- Must include risk assessment
- For unknown commands, note it's an external command or script"""

    def _user_prompt_zh(self, command: str, context: Dict[str, Any]) -> str:
        """中文用户 Prompt"""
        prompt = f"""请分析以下命令：

命令：{command}

请提供：
1. 命令的功能说明
2. 参数和选项的详细解释
3. 实际使用示例
4. 潜在的风险和注意事项
5. 风险等级评估"""

        if context.get("current_dir"):
            prompt += f"\n\n当前目录：{context['current_dir']}"

        if context.get("os_type"):
            prompt += f"\n\n操作系统：{context['os_type']}"

        return prompt

    def _user_prompt_en(self, command: str, context: Dict[str, Any]) -> str:
        """英文用户 Prompt"""
        prompt = f"""Please analyze the following command:

Command: {command}

Please provide:
1. Command functionality explanation
2. Detailed explanation of parameters and options
3. Practical usage examples
4. Potential risks and warnings
5. Risk level assessment"""

        if context.get("current_dir"):
            prompt += f"\n\nCurrent directory: {context['current_dir']}"

        if context.get("os_type"):
            prompt += f"\n\nOperating system: {context['os_type']}"

        return prompt


# JSON Schema for validation
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "description": {"type": "string"},
        "purpose": {"type": "string"},
        "parameters": {"type": "array", "items": {"type": "string"}},
        "examples": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "alternatives": {"type": "array", "items": {"type": "string"}},
        "risk_level": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        "risk_score": {"type": "number", "minimum": 0, "maximum": 100},
        "recommendation": {"type": "string"},
    },
    "required": [
        "summary",
        "description",
        "purpose",
        "parameters",
        "examples",
        "warnings",
        "alternatives",
        "risk_level",
        "risk_score",
        "recommendation",
    ],
}


def get_prompt_template(language: str = "zh") -> PromptTemplate:
    """获取 Prompt 模板实例

    Args:
        language: 语言设置

    Returns:
        PromptTemplate 实例
    """
    return PromptTemplate(language=language)


def get_json_schema() -> Dict[str, Any]:
    """获取 JSON Schema

    Returns:
        JSON Schema 字典
    """
    return JSON_SCHEMA

