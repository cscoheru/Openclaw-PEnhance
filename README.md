# OpenClaw-PEnhance

**Claude Code 编程增强方案** - 通过 OpenClaw Gateway 和 GLM-4 Plus 增强编程能力

---

## 概述

PEnhance 是一个编程增强 Skill，提供三大核心能力：

1. **记忆增强 (Memory Enhancer)** - 自动保存上下文，防止溢出
2. **计划匹配 (Plan Match Enforcer)** - 监控代码与计划的匹配，防止任务漂移
3. **算法增强 (Algorithm Enhancer)** - 识别、分析和优化复杂算法

---

## 架构

```
Claude Code (本地)
       │
       ▼
OpenClaw Gateway (A节点 - 阿里云)
ws://139.224.42.111:18789
       │
       ▼
GLM-4 Plus (智谱)
128K 上下文窗口
```

---

## 快速开始

### 1. 配置环境变量

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
export OPENCLAW_AUTH_TOKEN="your_auth_token"
```

### 2. 验证连接

```bash
curl -H "Authorization: Bearer $OPENCLAW_AUTH_TOKEN" \
  http://139.224.42.111:18789/health
```

### 3. 使用脚本

```bash
# 记忆管理
python3 skills/penhance/scripts/memory-manager.py list

# 计划执行
python3 skills/penhance/scripts/plan-enforcer.py --help

# 算法分析
python3 skills/penhance/scripts/algorithm-analyzer.py --help
```

---

## 目录结构

```
OpenClaw-PEnhance/
├── PLAN.md                    # 完整计划文档
├── README.md                  # 本文件
├── config/                    # 配置文件
│   ├── openclaw-config.json   # OpenClaw 连接配置
│   ├── memory-config.json     # 记忆增强配置
│   ├── plan-config.json       # 计划匹配配置
│   └── algorithm-config.json  # 算法增强配置
├── skills/                    # Skill 定义
│   └── penhance/
│       ├── SKILL.md           # 主 Skill 定义
│       ├── scripts/           # 辅助脚本
│       └── references/        # 参考文档
├── memory/                    # 记忆存储
│   ├── sessions/              # 会话记忆
│   ├── plans/                 # 开发计划
│   ├── algorithms/            # 算法库
│   └── context/               # 上下文快照
├── templates/                 # 模板文件
│   ├── plan-template.md       # 计划模板
│   ├── session-template.json  # 会话模板
│   └── algorithm-template.md  # 算法模板
└── logs/                      # 日志目录
```

---

## 核心功能

### 记忆增强

```bash
# 保存当前上下文
python3 skills/penhance/scripts/memory-manager.py save --data '{"currentTask": "..."}'

# 列出所有会话
python3 skills/penhance/scripts/memory-manager.py list

# 加载指定会话
python3 skills/penhance/scripts/memory-manager.py load --session-id <id>
```

### 计划匹配

```bash
# 加载开发计划
python3 skills/penhance/scripts/plan-enforcer.py load --plan path/to/plan.md

# 分析代码变更
python3 skills/penhance/scripts/plan-enforcer.py analyze --change "添加用户认证"

# 检查偏离
python3 skills/penhance/scripts/plan-enforcer.py deviation

# 获取建议
python3 skills/penhance/scripts/plan-enforcer.py suggest
```

### 算法分析

```bash
# 分析代码中的算法
python3 skills/penhance/scripts/algorithm-analyzer.py analyze --code "def quicksort(arr): ..."

# 从文件分析
python3 skills/penhance/scripts/algorithm-analyzer.py analyze --file path/to/code.py

# 保存分析结果
python3 skills/penhance/scripts/algorithm-analyzer.py save --file path/to/code.py
```

---

## 配置说明

### OpenClaw 连接

编辑 `config/openclaw-config.json`:

```json
{
  "gateway": {
    "url": "ws://139.224.42.111:18789",
    "authToken": "${OPENCLAW_AUTH_TOKEN}"
  }
}
```

### 记忆配置

编辑 `config/memory-config.json`:

```json
{
  "contextThreshold": 100000,  // 上下文阈值
  "retentionDays": 30,          // 保留天数
  "compressionEnabled": true    // 启用压缩
}
```

### 计划配置

编辑 `config/plan-config.json`:

```json
{
  "enforcement": {
    "strictMode": true,         // 严格模式
    "allowDeviation": false     // 允许偏离
  },
  "deviationHandling": {
    "warnThreshold": 0.3,       // 警告阈值
    "blockThreshold": 0.5       // 阻止阈值
  }
}
```

---

## 与 Claude Code 集成

### 方法 1: 自定义命令

在 `~/.claude/commands/` 创建 `penhance.md`:

```markdown
---
description: Programming Enhancement with OpenClaw + GLM-4 Plus
---

使用 PEnhance Skill 增强编程能力。
```

### 方法 2: Hook 自动触发

在 `~/.claude/settings.json` 添加:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": ["/Users/kjonekong/OpenClaw-PEnhance/scripts/penhance-hook.sh"]
      }
    ]
  }
}
```

---

## 资源需求

| 资源 | A节点状态 | PEnhance需求 |
|------|-----------|--------------|
| 内存 | 527MB可用 | +50MB |
| 磁盘 | 17GB可用 | +100MB |
| CPU | 0.08负载 | 可忽略 |

---

## 故障排除

### 连接问题

```bash
# 检查 Gateway 状态
curl http://139.224.42.111:18789/health

# 检查 SSH 连接
ssh aliyun "systemctl status openclaw"
```

### 认证问题

```bash
# 验证 Token
echo $OPENCLAW_AUTH_TOKEN

# 测试认证
curl -H "Authorization: Bearer $OPENCLAW_AUTH_TOKEN" \
  http://139.224.42.111:18789/api/status
```

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-03-16 | 1.0.0 | 初始版本，三大核心模块 |

---

## 相关文档

- [完整计划文档](./PLAN.md)
- [Skill 定义](./skills/penhance/SKILL.md)
- [OpenClaw Skills 指南](../.claude/plans/openclaw-skills-guide.md)
