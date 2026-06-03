# MEMORY.md — 项目上下文参考

*静态参考文件。每次会话加载后不再修改。*

---

## 核心事实

1. **你是远程助手**，服务 AI Learning 项目。项目由 Claude Code 主导开发。
2. **项目根目录**: `../`（从 workspace 上一级）
3. **你的 workspace**: `.`（`cowagent_workspace/`）
4. **你的 workspace 不是项目！** 项目根目录在上一级。

## 项目上下文

**每次新会话，必须先读 CLAUDE.md：**
```
read(../.claude/CLAUDE.md)
```

CLAUDE.md 包含完整项目规则，是本文件的权威来源。

## 项目路径速查

| 内容 | 相对路径 (从 workspace) |
|------|---------|
| 项目配置 | `../.claude/CLAUDE.md` |
| 项目 Skills | `../.claude/skills/` |
| 外部工具 | `../tools/` (CowAgent, Superpowers submodules) |
| 任务数据 | `00_local_task/tasks/` |
| 任务索引 | `00_local_task/task_index.md` |

## 行为规则

1. **每次新会话先读 CLAUDE.md**
2. **中文回复**，简洁高效
3. **主动使用工具** — bash/read/write/edit/ls，不等用户说"执行"
4. **路径** — 项目根 = `../`，所有项目路径以此为前缀
5. **Git** — 不自主 commit/push，遵循 `0001_git-commit`
6. **工作流** — 复杂任务用 `0004_superpowers` 方法论

## 数据存储策略

<HARD-GATE>
本文件是静态参考，不得在此追加长期记忆。
所有项目操作遵循 `0002_task-create` 规范，任务数据写入 `00_local_task/tasks/{任务ID}/`。
</HARD-GATE>

| 存储需求 | 写入位置 | 说明 |
|---------|---------|------|
| 项目规则 | `../.claude/CLAUDE.md` | 权威来源，不在此重复 |
| 任务数据 | `00_local_task/tasks/{任务ID}/` | 由 0002_task-create 管理 |
| 任务状态 | `00_local_task/task_index.md` | active/paused/done |
| 临时记忆 | `memory/YYYY-MM-DD.md` | CowAgent 自动管理，不手动修改 |
| 本文件 | 不追加 | 仅当项目结构变更时手动更新 |

<HARD-GATE>
操作任何项目文件前，必须先确认对应 00_local_task 任务是否存在。
无任务 → 先创建任务 → 再操作。不得绕过任务系统。
</HARD-GATE>

## 当前状态

- CowAgent 已集成 (git submodule, `tools/cowagent`)
- 企微 bot 通道已配置
- 当前任务查阅 `00_local_task/task_index.md`
