# 命令识别改进方案

## 问题分析

### 识别失败的案例
```
❌ ufw default allow      - 没有被识别
❌ ufw status            - 没有被识别
✅ sudo iwlist scan      - 成功识别（因为有 'sudo '）
✅ apt -get dist-upgrade - 成功识别（因为有 'apt '，但命令本身是错误的）
```

### 根本原因

**当前 `is_command()` 逻辑（src/capturer/clipboard.py）**：

1. **硬编码命令列表不完整**（第81-90行）
   - 缺少 `ufw`, `systemctl`, `service`, `iptables` 等常用命令
   
2. **连字符检查过于宽泛**（第97-98行）
   ```python
   if '--' in content or '-' in content:
       return True
   ```
   这会误判任何包含连字符的普通文本！

3. **缺少对命令结构的验证**
   - 没有检查第一个单词是否是有效的命令

---

## 改进方案

### 方案一：扩展命令列表 + 改进参数检测（推荐）

**核心思路**：
1. 大幅扩展已知命令列表
2. 修复连字符检测逻辑（只在首单词是潜在命令时检查）
3. 添加更智能的命令特征检测

**优点**：
- ✅ 实现简单
- ✅ 立即解决当前问题
- ✅ 误判率低

**缺点**：
- ⚠️ 需要维护命令列表
- ⚠️ 无法识别自定义命令

---

### 方案二：基于PATH的动态检测（高级）

**核心思路**：
1. 读取系统 PATH 环境变量
2. 检查首单词是否存在于系统可执行文件中
3. 结合语法特征辅助判断

**优点**：
- ✅ 能识别所有系统命令
- ✅ 能识别自定义脚本

**缺点**：
- ⚠️ Windows/Linux/Mac 的PATH解析不同
- ⚠️ 性能开销
- ⚠️ 可能误判同名的非命令词

---

### 方案三：混合策略（最佳）

结合方案一和方案二：
1. **首先**检查已知命令列表（快速路径）
2. **其次**检查常见命令特征（参数、路径等）
3. **最后**查询系统PATH（慢速回退方案）

---

## 推荐实现

### 修改 `is_command()` 方法

```python
def is_command(self, content: Optional[str]) -> bool:
    """判断内容是否为有效的命令
    
    改进点:
    1. 扩展命令列表
    2. 修复连字符检测逻辑
    3. 添加更多命令特征
    """
    if not content:
        return False

    content = content.strip()
    if not content or '\n' in content:
        return False

    # 分割第一个单词
    parts = content.split()
    if not parts:
        return False
    
    first_word = parts[0].lower()

    # === 1. 常见命令前缀检查 ===
    command_prefixes = [
        # 系统管理
        'sudo', 'su', 'doas',
        # 包管理
        'apt', 'apt-get', 'yum', 'dnf', 'pacman', 'zypper',
        'brew', 'choco', 'winget', 'scoop',
        # 开发工具
        'git', 'npm', 'yarn', 'pnpm', 'pip', 'pipenv', 'poetry',
        'cargo', 'go', 'rustc', 'gcc', 'clang', 'make', 'cmake',
        'docker', 'docker-compose', 'podman', 'kubectl', 'helm',
        'node', 'python', 'python3', 'ruby', 'php', 'java', 'javac',
        # 文件操作
        'ls', 'cd', 'pwd', 'cp', 'mv', 'rm', 'mkdir', 'rmdir',
        'cat', 'less', 'more', 'head', 'tail', 'touch', 'ln',
        'chmod', 'chown', 'chgrp',
        # 文本处理
        'grep', 'sed', 'awk', 'cut', 'sort', 'uniq', 'wc', 'tr',
        'find', 'locate', 'which', 'whereis',
        # 网络工具
        'curl', 'wget', 'ping', 'traceroute', 'netstat', 'ss',
        'ip', 'ifconfig', 'nslookup', 'dig', 'host',
        'ssh', 'scp', 'sftp', 'rsync', 'nc', 'telnet',
        # 系统信息
        'ps', 'top', 'htop', 'free', 'df', 'du', 'uname', 'hostname',
        'uptime', 'whoami', 'id', 'groups', 'last', 'w',
        # 压缩解压
        'tar', 'gzip', 'gunzip', 'zip', 'unzip', '7z', 'rar', 'unrar',
        # 防火墙/安全
        'ufw', 'iptables', 'firewalld', 'firewall-cmd',
        'setenforce', 'getenforce', 'apparmor',
        # 服务管理
        'systemctl', 'service', 'systemd', 'journalctl',
        'rc-service', 'rc-update',
        # 无线网络
        'iwlist', 'iwconfig', 'iw', 'nmcli', 'nmtui',
        'wpa_supplicant', 'wpa_cli',
        # Windows命令
        'cmd', 'powershell', 'pwsh', 'wsl',
    ]

    for prefix in command_prefixes:
        if first_word == prefix or content.startswith(prefix + ' '):
            return True

    # === 2. 独立命令检查 ===
    standalone_commands = [
        'ls', 'pwd', 'clear', 'exit', 'history', 'help',
        'git', 'npm', 'pip', 'yarn', 'cargo', 'docker', 'kubectl',
        'make', 'cmake', 'vim', 'nano', 'emacs', 'code',
    ]
    if first_word in standalone_commands:
        return True

    # === 3. 命令参数模式检查（更严格）===
    # 只有当第二个词是参数时才认为可能是命令
    if len(parts) >= 2:
        second_word = parts[1]
        # 检查第二个词是否是标准参数格式
        if second_word.startswith('-') or second_word.startswith('--'):
            # 排除明显的非命令（如 "some-文本" 这种连字符分隔的普通文本）
            # 命令参数通常很短，且不含中文
            if len(second_word) <= 20 and not any('\u4e00' <= c <= '\u9fff' for c in second_word):
                return True

    # === 4. 路径特征检查 ===
    # 包含 ./ 或 / 开头，且以可执行文件结尾
    if first_word.startswith('./') or first_word.startswith('/'):
        return True
    
    # Windows 路径
    if first_word.startswith('.\\') or (len(first_word) > 2 and first_word[1] == ':'):
        return True

    # === 5. 脚本文件扩展名 ===
    script_extensions = ['.sh', '.py', '.rb', '.pl', '.js', '.bat', '.cmd', '.ps1']
    if any(first_word.endswith(ext) for ext in script_extensions):
        return True

    return False
```

---

## 测试用例

### 应该识别的命令
```python
assert is_command("ufw default allow") == True          # ✅ Fix: 添加 ufw
assert is_command("ufw status") == True                 # ✅ Fix: 添加 ufw
assert is_command("sudo iwlist scan") == True           # ✅ 原有功能
assert is_command("systemctl status nginx") == True     # ✅ Fix: 添加 systemctl
assert is_command("ls -la") == True                     # ✅ 原有功能
assert is_command("git commit -m 'test'") == True       # ✅ 原有功能
assert is_command("./build.sh") == True                 # ✅ 脚本文件
assert is_command("python script.py") == True           # ✅ 原有功能
```

### 不应该识别的内容
```python
assert is_command("这是一段-普通文本") == False         # ✅ Fix: 修复连字符误判
assert is_command("hello-world") == False               # ✅ Fix: 普通连字符文本
assert is_command("some random text") == False          # ✅ 原有功能
assert is_command("") == False                          # ✅ 空字符串
assert is_command("line1\nline2") == False              # ✅ 多行文本
```

### 边界情况
```python
assert is_command("apt -get") == True   # ⚠️ 虽然命令有误，但应识别为命令
assert is_command("rm-old") == False    # ✅ 不是命令，只是包含连字符的词
```

---

## 额外改进建议

### 1. 添加命令纠错提示

当识别到可疑命令（如 `apt -get`）时，提示用户：

```python
if first_word == "apt" and len(parts) >= 2 and parts[1] == "-get":
    # 在解释中添加警告
    warnings.append("⚠️ 您是否想输入 'apt-get' 而不是 'apt -get'？")
```

### 2. 可配置的命令列表

允许用户在配置文件中添加自定义命令：

```yaml
# config.yaml
capturer:
  custom_commands:
    - mycommand
    - deploy
    - build
```

### 3. 学习模式（高级）

记录用户确认过的命令，自动扩展识别列表：

```python
# 在 ~/.cli-explainer/learned_commands.txt 中保存
def save_confirmed_command(command: str):
    first_word = command.split()[0]
    # 保存到本地数据库
```

---

## 实施优先级

| 改进项 | 优先级 | 工作量 |
|--------|:------:|:------:|
| 扩展命令列表 | 🔴 高 | ⭐ 低 |
| 修复连字符检测 | 🔴 高 | ⭐ 低 |
| 添加脚本扩展名检测 | 🟡 中 | ⭐ 低 |
| 命令纠错提示 | 🟡 中 | ⭐⭐ 中 |
| 可配置命令列表 | 🟢 低 | ⭐⭐ 中 |
| 学习模式 | 🟢 低 | ⭐⭐⭐ 高 |

---

## 下一步行动

1. ✅ 修改 `src/capturer/clipboard.py` 的 `is_command()` 方法
2. ✅ 添加单元测试验证修复
3. ✅ 测试之前失败的命令（ufw, systemctl等）
4. 🔄 考虑添加命令纠错功能
5. 🔄 添加可配置的自定义命令支持
