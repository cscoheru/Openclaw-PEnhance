# PEnhance Proxy

**真正的指令增强代理** - 所有Claude Code对话都会经过增强后再发送到GLM。

## 架构

```
Claude Code → PEnhance Proxy (localhost:8080) → GLM-4.7 API
                    ↓
              增强层:
              • 代码模板注入
              • 最佳实践提示
              • 上下文压缩
              • 类型提示要求
```

## 快速开始

### 1. 启动代理

```bash
cd OpenClaw-PEnhance/proxy
./start.sh
```

### 2. 配置Claude Code

在 `~/.claude/settings.json` 中设置:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:8080/v1"
  }
}
```

### 3. 重启Claude Code

所有对话现在都会经过PEnhance增强！

## 验证

```bash
# 检查代理状态
curl http://localhost:8080/health

# 查看统计
curl http://localhost:8080/stats

# 测试请求
curl http://localhost:8080/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"model": "glm-4.7", "max_tokens": 100, "messages": [{"role": "user", "content": "Hello"}]}'
```

## 增强效果

| 请求类型 | 增强内容 |
|----------|----------|
| **代码生成** | 类型提示、错误处理、文档字符串 |
| **算法问题** | 复杂度分析、边界条件、测试用例 |
| **调试请求** | 调试清单、错误检查、根因分析 |
| **长上下文** | 智能压缩、关键信息保留 |

## 配置选项

编辑 `config.py`:

```python
# 启用/禁用功能
ENABLE_CODE_TEMPLATES = True
ENABLE_BEST_PRACTICES = True
ENABLE_CONTEXT_COMPRESSION = True

# OpenClaw增强 (可选)
ENABLE_OPENCLAW = False
OPENCLAW_URL = "http://139.224.42.111:18789"
```

## 降级策略

- OpenClaw不可用时 → 自动使用本地增强
- 代理崩溃时 → Claude Code直接连接GLM API（需移除ANTHROPIC_BASE_URL配置）

## 日志

```bash
tail -f ../logs/proxy.log
```

## 停止代理

```bash
./stop.sh
# 或
pkill -f penhance_proxy.py
```
