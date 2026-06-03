# Superpowers Skills 集成指南

> 来源：[obra/superpowers](https://github.com/obra/superpowers) (Jesse Vincent)
> 协议：MIT | 93K+ stars | v5.1.0
> 集成日期：2026-06-03
> **上游 commit：** `6fd4507659784c351abbd2bc264c7162cfd386dc` (2026-05-29)
> **集成模式：** 逐文件拉取 (raw.githubusercontent.com)
> **同步状态：** 已是最新（集成后上游无新提交）

## 已集成的 Skills (14/14)

| 编号 | Skill | 阶段 | 用途 |
|------|-------|------|------|
| 001 | `001_brainstorming` | 设计 | Socratic 设计，写代码前先想清楚 |
| 002 | `002_writing-plans` | 计划 | 将设计拆解为 2-5 分钟小任务 |
| 003 | `003_using-git-worktrees` | 隔离 | 创建隔离 worktree，保护主分支 |
| 004 | `004_test-driven-development` | 实现 | RED-GREEN-REFACTOR 循环 |
| 005 | `005_verification-before-completion` | 验证 | 完成前强制验证，证据先于断言 |
| 006 | `006_executing-plans` | 执行 | 按计划逐步执行 |
| 007 | `007_subagent-driven-development` | 执行 | 每 task 独立 subagent + 两阶段 review |
| 008 | `008_dispatching-parallel-agents` | 执行 | 无依赖 task 并行派发 |
| 009 | `009_systematic-debugging` | 调试 | 四阶段系统化调试 |
| 010 | `010_requesting-code-review` | 审查 | 任务完成后代码审查 |
| 011 | `011_receiving-code-review` | 审查 | 接收审查反馈 |
| 012 | `012_finishing-a-development-branch` | 收尾 | 合并/PR/清理 |
| 013 | `013_using-superpowers` | 诊断 | 运行时环境自检 |
| 014 | `014_writing-skills` | 元技能 | Skill 编写规范（融合上游+项目标准） |

## 工作流

```
001_brainstorming → 002_writing-plans → 003_worktrees → 004_TDD
  → 007_subagent | 008_parallel | 006_executing
  → 009_debugging → 010+011_review → 005_verification → 012_finishing
```


## 桥接规则

Superpowers 与项目 `0002_task-create` 任务系统的桥接，详见 `CLAUDE.md` §1.1「Superpowers 与 Task Skill 桥接规则」。

### 路径映射
| Skill 逻辑路径 | 实际写入路径 |
|--------------|-------------|
| `docs/superpowers/specs/` | `00_local_task/tasks/{任务ID}/specs/` |
| `docs/superpowers/plans/` | `00_local_task/tasks/{任务ID}/plans/` |

### 任务绑定流程
1. Superpowers 调用前 → 确认 active 任务存在
2. 无任务 → 先调 `0002_task-create`
3. 每个阶段完成 → 同步更新任务文档 6 处

## 在 CLAUDE.md 中的注册

已在 `CLAUDE.md` 的 `### 1.1 Superpowers 开发工作流 Skills` 节注册。Claude Code 启动时自动读取。

## 与项目 Skills 的关系

| 类型 | 示例 | 用途 |
|------|------|------|
| 项目 Skills | 0001_git-commit, 0002_task-create | 项目特定操作规范 |
| Superpowers Skills | brainstorming, writing-plans | 通用开发工作流方法论 |

两者互不干扰，按场景独立调用。

## 后续可集成的 Skills

| 优先级 | Skill | 价值 | 说明 |
|--------|-------|------|------|
| 高 | test-driven-development | 强制 RED-GREEN-REFACTOR | 与 writing-plans 配合 |
| 高 | verification-before-completion | 完成前自检 | 防遗漏 |
| 中 | systematic-debugging | 系统化调试流程 | 通用性高 |
| 中 | requesting-code-review | 按计划审查代码 | 与 executing-plans 配合 |
| 低 | using-git-worktrees | 隔离工作区 | 需要 worktree 基础设施 |
| 低 | dispatching-parallel-agents | 并行子代理 | 需要 subagent 支持 |

## 已知差异（与上游对比）

| 维度 | 上游 | 本集成 |
|------|------|--------|
| visual-companion 服务器脚本 | 有 `scripts/start-server.sh` | 未集成（需额外脚本） |
| subagent-driven-development | 有（推荐用 subagent 执行） | 未集成（本环境支持 Agent 工具，后续评估） |
| finishing-a-development-branch | 有（收尾流程） | 未集成（项目用 0001_git-commit 替代） |
| using-superpowers | 有（引导加载） | 未集成（通过 CLAUDE.md 直接引用替代） |

## 更新方式

从上游 `obra/superpowers` 仓库拉取新版本 Skills，做最小适配后覆盖。更新时注意：
1. 对比上游 CHANGELOG/RELEASE-NOTES
2. 检查是否有新依赖（脚本、配置）
3. 本目录的 `visual-companion.md` 是精简版，上游更新时需手动合并
