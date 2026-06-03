---
name: using-git-worktrees
description: 任何功能实现开始前使用 — 创建隔离的 git worktree 和独立分支以保护主分支
allowed-tools: Bash EnterWorktree ExitWorktree
---

# Using Git Worktrees

## 概述

为每个功能创建隔离的 git worktree。主工作目录保持干净。每个 worktree 有自己的分支。完成后，合并或丢弃，worktree 被清理。

**核心原则:** 绝不在 main/master 上直接开发。始终隔离。

## 何时使用

**实现前始终使用:**
- 新功能
- 大改动
- 多文件修改
- 涉及多次提交的工作

**仅在以下情况跳过:**
- 单文件笔误修复
- 纯配置修改
- 已经处于 worktree 中

<HARD-GATE>
未创建 worktree 之前，不得开始任何实现工作。在主分支上直接编写代码 = 不可接受。
</HARD-GATE>

## 创建 Worktree

```
EnterWorktree(name="<功能描述>")
```

这会创建:
- 一个基于当前 HEAD 的新分支
- 一个位于 `.claude/worktrees/` 下的隔离工作区
- 会话自动切换到新 worktree

**命名:** 使用 kebab-case 描述功能，如 `add-verification-skill`、`fix-auth-bug`

**创建后验证:**
```bash
git branch --show-current   # 应显示新分支
pwd                         # 应处于 .claude/worktrees/ 下
```

## 在 Worktree 中工作

Worktree 是完整的独立 git 工作区:
- 所有 git 操作只在此功能分支范围内
- 主工作目录不受影响
- 可自由提交、修改、变基，不影响主分支

## 收尾

所有任务完成且测试通过后，调用收尾 skill:

**必须调用的下一个 Skill:** 0004_superpowers:012_finishing-a-development-branch

该 skill 会:
1. 验证测试通过
2. 呈现 4 个选项 (合并/PR/保留/丢弃)
3. 执行选择
4. 清理 worktree:
   - 本地合并或丢弃 → `ExitWorktree(action="remove")`
   - 创建 PR 或保留 → `ExitWorktree(action="keep")`

## 集成

**上游调用:** brainstorming → writing-plans (执行开始前)
**链式连接:** subagent-driven-development 或 executing-plans
**清理者:** finishing-a-development-branch

**工作流位置:**
```
brainstorming → writing-plans → [using-git-worktrees] → 执行 → finishing
```

## 反模式: "改的不多，直接在 master 上改就行"

在主分支上直接开发是最常见的灾难来源。一个不小心的 rebase、一个错误的 reset、一个未完成的实验 — 都会污染主分支。创建 worktree 只需一条命令，代价为零。

## 红灯 — 立即停止

- 未创建 worktree 就开始实现
- 直接在 main/master 上提交
- 忘记清理已完成的 worktree
- 在其他 worktree 内执行 worktree 命令

## 牢记

- 实现前始终隔离
- worktree = 分支 + 工作区，两者均限于此功能
- 清理由 finishing-a-development-branch 处理
