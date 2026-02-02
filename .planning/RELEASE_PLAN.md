# 开源项目发布计划

## 项目概述

**项目名称**: CLI Command Explainer  
**版本**: v1.0.0 (首次发布)  
**目标**: 将现有功能包装成完整可发布的开源项目

---

## 当前状态分析

### ✅ 已完成（核心功能）

| 模块 | 文件 | 状态 |
|------|------|------|
| **命令捕获** | `src/capturer/` | ✅ 完成 |
| **命令解析** | `src/parser/` | ✅ 完成 |
| **风险评估** | `src/risk/` | ✅ 完成 |
| **AI解释** | `src/explainer/` | ✅ 完成 |
| **UI展示** | `src/ui/` | ✅ 完成 |
| **主程序** | `src/main.py` | ✅ 完成 |
| **配置管理** | `src/config.py` | ✅ 完成 |

### ✅ 已有文档

- `QUICKSTART.md` - 快速开始指南
- `CODE_REVIEW.md` - 代码审查报告
- `PROGRESS.md` - 进度报告
- `.env.example` - 环境变量示例
- `requirements.txt` - 依赖列表

### ❌ 缺失（发布必需）

| 文件 | 重要性 | 说明 |
|------|:------:|------|
| `README.md` | 🔴 必需 | 项目主页/介绍 |
| `LICENSE` | 🔴 必需 | 开源许可证 |
| `pyproject.toml` | 🔴 必需 | 标准包安装配置 & CLI 入口定义 |
| `requirements.txt` | 🟡 完善 | 补充缺失依赖（如 `python-dotenv`）并固定版本 |
| `CHANGELOG.md` | 🟡 推荐 | 版本变动记录 |
| `CONTRIBUTING.md` | 🟡 推荐 | 贡献指南 |
| `MANIFEST.in` | 🟡 推荐 | 打包文件清单 |

---

## 发布任务清单

### 阶段1：文档准备（必需）

#### 1.1 创建 README.md
**内容结构**：
- 项目标题和徽章（badges）
- 功能特性介绍
- 演示GIF/截图
- 快速安装
- 基本使用
- 配置说明
- 常见问题
- 贡献/许可证链接

#### 1.2 选择并添加 LICENSE
**推荐选项**：
- `MIT` - 最宽松，企业友好
- `Apache 2.0` - 提供专利保护
- `GPL 3.0` - 强制开源

#### 1.3 创建 CHANGELOG.md
```markdown
# Changelog

## [1.0.0] - 2026-01-30
### Added
- 快捷键+剪贴板命令捕获
- AI命令解释（支持DeepSeek/OpenAI）
- 风险评估（4级：低/中/高/严重）
- Rich终端美化输出
- 中英文双语支持
```

---

### 阶段2：包发布配置（必需）

#### 2.1 创建 pyproject.toml（推荐）
通过定义 `[project.scripts]`，将 `python -m src.main` 封装成标准命令 `cli-explainer`。

```toml
[project]
name = "cli-explainer"
version = "1.0.0"
...
dependencies = [
    "pyperclip>=1.8.2",
    "keyboard>=0.13.5",
    "rich>=13.7.0",
    "litellm>=1.40.0",
    "pyyaml>=6.0",
    "click>=8.1.0",
    "python-dotenv>=1.0.0"
]

[project.scripts]
cli-explainer = "src.main:main"
```

#### 2.2 完善依赖管理
- **引入 `python-dotenv`**: 替换现有的手动 `.env` 解析逻辑，提高兼容性。
- **固定版本**: 在 `requirements.txt` 中明确依赖版本，确保环境一致性。
- **创建 MANIFEST.in**: 确保 `config.yaml` 等非代码文件被包含在安装包中。

---

### 阶段3：项目清理

#### 3.1 清理临时/调试文件
需要清理或移入 `.gitignore`：
- `test_output.txt`
- `test_stderr.txt`
- `test_stdout.txt`
- `full_test.log`
- `cli-venv/`（虚拟环境）
- `__pycache__/`

#### 3.2 更新 .gitignore
确保包含：
```gitignore
# 虚拟环境
cli-venv/
venv/
.venv/

# 测试输出
*.log
test_*.txt

# 环境变量
.env

# 缓存
__pycache__/
.pytest_cache/

# 打包产物
dist/
build/
*.egg-info/
```

#### 3.3 整理评估文档
将 `.planning/` 中的开发文档移至单独分支或删除：
- `command_recognition_*.md` → 保留参考或移除
- `CODE_REVIEW.md` → 可保留为开发文档

---

### 阶段4：质量保障

#### 4.1 运行完整测试
```bash
pytest tests/ -v --tb=short
```

#### 4.2 验证安装流程
```bash
# 从干净环境测试
python -m venv test-venv
test-venv\Scripts\activate
pip install -r requirements.txt
python -m src.main "ls -la"
```

#### 4.3 验证文档准确性
- 确认 QUICKSTART.md 步骤可执行
- 确认 README.md 内容准确

---

### 阶段5：可选增强

#### 5.1 创建 CONTRIBUTING.md
- 如何报告Bug
- 如何提交PR
- 代码风格指南
- 测试要求

#### 5.2 添加 GitHub模板（可选）
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/PULL_REQUEST_TEMPLATE.md`

#### 5.3 添加 CI/CD（可选）
- `.github/workflows/test.yml`

---

## 发布前 Checklist

### 必需项 ✅
- [ ] README.md 已创建
- [ ] LICENSE 已选择并添加
- [ ] pyproject.toml 或 setup.py 已创建
- [ ] requirements.txt 依赖完整
- [ ] .gitignore 已更新
- [ ] 临时文件已清理
- [ ] 测试全部通过
- [ ] 安装流程已验证

### 推荐项 📋
- [ ] CHANGELOG.md 已创建
- [ ] CONTRIBUTING.md 已创建
- [ ] 演示截图/GIF已添加

---

## 后续 TODO（v1.1+）

发布后根据用户反馈添加：

| 功能 | 优先级 | 说明 |
|------|:------:|------|
| 可配置命令列表 | 🟡 中 | 用户自定义命令 |
| 执行确认交互 | 🟡 中 | [Y/N]确认 |
| GUI弹窗模式 | 🟢 低 | Tkinter弹窗 |
| AI辅助命令判断 | 🟢 低 | 疑似命令询问AI |
| PyPI发布 | 🟡 中 | pip install cli-explainer |
| 多语言支持 | 🟢 低 | 添加更多语言 |

---

## 预计工作量

| 任务 | 时间估算 |
|------|:--------:|
| 创建 README.md | 30分钟 |
| 添加 LICENSE | 5分钟 |
| 创建 pyproject.toml | 15分钟 |
| 创建 CHANGELOG.md | 10分钟 |
| 清理临时文件 | 10分钟 |
| 更新 .gitignore | 5分钟 |
| 运行测试验证 | 15分钟 |
| **总计** | **约1.5小时** |

---

## 文件结构目标

发布后的项目结构：
```
cli-command-explainer/
├── README.md              ← 新建
├── LICENSE                ← 新建
├── CHANGELOG.md           ← 新建
├── CONTRIBUTING.md        ← 新建（可选）
├── pyproject.toml         ← 新建
├── MANIFEST.in            ← 新建
├── requirements.txt       ← 已有
├── .gitignore             ← 更新
├── .env.example           ← 已有
├── config/
│   └── config.yaml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── capturer/
│   ├── parser/
│   ├── risk/
│   ├── explainer/
│   └── ui/
├── tests/
│   └── ...
└── docs/                  ← 可选
    ├── QUICKSTART.md      ← 移动
    └── ...
```
