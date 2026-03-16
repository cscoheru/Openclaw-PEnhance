---
name: penhance
description: Programming Enhancement Skill for Claude Code with GLM-4 Plus - Memory, Plan Enforcement, and Algorithm Enhancement
metadata:
  {
    "openclaw": {
      "emoji": "🧠",
      "version": "1.0.0",
      "author": "kjonekong",
      "requires": {
        "anyBins": ["curl", "python3"]
      },
      "config": {
        "memory": "/Users/kjonekong/OpenClaw-PEnhance/config/memory-config.json",
        "plan": "/Users/kjonekong/OpenClaw-PEnhance/config/plan-config.json",
        "algorithm": "/Users/kjonekong/OpenClaw-PEnhance/config/algorithm-config.json"
      }
    }
  }
---

# PEnhance - Programming Enhancement Skill

**Version**: 1.0.0
**Gateway**: Node A (Aliyun) - ws://139.224.42.111:18789
**Model**: GLM-4 Plus (128K context window)

---

## 概述

PEnhance 是一个编程增强 Skill，通过 OpenClaw Gateway 和 GLM-4 Plus 提供三大核心增强能力：

1. **记忆增强 (Memory Enhancer)** - 防止上下文溢出
2. **计划匹配 (Plan Match Enforcer)** - 防止任务漂移
3. **算法增强 (Algorithm Enhancer)** - 深度算法理解

---

## 一、记忆增强 (Memory Enhancer)

### 1.1 核心功能

当检测到以下触发条件时，自动保存上下文信息：

| 触发器 | 描述 | 行为 |
|--------|------|------|
| `file_save` | 文件保存时 | 提取并存储关键上下文 |
| `task_complete` | 任务完成时 | 保存完整会话状态 |
| `context_threshold` | 上下文达到阈值时 | 压缩并归档旧上下文 |

### 1.2 使用方式

```
用户: /penhance memory save
→ 手动保存当前上下文

用户: /penhance memory load <session_id>
→ 加载指定会话的上下文

用户: /penhance memory list
→ 列出所有已保存的会话

用户: /penhance memory compress
→ 压缩当前上下文（保留关键信息）
```

### 1.3 上下文提取内容

保存时会提取以下信息：

- 当前任务描述
- 已完成的工作列表
- 待办事项
- 关键技术决策
- 代码变更摘要
- 最近的文件操作
- 活跃的变量和函数

---

## 二、计划匹配 (Plan Match Enforcer)

### 2.1 核心功能

监控代码变更与开发计划的匹配程度，防止任务漂移。

### 2.2 工作流程

```
1. 创建开发计划 (使用 plan-template.md)
   ↓
2. 开始编码
   ↓
3. 每次代码变更时：
   a) 解析变更内容
   b) 匹配计划中的任务
   c) 计算匹配分数
   d) 检测偏离程度
   ↓
4. 如果检测到偏离：
   - 警告: 偏离度 < 30%
   - 阻止: 偏离度 > 50%
   - 请求用户决策
```

### 2.3 使用方式

```
用户: /penhance plan create <plan_name>
→ 创建新的开发计划

用户: /penhance plan track
→ 开始跟踪当前计划

用户: /penhance plan status
→ 查看计划完成状态和匹配度

用户: /penhance plan deviation
→ 查看偏离分析报告

用户: /penhance plan update
→ 更新计划（添加新任务）
```

### 2.4 偏离处理选项

当检测到偏离时，提供以下选项：

1. **更新计划** - 新任务是必要的，更新计划
2. **回滚代码** - 偏离应该被拒绝，回滚变更
3. **标记技术债务** - 稍后处理，记录为技术债务

---

## 三、算法增强 (Algorithm Enhancer)

### 3.1 支持的算法类型

| 类型 | 算法示例 |
|------|----------|
| 排序 | 快速排序、归并排序、堆排序、基数排序 |
| 搜索 | 二分查找、DFS、BFS |
| 图算法 | Dijkstra、Bellman-Ford、Floyd-Warshall、A* |
| 动态规划 | 背包问题、LCS、编辑距离 |
| 贪心 | 活动选择、霍夫曼编码 |
| 回溯 | N皇后、数独求解 |
| 机器学习 | 梯度下降、K-Means、决策树 |

### 3.2 分析输出

对于识别到的算法，输出以下内容：

1. **复杂度分析** - 时间和空间复杂度
2. **边界条件** - 特殊情况处理
3. **测试用例** - 自动生成的测试用例
4. **优化建议** - 可能的优化方向
5. **伪代码** - 算法的伪代码描述

### 3.3 使用方式

```
用户: /penhance algo analyze <code_snippet>
→ 分析指定代码的算法

用户: /penhance algo suggest <problem_description>
→ 根据问题描述推荐算法

用户: /penhance algo generate <algorithm_name>
→ 生成算法的代码实现

用户: /penhance algo compare <algo1> <algo2>
→ 比较两个算法的优劣
```

---

## 四、综合命令

```
用户: /penhance status
→ 显示所有增强模块的状态

用户: /penhance config
→ 显示当前配置

用户: /penhance health
→ 检查 OpenClaw Gateway 连接状态

用户: /penhance reset
→ 重置所有状态
```

---

## 五、配置文件

| 配置 | 路径 |
|------|------|
| OpenClaw 连接 | `config/openclaw-config.json` |
| 记忆增强 | `config/memory-config.json` |
| 计划匹配 | `config/plan-config.json` |
| 算法增强 | `config/algorithm-config.json` |

---

## 六、环境变量

```bash
# 必需
export OPENCLAW_AUTH_TOKEN="your_auth_token"

# 可选
export PENHANCE_LOG_LEVEL="info"
export PENHANCE_CONTEXT_THRESHOLD="100000"
```

---

## 七、与 Claude Code 集成

### 7.1 作为自定义命令

在 `~/.claude/commands/` 目录创建 `penhance.md`:

```markdown
---
description: Programming Enhancement with OpenClaw + GLM-4 Plus
---

Use the PEnhance skill to enhance programming capabilities.
```

### 7.2 通过 Hook 自动触发

在 `~/.claude/settings.json` 配置 hooks：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": ["/path/to/penhance-hook.sh"]
      }
    ]
  }
}
```

---

## 八、故障排除

### 8.1 常见问题

| 问题 | 解决方案 |
|------|----------|
| 连接超时 | 检查 OpenClaw Gateway 是否运行 |
| 认证失败 | 验证 OPENCLAW_AUTH_TOKEN |
| 内存不足 | 调整 contextThreshold 配置 |
| 计划不匹配 | 检查计划格式是否符合模板 |

### 8.2 健康检查

```bash
# 检查 Gateway 连接
curl -H "Authorization: Bearer $OPENCLAW_AUTH_TOKEN" \
  http://139.224.42.111:18789/health
```

---

**状态**: 准备就绪
**最后更新**: 2026-03-16
