# 项目改进实施计划

## 背景

基于用户反馈和代码审查，发现以下问题需要改进：
1. **命令识别不完整**：`ufw`, `systemctl` 等常用命令无法识别
2. **无法支持自定义命令**：用户项目特定命令无法识别
3. **缺少执行确认交互**：用户看完解释后没有后续操作

## 改进目标

### 短期目标（本周）
- ✅ 修复命令识别问题 - 扩充70+个常用命令
- 🔄 实现可配置自定义命令列表

### 中期目标（2周内）
- 添加执行确认交互（UI改进）
- 完善文档和测试

---

## 改进1：扩充静态命令列表

### 目标
将命令覆盖率从 90% → 95%，从80个增加到150+个常用命令。

### 代码变更

#### 修改文件：[src/capturer/clipboard.py](file:///c:/01_WorkSpace/07_/cli-command-explainer/src/capturer/clipboard.py)

**位置**：`is_command()` 方法中的 `command_prefixes` 列表

**新增命令分类**：
```python
# 编辑器（7个）
'vim', 'nvim', 'nano', 'emacs', 'code', 'subl', 'gedit',

# 版本控制（4个）
'svn', 'hg', 'fossil', 'bzr',

# 构建工具（6个）
'mvn', 'gradle', 'ant', 'sbt', 'bazel', 'ninja',

# 数据库（5个）
'mysql', 'psql', 'sqlite3', 'mongo', 'redis-cli',

# 监控工具（6个）
'watch', 'strace', 'lsof', 'netcat', 'tcpdump', 'wireshark',

# 容器/虚拟化（4个）
'vagrant', 'virtualbox', 'lxc', 'qemu',

# 包管理（语言特定）（6个）
'gem', 'bundler', 'composer', 'nuget', 'mix', 'pub',

# 系统工具（11个）
'killall', 'pkill', 'crontab', 'at', 'batch', 
'nice', 'renice', 'nohup', 'screen', 'bg', 'fg', 'jobs',

# 磁盘工具（6个）
'fdisk', 'parted', 'mkfs', 'mount', 'umount', 'fsck',

# 用户管理（5个）
'useradd', 'userdel', 'usermod', 'groupadd', 'passwd',

# 其他常用工具（10+个）
'awk', 'od', 'xxd', 'diff', 'patch', 'xargs', 
'env', 'export', 'source', 'alias', 'history',
```

**总计新增**：约70个命令

### 验证方案

#### 自动化测试

创建测试文件验证新增命令识别：

**文件**：`tests/test_command_recognition.py`

```python
import pytest
from src.capturer.clipboard import ClipboardCapturer

def test_new_commands_recognition():
    """测试新增加的命令是否能被识别"""
    capturer = ClipboardCapturer()
    
    # 编辑器
    assert capturer.is_command("vim test.py") == True
    assert capturer.is_command("code .") == True
    
    # 版本控制
    assert capturer.is_command("svn commit") == True
    assert capturer.is_command("hg pull") == True
    
    # 构建工具
    assert capturer.is_command("mvn clean install") == True
    assert capturer.is_command("gradle build") == True
    
    # 数据库
    assert capturer.is_command("mysql -u root") == True
    assert capturer.is_command("psql mydatabase") == True
    
    # 监控工具
    assert capturer.is_command("watch ls") == True
    assert capturer.is_command("strace python app.py") == True
    
    # 系统工具
    assert capturer.is_command("killall process") == True
    assert capturer.is_command("crontab -e") == True
    assert capturer.is_command("tmux new -s mysession") == True
    
    # 磁盘工具
    assert capturer.is_command("fdisk -l") == True
    assert capturer.is_command("mount /dev/sda1") == True
    
    # 用户管理
    assert capturer.is_command("useradd newuser") == True
    assert capturer.is_command("passwd username") == True

def test_still_reject_non_commands():
    """确保不会误判非命令"""
    capturer = ClipboardCapturer()
    
    assert capturer.is_command("hello-world") == False
    assert capturer.is_command("just some text") == False
    assert capturer.is_command("这是中文-测试") == False
```

**运行测试**：
```bash
cd c:\01_WorkSpace\07_\cli-command-explainer
python -m pytest tests/test_command_recognition.py -v
```

#### 手动测试

使用 `test_ai_chain.py` 测试之前失败的命令：

```bash
# 测试之前失败的命令
1. 复制 "ufw default allow"
2. 按 Ctrl+Shift+E
3. 验证：应该触发解释

4. 复制 "ufw status"
5. 按 Ctrl+Shift+E
6. 验证：应该触发解释

7. 复制 "systemctl status nginx"
8. 按 Ctrl+Shift+E
9. 验证：应该触发解释

10. 复制 "tmux new -s test"
11. 按 Ctrl+Shift+E
12. 验证：应该触发解释
```

---

## 改进2：实现可配置自定义命令列表

### 目标
允许用户在 `config.yaml` 中添加自定义命令，覆盖率从 95% → 98%。

### 代码变更

#### 1. 修改文件：[config.yaml](file:///c:/01_WorkSpace/07_/cli-command-explainer/config.yaml)

**新增配置项**：
```yaml
# 在 capturer 节点下添加
capturer:
  mode: keyboard  # keyboard | clipboard
  hotkey: ctrl+shift+E
  
  # 新增：用户自定义命令列表
 custom_commands:
    # - mycommand    # 示例：添加您的自定义命令
    # - deploy
    # - build
  
  # 新增：命令别名映射（可选）
  command_aliases:
    # dc: docker-compose  # 示例：dc 等同于 docker-compose
    # k: kubectl
```

#### 2. 修改文件：[src/config.py](file:///c:/01_WorkSpace/07_/cli-command-explainer/src/config.py)

**确保配置类支持嵌套字典访问**：
```python
@property
def custom_commands(self) -> list:
    """获取用户自定义命令列表"""
    return self._config.get('capturer', {}).get('custom_commands', [])

@property
def command_aliases(self) -> dict:
    """获取命令别名映射"""
    return self._config.get('capturer', {}).get('command_aliases', {})
```

#### 3. 修改文件：[src/capturer/clipboard.py](file:///c:/01_WorkSpace/07_/cli-command-explainer/src/capturer/clipboard.py)

**变更1**：修改构造函数接收配置

```python
class ClipboardCapturer(BaseCapturer):
    def __init__(self, config=None) -> None:
        super().__init__(name="clipboard")
        self._last_content: Optional[str] = None
        self._config = config  # 新增：保存配置对象
```

**变更2**：修改 `is_command()` 方法

在现有逻辑**之后**添加（第150行左右）：

```python
def is_command(self, content: Optional[str]) -> bool:
    # ... 现有静态列表检查逻辑 ...
    
    # === 新增：检查用户自定义命令 ===
    if self._config:
        # 自定义命令列表
        custom_commands = self._config.get('capturer', {}).get('custom_commands', [])
        if first_word in custom_commands:
            return True
        
        # 命令别名
        aliases = self._config.get('capturer', {}).get('command_aliases', {})
        if first_word in aliases:
            return True
    
    return False
```

#### 4. 修改文件：主程序入口（需要查找main.py或启动脚本）

**传递配置给 ClipboardCapturer**：
```python
# 之前
capturer = ClipboardCapturer()

# 之后
capturer = ClipboardCapturer(config=config._config)
```

### 验证方案

#### 自动化测试

**文件**：`tests/test_custom_commands.py`

```python
import pytest
import tempfile
import yaml
from pathlib import Path
from src.config import Config
from src.capturer.clipboard import ClipboardCapturer

def test_custom_commands():
    """测试自定义命令识别"""
    # 创建临时配置文件
    config_data = {
        'capturer': {
            'custom_commands': ['mycommand', 'deploy', 'build']
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        # 加载配置
        config = Config(config_path)
        capturer = ClipboardCapturer(config=config._config)
        
        # 测试自定义命令
        assert capturer.is_command("mycommand --option") == True
        assert capturer.is_command("deploy prod") == True
        assert capturer.is_command("build --release") == True
        
        # 测试仍然识别标准命令
        assert capturer.is_command("git status") == True
    finally:
        Path(config_path).unlink()

def test_command_aliases():
    """测试命令别名"""
    config_data = {
        'capturer': {
            'command_aliases': {
                'dc': 'docker-compose',
                'k': 'kubectl'
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        config = Config(config_path)
        capturer = ClipboardCapturer(config=config._config)
        
        # 测试别名
        assert capturer.is_command("dc up") == True
        assert capturer.is_command("k get pods") == True
    finally:
        Path(config_path).unlink()
```

**运行测试**：
```bash
python -m pytest tests/test_custom_commands.py -v
```

#### 手动测试

1. **编辑配置文件** `config.yaml`：
```yaml
capturer:
  custom_commands:
    - myapp
    - deploy
```

2. **重启程序并测试**：
```bash
# 启动程序
python src/main.py  # 或实际启动命令

# 测试
1. 复制 "myapp --config prod"
2. 按 Ctrl+Shift+E
3. 验证：应该触发解释

4. 复制 "deploy staging"
5. 按 Ctrl+Shift+E
6. 验证：应该触发解释
```

---

## 用户审查要点

### ⚠️ 需要确认的事项

1. **主程序入口位置**
   - 当前项目的启动脚本是哪个文件？
   - 是否是 `src/main.py`？
   - 需要在哪里修改才能传递配置给 `ClipboardCapturer`？

2. **测试方式确认**
   - 是否有现有的测试框架？
   - 自动化测试方案是否可行？
   - 手动测试步骤是否清晰？

### ✅ 无需确认的改进

- 扩充静态命令列表（已在代码中完成）
- 配置文件结构设计（向后兼容）

---

## 实施顺序

1. **立即执行**：扩充静态命令列表
   - 修改 `clipboard.py`
   - 运行测试验证

2. **本周完成**：实现可配置列表
   - 更新 `config.yaml`
   - 修改 `config.py`
   - 修改 `clipboard.py`
   - 更新主程序入口
   - 编写测试
   - 更新文档

3. **下周**：UI改进（执行确认交互）

---

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 新增命令过多影响性能 | 低 | 使用集合查找（O(1)） |
| 配置文件兼容性 | 低 | 使用 `.get()` 提供默认值 |
| 测试覆盖不足 | 中 | 增加边界情况测试 |

---

## 后续计划

完成上述改进后，建议按以下顺序继续优化：

1. UI改进 - 添加执行确认交互
2. 完善文档 - 更新 README 和配置说明
3. 可选功能 - AI辅助判断、学习模式
