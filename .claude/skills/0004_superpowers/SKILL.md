---
name: 0004_superpowers
description: Superpowers 开发工作流方法论。14 个子 Skill 覆盖完整 8 阶段工作流。来源 obra/superpowers (Jesse Vincent, MIT)
allowed-tools: Read Write Edit Bash Glob Agent
---

# Superpowers 开发工作流

来自 [obra/superpowers](https://github.com/obra/superpowers) (Jesse Vincent, MIT)，通用软件开发方法论。

## 子 Skill 列表 (14 个，按工作流顺序)

| 编号 | Skill | 阶段 | 说明 |
|------|-------|------|------|
| 001 | `001_brainstorming` | 设计 | Socratic 设计，写代码前先想清楚 |
| 002 | `002_writing-plans` | 计划 | 将设计拆解为 2-5 分钟小任务 |
| 003 | `003_using-git-worktrees` | 隔离 | 创建隔离 worktree，保护主分支 |
| 004 | `004_test-driven-development` | 实现 | RED-GREEN-REFACTOR 循环 |
| 005 | `005_verification-before-completion` | 验证 | 完成前强制验证，证据先于断言 |
| 006 | `006_executing-plans` | 执行 | 按计划逐步执行 + review checkpoints |
| 007 | `007_subagent-driven-development` | 执行 | 每 task 独立 subagent + 两阶段 review |
| 008 | `008_dispatching-parallel-agents` | 执行 | 无依赖 task 并行派发，最多 4 并发 |
| 009 | `009_systematic-debugging` | 调试 | 四阶段系统化调试，禁止猜测式修复 |
| 010 | `010_requesting-code-review` | 审查 | 任务完成/合并前的代码审查 |
| 011 | `011_receiving-code-review` | 审查 | 接收审查反馈，技术求真 |
| 012 | `012_finishing-a-development-branch` | 收尾 | 合并/PR/清理，与 0001_git-commit 协同 |
| 013 | `013_using-superpowers` | 诊断 | 运行时环境自检 |
| 014 | `014_writing-skills` | 元技能 | Skill 编写规范（融合上游+项目标准） |

## 工作流链

```
001_brainstorming → 002_writing-plans → 003_using-git-worktrees → 004_TDD
  → 007_subagent | 008_parallel | 006_executing-plans
  → 009_debugging → 010+011_review → 005_verification → 012_finishing
```

## 桥接规则

与 `0002_task-create` 的桥接，详见 `CLAUDE.md` §1.1。

**前置**: 调用任何子 Skill 前，确认 active 任务存在，否则先调 `0002_task-create`。
**输出**: 所有产出文件存入 `00_local_task/tasks/{任务ID}/` 对应子目录。
**后置**: 每个阶段完成后同步更新任务文档 6 处。

## 语言规则

- Skill 本体 (SKILL.md) 使用中文
- 工作流产出的文档 (specs, plans, review) 使用中文
