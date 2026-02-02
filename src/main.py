# -*- coding: utf-8 -*-
"""CLI 命令解释 Agent - 主程序入口"""

import sys
import logging
from typing import Optional
from pathlib import Path

from .config import load_config
from .parser import CommandParser
from .risk import RiskAssessor
from .explainer import AIExplainer, ExplainerConfig
from .ui import create_display
from .capturer import ClipboardCapturer, CaptureEvent
from .capturer.hotkey import create_integrated_capturer


# 配置日志
logging.basicConfig(
    level=logging.WARNING,  # 生产环境使用WARNING级别，减少日志输出
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class CommandExplainerApp:
    """CLI 命令解释 Agent 主应用"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = load_config(config_path)

        # 初始化各个模块
        self.parser = CommandParser()
        self.risk_assessor = RiskAssessor(language=self.config.language)

        explainer_config = ExplainerConfig.from_dict(self.config._config)
        self.ai_explainer = AIExplainer(
            api_key=explainer_config.api_key,
            model=explainer_config.model,
            language=explainer_config.language,
            timeout=explainer_config.timeout,
            max_retries=explainer_config.max_retries,
            api_base=explainer_config.api_base,
        )

        display_config = self.config.get_display_config()
        self.display = create_display(
            language=self.config.language,
            show_emoji=display_config.get("show_emoji", True),
        )

        # 检查 AI 可用性
        if not self.ai_explainer.is_available():
            self.display.display_warning(
                "⚠️  AI 服务不可用，请检查 API_KEY 配置或网络连接。"
            )

    def explain_command(self, command: str) -> None:
        """解释单个命令

        Args:
            command: 命令字符串
        """
        try:
            # 1. 解析命令
            parsed_command = self.parser.parse(command)

            # 2. 风险评估
            risk_assessment = self.risk_assessor.assess(parsed_command)

            # 3. AI 解释（显示进度提示）
            self.display.console.print("[dim]⏳ 正在调用 AI 解释命令...[/dim]")
            context = {
                "command_type": parsed_command.command_type,
                "risk_level": risk_assessment.level.value,
            }
            ai_explanation = self.ai_explainer.explain(command, context)

            # 4. 展示结果
            self.display.display_explanation(
                command=command,
                explanation=ai_explanation.to_dict(),
                risk_assessment=risk_assessment,
            )

        except KeyboardInterrupt:
            self.display.display_info("操作已取消")
        except Exception as e:
            logger.error(f"解释命令时出错: {e}")
            self.display.display_error(f"解释命令时出错: {str(e)}")

    def run_interactive_mode(self) -> None:
        """运行交互模式"""
        try:
            self.display.console.print(
                "[bold cyan]CLI 命令解释 Agent[/bold cyan] - 交互模式"
            )
            self.display.console.print("输入命令进行解释，输入 'quit' 或 'exit' 退出\n")

            while True:
                try:
                    # 读取用户输入
                    command = input("$ ")
                    command = command.strip()

                    # 退出命令
                    if command.lower() in ["quit", "exit", "q"]:
                        self.display.display_info("再见！")
                        break

                    # 空命令
                    if not command:
                        continue

                    # 解释命令
                    self.explain_command(command)

                except EOFError:
                    break
                except KeyboardInterrupt:
                    self.display.console.print()
                    self.display.display_info("使用 'quit' 或 'exit' 退出")

        except Exception as e:
            logger.error(f"交互模式出错: {e}", exc_info=True)
            self.display.display_error(f"程序出错: {str(e)}")

    def run_clipboard_mode(self) -> None:
        """运行剪贴板监听模式"""
        try:
            self.display.console.print(
                "[bold cyan]CLI 命令解释 Agent[/bold cyan] - 剪贴板监听模式"
            )

            # 获取快捷键配置
            hotkey_config = self.config.get_hotkey_config()
            trigger_key = hotkey_config.get("trigger", "ctrl+shift+e")

            self.display.console.print(
                f"按 [bold yellow]{trigger_key}[/bold yellow] 触发解释剪贴板中的命令"
            )
            self.display.console.print("按 [bold red]Ctrl+C[/bold red] 退出\n")

            # 创建集成捕获器
            def on_capture(event: CaptureEvent):
                """捕获事件回调"""
                command = event.content
                self.display.console.print(f"\n[dim]>>> 捕获到命令[/dim]\n")
                self.explain_command(command)
                self.display.console.print()

            capturer, _ = create_integrated_capturer(
                hotkey_combo=trigger_key,
                capturer_callback=on_capture,
            )

            # 启动捕获
            try:
                capturer.start_listening()
                self.display.display_success(f"剪贴板监听已启动 (热键: {trigger_key})")

                # 保持运行
                try:
                    import time

                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.display.console.print()
                    self.display.display_info("停止监听...")

            except Exception as e:
                self.display.display_error(f"热键注册失败: {e}")
                self.display.display_info("💡 提示: Windows 上可能需要以管理员权限运行")
                return

        except Exception as e:
            logger.error(f"剪贴板模式出错: {e}")
            self.display.display_error(f"程序出错: {str(e)}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="CLI 命令解释 Agent - 使用 AI 解释命令行命令"
    )
    parser.add_argument(
        "command",
        nargs="*",
        help="要解释的命令（可选，不提供则进入交互模式）",
    )
    parser.add_argument(
        "--config",
        "-c",
        help="配置文件路径",
        default=None,
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="启用剪贴板监听模式",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="启用交互模式",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="详细日志输出",
    )

    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # 创建应用实例
        app = CommandExplainerApp(config_path=args.config)

        # 根据参数选择运行模式
        if args.clipboard:
            # 剪贴板监听模式
            app.run_clipboard_mode()
        elif args.interactive or not args.command:
            # 交互模式
            app.run_interactive_mode()
        else:
            # 单命令模式
            command = " ".join(args.command)
            app.explain_command(command)

    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序出错: {e}", exc_info=True)
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
