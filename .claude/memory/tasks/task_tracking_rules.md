# Task Tracking Rules

> 任务追踪规则 — Claude Code 与 Cursor **共用**；Cursor 侧见 `.cursor/rules/task-workflow.mdc`。

## 目录说明

`.claude/memory/tasks/` 只存放**规则与模板**，不存放实际任务记录。

## 功能定位

| 层 | 目录 | Git | 内容 |
|----|------|-----|------|
| 规则/模板层 | `.claude/memory/tasks/` | ✅ 同步 | 模板、工作流说明 |
| **数据层（双方）** | `00_local_task/` | ❌ 排除（除 `local_data_guide.md`） | 任务主文档、索引、附件 |

## 使用流程

1. **创建任务**：参考 `_template.md` → `00_local_task/tasks/{任务ID}/{任务ID}.md`
2. **初始化索引**：若 `task_index.md` 缺失，从 `task_index.template.md` 复制到 `00_local_task/`
3. **维护索引**：新建 / 暂停 / 恢复 / 完成时更新 `00_local_task/task_index.md`

## 进度更新规则（强制执行）

1. **文档优先**：任何操作前，先将当前状态写入文档
2. **即时更新**：每完成一个子步骤，立即更新进度表
3. **单一来源**：主文档进度表是唯一状态来源（**禁止**第二份任务副本）
4. **失败也记录**：实验即使失败也必须更新结果
5. **每次会话结束前**：确保文档反映最新状态

## 进度更新 6 处（双方相同）

| # | 位置 | 操作 |
|---|------|------|
| 1 | `> **更新时间**` | 刷新为当前时间 |
| 2 | `## TL;DR` | 一句话概括当前状态 |
| 3 | `## 进度表` | 对应步骤 `✅`，下一行 `⏳` |
| 4 | `## 当前操作` | 下一步 checklist |
| 5 | `## 已完成操作` | 追加刚完成项 |
| 6 | `## 进度日志` | 追加一行 |

## 索引规则

- 固定路径：`00_local_task/task_index.md`
- 模板：`.claude/memory/tasks/task_index.template.md`
- 字段：`id | status | owner | last_update | task_file`

## 任务文件设计约定

```
00_local_task/tasks/{任务ID}/
  ├── {任务ID}.md              ← 主文档（双方唯一入口）
  ├── data/
  ├── outputs/
  └── notes/
```

## 恢复任务

| 工具 | 命令 |
|------|------|
| Claude Code | `继续 {任务ID}` |
| Cursor | `继续 {任务ID}` 或 `@00_local_task/tasks/{任务ID}/{任务ID}.md` |

## 与 Cursor 的差异

仅工具层不同（`/clear`、Skill、`.claude` 权限区），数据路径与 6 处更新**无区别**。详见 `00_local_task/local_data_guide.md` 差异表。

## 任务 done 检查清单

- [ ] 是否有经验值得沉淀到 CLAUDE.md 或 memory/rules？
- [ ] 索引中状态已更新为 done
- [ ] 实验结论已写入对应文档
