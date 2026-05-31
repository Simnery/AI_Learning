---
name: feedback_skill_usage
description: 优先使用已集成的 Skills 而非手动搜索脚本路径
type: feedback
---

优先使用 `.claude/skills/` 下已集成的 Skill，避免重复手动操作。

## 触发规则

| 场景 | Skill |
|------|-------|
| Git 提交/推送 | `0001_git-commit` |
| 创建长任务记录 | `0002_task-create` |

## 执行流程

1. 判断需求是否命中已集成 Skill
2. 命中则优先读取并遵循该 Skill 文档
3. 仅当 Skill 不覆盖当前需求时，再补充通用操作
