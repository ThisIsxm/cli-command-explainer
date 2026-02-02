# Changelog

本文档记录 CLI Command Explainer 所有重要的版本变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-01-30

### 🎉 首次发布

#### Added
- ✨ AI 驱动的命令解释功能
  - 支持 DeepSeek、OpenAI、Ollama 等所有 OpenAI 兼容服务
  - 详细的命令说明、参数解释、用例展示
  - 自动生成警告和替代方案建议
  
- 🛡️ 命令风险评估系统
  - 4 级风险评估（低/中/高/严重）
  - 多维度风险分析（文件操作、系统操作、网络操作等）
  - 基于风险级别的执行建议
  
- 🎯 多种运行模式
  - 单命令模式：快速解释单个命令
  - 交互模式：Shell 风格的交互式输入
  - 剪贴板监听模式：热键触发解释
  
- 🎨 Rich 终端美化
  - 彩色输出和格式化表格
  - 风险级别颜色编码
  - Emoji 图标支持
  
- ⚙️ 灵活的配置系统
  - YAML 配置文件
  - 环境变量支持
  - 可自定义热键和显示选项
  
- 🌐 多语言支持
  - 中文界面
  - 英文界面
  
#### Technical
- 模块化架构设计
  - `capturer`: 命令捕获（剪贴板/热键）
  - `parser`: 命令解析
  - `risk`: 风险评估引擎
  - `explainer`: AI 解释引擎
  - `ui`: 终端 UI 展示
  
- 完善的错误处理
  - API 失败自动降级
  - 友好的错误提示
  - 详细的日志记录（可选）
  
- 统一的 API 接口
  - 通过 LiteLLM 支持多种 AI 服务
  - 简化的配置方式（api_base + model）

#### Documentation
- 📖 完整的 README.md
- 🚀 快速开始指南 (QUICKSTART.md)
- 📋 发布计划和任务清单
- 🔍 代码审查报告和清理总结

---

## [Unreleased]

### 计划中的功能

#### v1.1.0
- [ ] 用户自定义命令列表支持
- [ ] 命令执行确认交互 `[Y/N]`
- [ ] 扩展静态命令识别库（200+ 命令）
- [ ] 学习模式（记录用户确认的命令）

#### v1.2.0
- [ ] GUI 弹窗显示模式
- [ ] 多平台打包（Windows/macOS/Linux）
- [ ] PyPI 发布（`pip install cli-explainer`）

#### Future
- [ ] 命令历史记录
- [ ] 社区命令库
- [ ] 命令模板和别名管理
- [ ] 批量命令分析

---

## 版本说明

- **[1.0.0]**: 首个稳定版本
- **[Unreleased]**: 开发中的功能

[1.0.0]: https://github.com/ThisIsxm/cli-command-explainer/releases/tag/v1.0.0
[Unreleased]: https://github.com/ThisIsxm/cli-command-explainer/compare/v1.0.0...HEAD
