---
name: using-superpowers
description: 验证所有 Superpowers Skills 是否正确加载 — 运行时环境自检
allowed-tools: Read Bash Glob Grep
---

# Using Superpowers

## 概述

快速运行时检查，验证所有已集成的 Superpowers Skills 是否存在且配置正确。诊断工具，不是启动器。

**这不是引导程序** — CLAUDE.md 已处理 skill 加载。这是验证/排障助手。

## 何时使用

- 首次安装或重新克隆后
- 排查 skill 可用性问题时
- 复杂多 skill 工作流执行前
- 用户问 "检查 superpowers 状态"

## 检查清单

按顺序执行:

### 1. 文件存在检查

验证每个已注册 skill 的 SKILL.md 存在:

```
待检查 Skills:
- brainstorming
- writing-plans
- test-driven-development
- executing-plans
- systematic-debugging
- requesting-code-review
- receiving-code-review
- verification-before-completion
- finishing-a-development-branch
- subagent-driven-development
- dispatching-parallel-agents
- using-git-worktrees
- writing-skills
```

### 2. Frontmatter 验证

对每个找到的 SKILL.md，验证:
- `name` 字段存在
- `description` 字段存在
- 无空的 frontmatter

### 3. 工作流链完整性

验证链式引用有效:
```
brainstorming → writing-plans (在 brainstorming/SKILL.md 末尾引用)
writing-plans → subagent-driven-development 或 executing-plans
test-driven-development → (被 executing-plans 和 systematic-debugging 引用)
executing-plans → finishing-a-development-branch
systematic-debugging → test-driven-development (第 4 阶段引用)
finishing-a-development-branch → (终点 — 无链)
```

### 4. 状态报告

输出表格:

| Skill | 文件 | Frontmatter | 链路 | 状态 |
|-------|------|-------------|------|------|
| brainstorming | .claude/skills/0004_superpowers/001_brainstorming/SKILL.md | OK | → writing-plans | 就绪 |

如发现问题:
- 文件缺失 → 检查 `.claude/skills/0004_superpowers/` 目录
- Frontmatter 无效 → 检查 YAML 格式
- 链路断裂 → 检查引用目标 Skill 是否存在

## 牢记

- 这是诊断工具，不是启动器
- CLAUDE.md 是 skill 注册的权威来源
- 如果 skill 缺失，将其添加到 `.claude/skills/0004_superpowers/`
