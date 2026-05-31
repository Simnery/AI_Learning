# 00_local_task — 双方共用任务数据区

> **Claude Code 与 Cursor 共用本目录**，规则一致；模板与流程说明在 `.claude/memory/tasks/`（git 同步）。  
> 位于项目根目录，不在 `.claude/` 下（Claude 避免保护区权限弹窗）。

## 目录功能

| 类型 | 路径 | Git | 用途 |
|------|------|-----|------|
| 规则/模板 | `.claude/memory/tasks/` | ✅ | `_template.md`、`task_tracking_rules.md`、索引模板 |
| **任务数据（双方）** | `00_local_task/tasks/{任务ID}/` | ❌ | 主文档、附件、脚本 |
| 任务索引 | `00_local_task/task_index.md` | ❌ | 状态总览 |

## 创建任务（双方相同）

1. 在 `tasks/` 下创建文件夹 `{任务ID}/`，内含 `{任务ID}.md`（模板：`.claude/memory/tasks/_template.md`）
2. `{任务ID}` = `{日期}_{类别}_{简要描述}`，**文件夹名与 .md 文件名相同**
3. 若 `task_index.md` 缺失，从 `.claude/memory/tasks/task_index.template.md` 复制
4. 新建任务写入索引：`id | status | owner | last_update | task_file`

## 进度更新（双方相同，强制执行）

每完成一个子步骤，**先更新主文档再继续**（6 处，顺序不变）：

| # | 位置 | 操作 |
|---|------|------|
| 1 | `> **更新时间**` | 刷新为当前时间 |
| 2 | `## TL;DR` | 一句话当前状态 |
| 3 | `## 进度表` | 完成行 `✅`，下一行 `⏳` |
| 4 | `## 当前操作` | 下一步 checklist |
| 5 | `## 已完成操作` | 追加刚完成项 |
| 6 | `## 进度日志` | 追加一行（时间\|步骤\|操作\|结果\|下一步） |

原则：文档优先、即时更新、**进度表为唯一状态来源**、失败也记录、会话结束前文档最新。

## 任务目录结构

```
00_local_task/
├── local_data_guide.md          ← 本文件（git 同步）
├── task_index.md                ← 索引（本地）
└── tasks/
    └── {任务ID}/
        ├── {任务ID}.md          ← 主文档（双方唯一入口）
        ├── data/
        ├── outputs/
        └── notes/
```

## 恢复任务

| 工具 | 推荐命令 | 说明 |
|------|----------|------|
| Claude Code | `继续 {任务ID}` | `/clear` 后同上；见 `0002_task-create` |
| Cursor | `继续 {任务ID}` | 或 `@00_local_task/tasks/{任务ID}/{任务ID}.md` 附带恢复 |

恢复后标准动作（**双方相同**）：
1. 打开 `00_local_task/tasks/{任务ID}/{任务ID}.md`
2. 读 `## TL;DR`、`## 当前操作`、`## 进度日志` 最新 3 行
3. 直接继续，不追问、不翻旧对话

## 与 Claude Code 的差异（仅此表允许不同）

| 项目 | Claude Code | Cursor |
|------|-------------|--------|
| 规则载体 | `CLAUDE.md` §3 + Skill `0002_task-create` | `.cursor/rules/task-workflow.mdc` |
| 上下文清理 | 建议 `/clear` 后 `继续 {任务ID}` | 新对话或 `@` 主任务文件即可 |
| 环境初始化 | 可能写 `.claude/settings.local.json` | **不适用** |
| 任务数据路径 | `00_local_task/` | **相同** |
| 模板/索引/6 处更新 | 见 `.claude/memory/tasks/` | **相同** |

## Git 策略

- ✅ 仅 `local_data_guide.md` 提交 git
- ❌ `tasks/`、`task_index.md` 及附件由根目录 `.gitignore` 排除

## 权威规则文件

- `.claude/memory/tasks/task_tracking_rules.md`
- `.claude/skills/0002_task-create/SKILL.md`（Claude 执行细节）
- `.cursor/rules/task-workflow.mdc`（Cursor 对齐说明，冲突时以上述 rules 为准）
