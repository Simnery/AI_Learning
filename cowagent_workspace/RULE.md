# RULE.md — 工作空间操作规范

本工作空间是 CowAgent Agent 的运行时目录。项目根目录在 `../`。

## 项目规则

**完整规则以 `../.claude/CLAUDE.md` 为准。** 本文件仅补充本工作空间特有的操作规范。

关键项目规则速览（详见 CLAUDE.md）：
- Git → `0001_git-commit` 规范（不自主提交）
- 任务 → `0002_task-create` 系统（任务记录在 `00_local_task/tasks/`）
- 工作流 → `0004_superpowers` 方法论（brainstorming → plans → TDD → ...）

## 工作空间目录

```
cowagent_workspace/        ← 当前目录（运行时数据，部分 gitignored）
├── AGENT.md               ← 我的身份定义
├── MEMORY.md              ← 长期记忆（会话自动加载）
├── RULE.md                ← 本文件
├── USER.md                ← 用户基本信息
├── memory/                ← 每日对话记忆（gitignored）
├── knowledge/             ← 结构化知识库
├── skills/                ← 工作空间技能（bridge-relay 等）
├── bridge/                ← 桥接消息数据（gitignored）
├── tmp/                   ← 临时文件（gitignored）
└── websites/              ← 网页产物（gitignored）
```

## 记忆系统

- **MEMORY.md** — 项目上下文 + 核心事实，每次会话自动加载
- **memory/YYYY-MM-DD.md** — 当天对话记录（运行时产物，本地保留）
- **knowledge/** — 结构化知识，持续积累

## 安全

- 不泄露 API Key 和私密数据
- 破坏性操作前确认（rm、git reset --hard 等）
- 有疑问时先查 CLAUDE.md 或问用户

## 工作空间演化

学到新东西、发现更好方式、犯错后改正时，记录到对应位置：
- 项目规则 → CLAUDE.md
- 个人记忆 → MEMORY.md
- 操作技巧 → 本文件
