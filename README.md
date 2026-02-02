# CLI Command Explainer

> AI 驱动的命令行命令解释工具，帮助你理解命令含义并评估风险

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 特性

- 智能命令识别 - 支持 150+ 常用命令自动识别
- AI 解释 - 使用 AI 详细解释命令功能和参数
- 风险评估 - 4 级风险评估（低/中/高/严重）
- 热键触发 - 快捷键 Ctrl+Shift+E 一键解释剪贴板命令
- 多服务支持 - 兼容所有 OpenAI 格式 API 及本地 Ollama
- 美化输出 - Rich 终端美化，清晰易读

## 快速开始

### 1. 安装

```bash
git clone https://github.com/ThisIsxm/cli-command-explainer.git
cd cli-command-explainer
python -m venv cli-venv
cli-venv\Scripts\activate  # Windows
# source cli-venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. 配置

```bash
cp .env.example .env
# 编辑 .env 设置 API_KEY=sk-your-key
```

编辑 config/config.yaml 配置 AI 服务：

```yaml
ai:
  # 支持所有 OpenAI 格式的 API
  api_base: https://openrouter.ai/api/v1
  model: openai/gpt-oss-120b

  # 或者本地 Ollama
  # api_base: http://localhost:11434/v1
  # model: llama3.2
```

### 3. 运行

```bash
# 单命令模式
python -m src.main "ls -la"

# 交互模式
python -m src.main --interactive

# 剪贴板监听模式（推荐）
python -m src.main --clipboard
```

## 使用模式

### 模式 1: 单命令模式

```bash
python -m src.main "git push --force"
python -m src.main "rm -rf /tmp/test"
```

### 模式 2: 交互模式

```bash
python -m src.main --interactive
$ ls -la
$ quit  # 退出
```

### 模式 3: 剪贴板监听模式

```bash
python -m src.main --clipboard
```

1. 复制任何命令
2. 按 Ctrl+Shift+E 触发解释
3. 查看详细说明和风险评估

## 项目结构

```
cli-command-explainer/
 src/
    capturer/       # 命令捕获（剪贴板/热键）
    parser/         # 命令解析
    risk/           # 风险评估
    explainer/      # AI 解释引擎
    ui/             # 终端 UI 展示
    main.py         # 主程序入口
 config/config.yaml  # 配置文件
 tests/              # 测试用例
```

## 其他版本

想要更简洁的纯 AI 版本？查看 [cli-explainer-v2](https://github.com/ThisIsxm/cli-explainer-v2)

v2 使用完全 AI 驱动，一次调用完成所有分析，代码量仅约 500 行。

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件

## 联系方式

- 问题反馈：[GitHub Issues](https://github.com/ThisIsxm/cli-command-explainer/issues)
- 功能建议：[GitHub Discussions](https://github.com/ThisIsxm/cli-command-explainer/discussions)

---

如果这个项目对你有帮助，请给个 Star！
