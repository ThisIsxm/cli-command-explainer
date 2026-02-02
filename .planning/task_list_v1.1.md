# 项目改进任务清单

## 已完成 ✅

### Phase 1 - 核心功能
- [x] 项目结构创建
- [x] 配置文件（`config.yaml`, `requirements.txt`）
- [x] 输入捕获模块抽象基类（`BaseCapturer`）
- [x] 剪贴板捕获器（`ClipboardCapturer`）
- [x] 快捷键监听（`HotkeyManager`）
- [x] 命令解析器（`CommandParser`）
- [x] 危险模式库（`PatternMatcher`）
- [x] 风险评估器（`RiskAssessor`）
- [x] AI Prompt模板（`PromptTemplate`）
- [x] AI解释引擎（`AIExplainer`）
- [x] UI展示模块（`ResultDisplay`，使用Rich库）
- [x] 配置管理（`Config`）

### 问题修复
- [x] 修复命令识别逻辑（扩展列表，修复连字符误判）
- [x] 代码审查完成

---

## 当前改进任务 🚧

### 改进1：扩充静态命令列表
**优先级**：🔴 高

- [/] 扩充 `clipboard.py` 的命令列表
  - [x] 第一批扩充（添加 ufw, systemctl 等80+个）
  - [ ] 第二批扩充（再添加70+个）
    - [ ] 编辑器类：vim, nvim, nano, emacs, code, subl, gedit
    - [ ] 版本控制：svn, hg, fossil, bzr
    - [ ] 构建工具：mvn, gradle, ant, sbt, bazel, ninja
    - [ ] 数据库：mysql, psql, sqlite3, mongo, redis-cli
    - [ ] 监控工具：watch, strace, lsof, netcat, tcpdump, wireshark
    - [ ] 容器/虚拟化：vagrant, virtualbox, lxc, qemu
    - [ ] 包管理（语言特定）：gem, bundler, composer, nuget, mix, pub
    - [ ] 系统工具：killall, pkill, crontab, at, batch, nice, renice, nohup, screen, tmux, bg, fg, jobs
    - [ ] 磁盘工具：fdisk, parted, mkfs, mount, umount, fsck
    - [ ] 用户管理：useradd, userdel, usermod, groupadd, passwd
  - [ ] 测试新增命令的识别率

**目标**：覆盖率从90% → 95%

---

### 改进2：实现可配置自定义命令列表
**优先级**：🟡 中

- [ ] 更新 `config.yaml` 结构
  - [ ] 添加 `capturer.custom_commands` 配置项
  - [ ] 添加 `capturer.command_aliases` 配置项（可选）
  - [ ] 添加 `capturer.recognition_mode` 配置项

- [ ] 修改 `clipboard.py`
  - [ ] 在 `__init__` 中接收配置对象
  - [ ] 在 `is_command()` 中读取自定义命令列表
  - [ ] 支持命令别名映射

- [ ] 更新 `README.md`
  - [ ] 添加自定义命令配置说明
  - [ ] 提供配置示例

**目标**：覆盖率从95% → 98%

---

## 待办事项 📝

### UI改进（基于评估报告）
**优先级**：🟡 中

- [ ] 添加执行确认交互
  - [ ] 在 `display.py` 添加 `prompt_confirmation()` 方法
  - [ ] 支持 [Y/N] 确认输入
  - [ ] 返回用户选择

- [ ] 实现风险分级显示策略
  - [ ] 低风险：一行摘要 + 直接确认
  - [ ] 中风险：摘要 + 警告 + 确认
  - [ ] 高风险：全量展示 + 延迟确认
  - [ ] 严重风险：全量展示 + 二次确认

- [ ] （可选）实现GUI弹窗模式
  - [ ] 使用 Tkinter 实现弹窗
  - [ ] 添加配置项选择显示模式
  - [ ] 支持 inline | gui 模式切换

---

### 测试完善
**优先级**：🟢 低

- [ ] 扩充单元测试
  - [ ] 测试新增加的命令识别
  - [ ] 测试自定义命令配置加载
  - [ ] 测试边界情况

- [ ] 集成测试
  - [ ] 端到端测试整个流程
  - [ ] 测试不同AI服务提供商

---

### 文档完善
**优先级**：🟢 低

- [ ] 更新 `README.md`
  - [ ] 添加最新功能说明
  - [ ] 更新使用示例
  - [ ] 添加故障排除

- [ ] 编写 `CONTRIBUTING.md`
  - [ ] 贡献指南
  - [ ] 代码规范
  - [ ] PR流程

---

## 未来规划 🔮

### Phase 1.5: 高级功能（可选）

- [ ] AI辅助命令判断
  - [ ] 实现 `_ask_ai_if_command()` 方法
  - [ ] 添加频率限制和缓存
  - [ ] 添加配置开关（默认禁用）
  - [ ] 成本控制：月均 < $0.05

- [ ] 学习模式
  - [ ] 记录用户确认的命令
  - [ ] 自动添加到自定义列表
  - [ ] 提供"未知命令"反馈机制

- [ ] 命令使用统计
  - [ ] 记录命令使用频率
  - [ ] 提示高频自定义命令添加到配置

- [ ] 社区命令库
  - [ ] 支持下载预定义命令包（如 k8s, aws）
  - [ ] `cli-explainer install-commands <category>`

---

### Phase 2: 自动终端监控（需用户需求驱动）

当前采用快捷键+剪贴板方案已满足基本需求。如有强烈自动化需求，可实施：

- [ ] 终端代理模式（PTY Wrapper）
  - [ ] 实现 `TerminalProxyCapturer`
  - [ ] 处理Windows ConPTY
  - [ ] 实时捕获输出流
  - [ ] 识别待确认命令模式

**评估**：
- 实现复杂度：⭐⭐⭐⭐⭐ 极高
- 用户体验提升：⭐⭐⭐⭐
- 建议：先通过Phase 1验证需求，确认有持续需求后再投入

---

## 执行优先级总结

```
🔴 立即执行（本周）：
├── 扩充静态命令列表第二批（70+个命令）
└── 测试验证识别率

🟡 短期目标（2周内）：
├── 实现可配置自定义命令列表
├── 添加执行确认交互（UI改进）
└── 更新用户文档

🟢 长期优化（按需）：
├── GUI弹窗模式
├── AI辅助判断（可选）
├── 学习模式
└── 社区命令库
```

---

## 变更记录

| 日期 | 变更内容 | 原因 |
|------|---------|------|
| 2026-01-30 | 扩充命令列表（第一批80+个） | 修复 ufw, systemctl 等命令无法识别 |
| 2026-01-30 | 修复连字符误判逻辑 | 避免普通文本被误判为命令 |
| 2026-01-30 | 规划可配置命令列表功能 | 支持用户自定义命令 |
| 2026-01-30 | 规划UI改进方案 | 基于UI展示评估报告 |
