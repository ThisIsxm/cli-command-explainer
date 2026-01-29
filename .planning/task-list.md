# 任务分解清单

> **适用范围**：本文档为 **Phase 1（快捷键 + 剪贴板模式）** 的任务分解清单。
> 供后续 Agent 按顺序执行。

---

## 阶段一：项目初始化

### 1.1 创建项目结构
- [ ] 创建 `cli-command-explainer/` 根目录（如不存在）
- [ ] 创建 `src/` 源代码目录及子模块目录
- [ ] 创建 `config/` 配置目录
- [ ] 创建 `tests/` 测试目录
- [ ] 创建各模块 `__init__.py`

### 1.2 配置文件
- [ ] 创建 `requirements.txt`
- [ ] 创建 `config/config.yaml` 默认配置
- [ ] 创建 `.gitignore`

---

## 阶段二：输入捕获模块（扩展性关键）

### 2.1 抽象基类
- [ ] 创建 `src/capturer/__init__.py`
- [ ] 实现 `src/capturer/base.py`
  - [ ] `BaseCapturer` 抽象类
  - [ ] `start(callback)` 抽象方法
  - [ ] `stop()` 抽象方法

### 2.2 剪贴板捕获
- [ ] 实现 `src/capturer/clipboard.py`
  - [ ] `ClipboardCapturer` 类（继承 BaseCapturer）
  - [ ] `get_content()` 方法
  - [ ] `is_command(content)` 方法

### 2.3 快捷键监听
- [ ] 实现 `src/capturer/hotkey.py`
  - [ ] `HotkeyManager` 类
  - [ ] `register(key_combo, callback)` 方法
  - [ ] `start_listening()` 方法
  - [ ] `stop_listening()` 方法

---

## 阶段三：命令解析模块

### 3.1 命令解析器
- [ ] 创建 `src/parser/__init__.py`
- [ ] 实现 `src/parser/command.py`
  - [ ] `CommandParser` 类
  - [ ] `parse(command_str)` 方法
  - [ ] `identify_type(command)` 方法
  - [ ] `extract_args(command)` 方法

### 3.2 危险模式库
- [ ] 创建 `src/parser/patterns.py`
  - [ ] 危险命令正则表达式
  - [ ] 高风险关键词列表
  - [ ] 命令类型映射表

---

## 阶段四：风险评估模块

### 4.1 风险评估器
- [ ] 创建 `src/risk/__init__.py`
- [ ] 实现 `src/risk/assessor.py`
  - [ ] `RiskAssessor` 类
  - [ ] `assess(parsed_command)` 方法
  - [ ] `get_risk_level()` 方法
  - [ ] `get_risk_factors()` 方法
  - [ ] `format_risk_report()` 方法

---

## 阶段五：AI解释引擎

### 5.1 Prompt模板
- [ ] 创建 `src/explainer/__init__.py`
- [ ] 实现 `src/explainer/prompts.py`
  - [ ] 命令解释Prompt模板
  - [ ] JSON输出格式定义
  - [ ] 多语言模板支持

### 5.2 解释引擎
- [ ] 实现 `src/explainer/engine.py`
  - [ ] `ExplainerEngine` 类
  - [ ] `explain(command_str)` 方法
  - [ ] `_call_ai(prompt)` 方法
  - [ ] `_parse_response(response)` 方法
  - [ ] 多AI服务适配器

---

## 阶段六：结果展示模块

### 6.1 终端展示
- [ ] 创建 `src/ui/__init__.py`
- [ ] 实现 `src/ui/display.py`
  - [ ] `DisplayManager` 类
  - [ ] `show_explanation(result)` 方法
  - [ ] `format_risk_badge(level)` 方法
  - [ ] `create_panel(content)` 方法

---

## 阶段七：主程序集成

### 7.1 配置管理
- [ ] 实现 `src/config.py`
  - [ ] `Config` 类
  - [ ] 配置文件加载
  - [ ] 环境变量支持
  - [ ] 默认值处理

### 7.2 入口文件
- [ ] 实现 `src/main.py`
  - [ ] 配置加载
  - [ ] 根据配置选择 Capturer（为 Phase 2 预留）
  - [ ] 模块初始化
  - [ ] 主事件循环
  - [ ] 命令行参数处理

---

## 阶段八：测试

### 8.1 单元测试
- [ ] 创建 `tests/__init__.py`
- [ ] 创建 `tests/test_parser.py`
- [ ] 创建 `tests/test_risk.py`
- [ ] 创建 `tests/test_explainer.py`

### 8.2 集成测试
- [ ] 创建 `tests/test_integration.py`

---

## 阶段九：文档

### 9.1 用户文档
- [ ] 编写 `README.md`
  - [ ] 项目介绍
  - [ ] 安装指南
  - [ ] 使用说明
  - [ ] 配置说明

---

## 执行优先级

```
高优先级（核心功能）：
├── 2.1 抽象基类 (扩展性关键)
├── 2.2 剪贴板捕获
├── 2.3 快捷键监听
├── 3.1 命令解析器
├── 4.1 风险评估器
├── 5.1 Prompt模板
├── 5.2 解释引擎
└── 7.2 入口文件

中优先级（完善功能）：
├── 3.2 危险模式库
├── 6.1 终端展示
└── 7.1 配置管理

低优先级（质量保障）：
├── 8.x 测试
└── 9.x 文档
```

---

## 注意事项

1. **API密钥安全**：不要在代码中硬编码API密钥，使用环境变量
2. **错误处理**：每个模块都应有完善的异常处理
3. **日志记录**：添加适当的日志便于调试
4. **代码风格**：遵循PEP8规范
5. **类型注解**：使用Python类型注解提高代码可读性
6. **扩展性**：严格遵循 `BaseCapturer` 接口设计，确保 Phase 2 可平滑扩展

---

## Phase 2 预留任务（当前阶段不执行）

以下任务在 Phase 1 中**仅预留接口**，不实现具体功能：

- [ ] `src/capturer/terminal_proxy.py`
  - [ ] `TerminalProxyCapturer` 类（继承 BaseCapturer）
  - [ ] PTY 启动和管理
  - [ ] 输出流实时捕获
  - [ ] 待确认命令识别
