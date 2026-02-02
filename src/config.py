# -*- coding: utf-8 -*-
"""配置文件加载器"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """配置管理类"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: 配置文件路径，默认为项目根目录下的 config/config.yaml
        """
        if config_path is None:
            # 默认配置文件路径
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "config.yaml"

        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
        self._load_env()

    def _load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f) or {}

    def _load_env(self):
        """从环境变量加载敏感信息"""
        # 尝试从 .env 文件加载
        project_root = Path(__file__).parent.parent
        env_file = project_root / ".env"

        if env_file.exists():
            self._load_env_file(env_file)

        # AI 配置
        ai_config = self._config.setdefault("ai", {})

        # API Key 优先从环境变量读取
        if not ai_config.get("api_key"):
            ai_config["api_key"] = os.getenv("API_KEY")

    def _load_env_file(self, env_file: Path):
        """加载 .env 文件"""
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith("#"):
                    continue

                # 解析 KEY=VALUE
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项

        Args:
            key: 配置键，支持点号分隔（如 "ai.provider"）
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def get_ai_config(self) -> Dict[str, Any]:
        """获取 AI 配置"""
        return self._config.get("ai", {})

    def get_display_config(self) -> Dict[str, Any]:
        """获取显示配置"""
        return self._config.get("display", {})

    def get_capturer_config(self) -> Dict[str, Any]:
        """获取捕获器配置"""
        return self._config.get("capturer", {})

    def get_hotkey_config(self) -> Dict[str, Any]:
        """获取快捷键配置"""
        return self._config.get("hotkey", {})

    def get_risk_config(self) -> Dict[str, Any]:
        """获取风险评估配置"""
        return self._config.get("risk", {})

    @property
    def language(self) -> str:
        """获取语言设置"""
        return self.get("display.language", "zh")

    @property
    def model(self) -> str:
        """获取 AI 模型"""
        return self.get("ai.model", "gpt-4")

    @property
    def api_key(self) -> Optional[str]:
        """获取 API 密钥"""
        return self.get("ai.api_key")

    @property
    def api_base(self) -> Optional[str]:
        """获取 API 基础 URL"""
        return self.get("ai.api_base")


def load_config(config_path: Optional[str] = None) -> Config:
    """加载配置

    Args:
        config_path: 配置文件路径

    Returns:
        Config 实例
    """
    return Config(config_path)
