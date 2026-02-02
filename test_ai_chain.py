#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 AI 链路是否正常工作"""

import sys
import io
from pathlib import Path

# Windows 控制台 UTF-8 修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import load_config
from src.parser import CommandParser
from src.risk import RiskAssessor
from src.explainer import AIExplainer, ExplainerConfig
from src.ui import create_display


def test_ai_chain():
    """测试完整的 AI 解释链路"""
    # 设置控制台为 UTF-8
    if sys.platform == 'win32':
        import os
        os.system('chcp 65001 > nul')

    # 禁用输出缓冲，确保实时显示    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    print("=" * 60, flush=True)
    print("CLI 命令解释 Agent - AI 链路测试", flush=True)
    print("=" * 60, flush=True)
    print(flush=True)

    # 加载配置
    print("1. 加载配置...", flush=True)
    try:
        config = load_config()
        print(f"   [OK] 配置加载成功", flush=True)
        print(f"   - Model: {config.model}", flush=True)
        print(f"   - API Base: {config.api_base or 'default'}", flush=True)
        print(f"   - Language: {config.language}", flush=True)
    except Exception as e:
        print(f"   [ERROR] 配置加载失败: {e}", flush=True)
        return False
    print()

    # 初始化模块
    print("2. 初始化模块...", flush=True)
    try:
        parser = CommandParser()
        risk_assessor = RiskAssessor(language=config.language)

        explainer_config = ExplainerConfig.from_dict(config._config)
        ai_explainer = AIExplainer(
            api_key=explainer_config.api_key,
            model=explainer_config.model,
            language=explainer_config.language,
            timeout=explainer_config.timeout,
            max_retries=explainer_config.max_retries,
            api_base=explainer_config.api_base,
        )

        display = create_display(language=config.language)
        print("   [OK] 所有模块初始化成功", flush=True)
    except Exception as e:
        print(f"   [ERROR] 模块初始化失败 {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False
    print()

    # 检查 AI 可用性
    print("3. 检查 AI 服务...", flush=True)
    if ai_explainer.is_available():
        print("   [OK] AI 服务可用 (LiteLLM 已安装)", flush=True)
    else:
        print("   [WARNING] AI 服务不可用，将使用降级模式", flush=True)
        print("   提示: 安装 LiteLLM: pip install litellm")
    print()

    # 测试命令
    test_command = "ls -la"
    print(f"4. 测试命令: {test_command}", flush=True)
    print()

    try:
        # 解析
        print("   - 解析命令...", flush=True)
        parsed = parser.parse(test_command)
        print(f"     [OK] 命令: {parsed.command}", flush=True)
        print(f"     [OK] 选项: {parsed.options}", flush=True)
        print(f"     [OK] 类型: {parsed.command_type}", flush=True)
        print()

        # 风险评估
        print("   - 评估风险...", flush=True)
        risk = risk_assessor.assess(parsed)
        print(f"     [OK] 风险等级: {risk.level.get_display_name(config.language)}", flush=True)
        print(f"     [OK] 风险评分: {risk.score:.1f}/100", flush=True)
        print()

        # AI 解释
        print("   - AI 解释...", flush=True)
        context = {
            "command_type": parsed.command_type,
            "risk_level": risk.level.value,
        }
        explanation = ai_explainer.explain(test_command, context)
        print(f"     [OK] 概要: {explanation.summary}", flush=True)
        print()

        # 展示结果
        print("5. 展示完整结果:", flush=True)
        print("-" * 60, flush=True)
        display.display_explanation(
            command=test_command,
            explanation=explanation.to_dict(),
            risk_assessment=risk,
        )
        print("-" * 60, flush=True)
        print()

        print("[SUCCESS] AI 链路测试成功！项目可以正常运行。", flush=True)
        return True

    except Exception as e:
        print(f"   [ERROR] 测试失败: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_ai_chain()
    sys.exit(0 if success else 1)
