# 详细实施计划

> **适用范围**：本文档为 **Phase 1（快捷键 + 剪贴板模式）** 的详细实施计划。
> Phase 2（终端代理模式）的实施计划将在 Phase 1 完成后另行制定。

---

## 一、项目初始化（第1天）

### 1.1 环境搭建
- [ ] 创建Python项目结构
- [ ] 初始化虚拟环境
- [ ] 创建 requirements.txt
- [ ] 创建基础配置文件

### 1.2 依赖清单
```
pyperclip      # 剪贴板操作
keyboard       # 快捷键监听
rich           # 终端美化输出
litellm        # 统一AI接口
pyyaml         # 配置文件解析
click          # CLI框架
```

---

## 二、输入捕获模块（第2天）

> **扩展性设计**：采用策略模式，定义 `BaseCapturer` 抽象接口，为 Phase 2 预留扩展点。

### 2.1 抽象基类

**文件**：`src/capturer/base.py`

实现内容：
- `BaseCapturer` 抽象类
- `start(callback)` 抽象方法
- `stop()` 抽象方法

### 2.2 剪贴板捕获

**文件**：`src/capturer/clipboard.py`

实现内容：
- `ClipboardCapturer` 类（继承 `BaseCapturer`）
- `get_content()` 方法
- `is_command(content)` 方法

### 2.3 快捷键监听

**文件**：`src/capturer/hotkey.py`

实现内容：
- `HotkeyManager` 类
- `register(key_combo, callback)` 方法
- `start_listening()` 方法
- `stop_listening()` 方法

---

## 三、命令解析模块（第2-3天）

### 3.1 命令解析器

**文件**：`src/parser/command.py`

实现内容：
- 命令字符串预处理
- 命令类型识别（shell/git/npm/pip等）
- 命令结构解析（命令、选项、参数）
- 常见命令模式匹配

### 3.2 危险模式库

**文件**：`src/parser/patterns.py`

实现内容：
- 危险命令模式库（正则表达式）
- 高风险操作关键词
- 命令类型特征库

---

## 四、风险评估模块（第3天）

**文件**：`src/risk/assessor.py`

实现内容：
- 基于规则的快速预评估
- 风险等级计算算法
- 风险因素权重配置
- 风险说明生成

---

## 五、AI解释引擎（第3-4天）

### 5.1 Prompt模板

**文件**：`src/explainer/prompts.py`

实现内容：
- 命令解释Prompt模板
- 结构化输出格式定义（JSON Schema）
- 多语言支持模板

### 5.2 解释引擎

**文件**：`src/explainer/engine.py`

实现内容：
- AI服务接口封装（使用LiteLLM）
- 多AI服务支持（OpenAI/OpenRouter/Ollama）
- 响应解析和验证
- 错误处理和重试

---

## 六、结果展示模块（第4天）

**文件**：`src/ui/display.py`

实现内容：
- Rich格式化输出
- 风险等级颜色编码
- 结构化信息展示
- 终端通知

---

## 七、主程序集成（第5天）

### 7.1 入口文件

**文件**：`src/main.py`

实现内容：
- 模块整合
- 主工作流程
- 命令行参数处理
- 配置文件加载

### 7.2 配置管理

**文件**：`src/config.py`

实现内容：
- `Config` 类
- 配置文件加载
- 环境变量支持
- 默认值处理

### 7.3 配置文件

**文件**：`config/config.yaml`

配置项：
```yaml
# 输入模式配置 (为Phase 2预留)
capturer:
  mode: clipboard  # clipboard / terminal_proxy (Phase 2)

# AI服务配置
ai:
  provider: openai  # openai / openrouter / ollama
  api_key: ${OPENAI_API_KEY}
  model: gpt-4

# 快捷键配置
hotkey:
  trigger: ctrl+shift+e

# 显示配置
display:
  language: zh  # zh / en
  show_details: true

# 风险评估配置
risk:
  enable_ai_assessment: true
  local_precheck: true
```

### 7.4 错误处理
- AI服务不可用时的降级策略（仅显示本地预评估）
- 剪贴板访问失败处理
- 配置文件错误处理

---

## 八、测试与文档（第6天）

### 8.1 单元测试
- 命令解析器测试
- 风险评估器测试
- Prompt模板测试

### 8.2 集成测试
- 端到端工作流测试
- 多AI服务测试

### 8.3 文档编写
- README.md 使用说明
- 配置指南
- 常见问题解答

---

## 验证计划

### 自动化测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_parser.py -v
pytest tests/test_risk.py -v
pytest tests/test_explainer.py -v
```

### 手动测试用例

| 测试场景 | 输入命令 | 预期结果 |
|----------|----------|----------|
| 安全命令 | `ls -la` | 🟢 低风险，只读操作 |
| 安装命令 | `npm install lodash` | 🟡 中风险，网络下载 |
| 删除命令 | `rm -rf node_modules` | 🟠 高风险，删除目录 |
| 危险命令 | `rm -rf /` | 🔴 危险，可能导致系统损坏 |
| Git推送 | `git push --force` | 🟠 高风险，可能丢失历史 |

### 手动验证步骤
1. 启动程序：`python src/main.py`
2. 复制测试命令到剪贴板
3. 按下快捷键（默认 Ctrl+Shift+E）
4. 检查解释输出是否正确
5. 验证风险等级是否合理

---

## Phase 2 扩展预留检查清单

在 Phase 1 开发过程中，确保以下扩展点正确实现：

- [ ] `BaseCapturer` 抽象类已定义
- [ ] `ClipboardCapturer` 正确实现接口
- [ ] `config.yaml` 包含 `capturer.mode` 字段
- [ ] 主程序根据配置决定使用哪个 Capturer
- [ ] 日志系统可复用
