# AI Learning Project

AI 模型、算法、技术应用的系统学习工程。

## 学习路线

### 当前路线：AI大模型应用开发工程师知识图谱

同一份知识图谱的两个版本：

| 版本 | 路径 | 说明 |
|------|------|------|
| 官方原版 | [papers_original/](../papers/papers_original/AI大模型应用开发工程师知识图谱.md) | 知乎来源，暂未开课 |
| 个人扩展 | [papers_self/](../papers/papers_self/AI大模型应用开发工程师知识图谱.md) | 66 文件、6 章扩展内容 |

### 备用学习路线

早期自设计的 BIOS 类比学习路线，详见 [AI_Learning_Roadmap.md](../backup/AI_Learning_Roadmap.md)。

**四阶段路径**：基础理论 → LLM 原理 → 应用开发 → 项目实战

**项目目标**：
- 学习 Transformer、GPT、BERT、Diffusion 等主流模型架构
- 实践模型训练、微调、部署全流程
- 探索 RAG、Agent、Function Calling 等应用范式

## 技术栈

| 领域 | 工具/框架 |
|------|-----------|
| 深度学习 | PyTorch, Transformers, Diffusers |
| 数据处理 | NumPy, Pandas, Datasets |
| 实验管理 | Jupyter Notebook |
| LLM 应用 | LangChain, LlamaIndex, Ollama |
| 向量检索 | FAISS, Chroma |
| 包管理 | uv, pip |

## 目录约定

```
./
├── .claude/          # Claude Code 配置、Skills、规则
├── .cursor/          # Cursor 编辑器规则
├── anki_tool/        # Anki 英语学习卡片工具
│   ├── cards/        # 6 章卡片数据源 (JSON)
│   ├── scripts/      # 制卡/编辑/同步脚本
│   ├── templates/    # 笔记类型模板
│   └── export/       # 牌组备份 (gitignore)
├── papers/           # 学习资料
│   ├── papers_original/  # 官方知识图谱
│   ├── papers_self/      # 个人扩展内容（66文件，6章）
│   └── backup_roadmap/   # 备用学习路线（4阶段，6章）
├── backup/           # 原始脚手架备份
│   └── AI_Learning_Roadmap.md  # 自设计 BIOS 类比学习路线
├── 00_local_task/    # 任务数据 (gitignore, 与 Cursor 共用)
├── data/             # 本地实验数据 (gitignore)
├── sample/           # 参考文件 (gitignore)
└── scripts/          # 临时/辅助脚本
```

## 协作规则

### 1. 优先使用已集成的 Skills

| 场景 | Skill |
|------|-------|
| Git 提交/推送 | 0001_git-commit |
| 创建长任务记录 | 0002_task-create |
| 创建 Anki 英语卡片 | 0003_anki-english |
| 新任务开发工作流 | 0004_superpowers |
| CowAgent 远程接入管理 | 0005_cowagent |

**新任务默认工作流 — Superpowers**：

> 后续所有新任务（项目实战、动手实验等需要多步骤执行的开发任务）**统一采用 Superpowers 工作流**：
> ```
> 0002_task-create → 0004_superpowers/001_brainstorming → 002_writing-plans
>   → 003_using-git-worktrees → 004_TDD → {执行Skill}
>   → 009_debugging → 010+011_review → 005_verification → 012_finishing
> ```
> 简单操作（单文件修复、配置修改）不受此限制。

**Skill 命名规则**：`NNNN_功能名`，4 位数字前缀控制排序，如 `0000_hello`、`0001_git-commit`、`0002_task-create`。新建 skill 时按功能分组递增编号。

**Skill 编写规范**：所有 Skill 必须用占位符（`{任务ID}` `{远程URL}`），禁止硬编码具体值。详见 `.claude/memory/rules/rule_skill_format.md`。

### 1.1 Superpowers 开发工作流 Skills (`0004_superpowers`)

来自 [obra/superpowers](https://github.com/obra/superpowers) (Jesse Vincent, MIT)，通用软件开发方法论。以 `0004_superpowers` 为父 Skill，14 个子 Skill 按工作流顺序编号。

| 编号 | Skill | 阶段 | 说明 |
|------|-------|------|------|
| 001 | `0004_superpowers/001_brainstorming` | 设计 | Socratic 设计，写代码前先想清楚 |
| 002 | `0004_superpowers/002_writing-plans` | 计划 | 将设计拆解为 2-5 分钟小任务 |
| 003 | `0004_superpowers/003_using-git-worktrees` | 隔离 | 创建隔离 worktree，保护主分支 |
| 004 | `0004_superpowers/004_test-driven-development` | 实现 | 强制 RED-GREEN-REFACTOR 循环 |
| 005 | `0004_superpowers/005_verification-before-completion` | 验证 | 完成前强制验证，证据先于断言 |
| 006 | `0004_superpowers/006_executing-plans` | 执行 | 按计划逐步执行 + review checkpoints |
| 007 | `0004_superpowers/007_subagent-driven-development` | 执行 | 每 task 独立 subagent + 两阶段 review |
| 008 | `0004_superpowers/008_dispatching-parallel-agents` | 执行 | 无依赖 task 并行派发，最多 4 并发 |
| 009 | `0004_superpowers/009_systematic-debugging` | 调试 | 四阶段系统化调试，禁止猜测式修复 |
| 010 | `0004_superpowers/010_requesting-code-review` | 审查 | 任务完成/合并前的代码审查 |
| 011 | `0004_superpowers/011_receiving-code-review` | 审查 | 接收审查反馈，技术求真 |
| 012 | `0004_superpowers/012_finishing-a-development-branch` | 收尾 | 合并/PR/清理，与 0001_git-commit 协同 |
| 013 | `0004_superpowers/013_using-superpowers` | 诊断 | 运行时环境自检 |
| 014 | `0004_superpowers/014_writing-skills` | 元技能 | Skill 编写规范（融合上游+项目标准） |

**工作流链**：`001_brainstorming → 002_writing-plans → 003_worktrees → 004_TDD → 007_subagent | 008_parallel | 006_executing → 009_debugging → 010+011_review → 005_verification → 012_finishing`

**与项目 Skills 的关系**：Superpowers Skills 是通用开发方法论，项目 Skills 是项目特定操作规范。两者互不干扰，按场景独立调用。

**文件位置**：`.claude/skills/0004_superpowers/`，详细说明见该目录下 `README.md`。

**Superpowers 与 Task Skill 桥接规则**：

> **1. 任务绑定（前置）**: 调用任何 Superpowers 工作流 Skill 之前，**必须先确认当前存在 active 状态的任务**。
> - 有活跃任务 → 直接继续
> - 无活跃任务 → 先调用 `0002_task-create` 创建任务，再启动 Superpowers 工作流
>
> **2. 路径映射**: Superpowers Skill 中引用的逻辑路径与任务目录的映射关系：
>
> | Superpowers 逻辑路径 | 实际写入路径 |
> |---------------------|-------------|
> | `docs/superpowers/specs/YYYY-MM-DD-<topic>.md` | `00_local_task/tasks/{任务ID}/specs/YYYY-MM-DD-<topic>.md` |
> | `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` | `00_local_task/tasks/{任务ID}/plans/YYYY-MM-DD-<feature>.md` |
>
> Skill 正文中保留逻辑路径格式（便于与上游同步），实际写入时映射到任务目录。
>
> **3. 任务文档同步（后置）**: Superpowers 工作流每完成一个阶段，**必须同步更新任务文档的 6 处**（见 `0002_task-create` 第 4 节）：
>
> | Superpowers 阶段 | 任务文档更新 |
> |-----------------|------------|
> | brainstorming 完成 | 更新「关键洞察与决策」— 记录设计决策 |
> | writing-plans 完成 | 更新「实验/学习进度表」— 方案各 task 对应进度行 |
> | 执行完成 (TDD/executing-plans) | 更新进度表 + 进度日志 — 每完成一个 task |
> | verification 完成 | 更新 TL;DR — 验证结果 |
> | finishing 完成 | 任务状态 → done，索引迁移 |
>
> **4. 语言**: Skill 本体 (SKILL.md) 和所有生成文档**一律使用中文**。

### 2. 权限配置规则

**核心**：`~/.claude/settings.json` 中 `defaultMode: "bypassPermissions"` 全局跳过所有权限弹窗。

**权限模式**（`defaultMode` 可选值）：

| 值 | 行为 |
|----|------|
| `bypassPermissions` | 跳过所有权限检查（当前使用） |
| `acceptEdits` | 自动接受编辑 |
| `default` | 标准询问 |
| `dontAsk` | 不询问，静默拒绝 |
| `plan` | 计划模式 |

**三层安全架构**（`bypassPermissions` 仅跳过第一层）：

| 层 | 控制文件 | 通配符 | `bypassPermissions` |
|---|---|---|---|
| 1. 工具权限 | `settings.json` allow/deny | 支持 `:*:*` `:**` | 跳过 |
| 2. 安全拦截器 | `settings.json` / `settings.local.json` | **冒号格式** `cmd:*` 有效；引号路径无效 | **不跳过** |
| 3. `.claude/` 保护区 | 无 | 无 | **不跳过** |

**安全拦截器触发场景**：shell 重定向写入 (`echo > file`)、文件删除 (`rm`/`rmdir`)、创建目录/文件 (`mkdir`/`touch`)

**安全拦截器消除方式**：
- `mkdir`/`touch`/`rm`/`rmdir` → `settings.json` 冒号通配符预授权（可 git 同步）：
  ```
  Bash(mkdir:*)  Bash(rm:*)  Bash(rmdir:*)  Bash(touch:*)
  ```
- **带子命令的命令**（conda, curl, git, pip, python, uv 等）→ 需同时保留两种格式：
  ```
  Bash(git:*:*)   ← 层1：子命令 + 参数
  Bash(git:*)     ← 层2：安全拦截器只认单冒号
  ```
- **shell 重定向** (`echo > file`) → **冒号格式无效**，每条新路径需弹窗授权一次，生成精确路径规则 `Bash("path")` 写入 `settings.local.json`。
  > **规则**：禁止使用 `echo > file` / `cat > file` 等 shell 重定向写文件，一律用 Write 工具替代。仅当 Write 工具无法满足需求时才可用重定向。

**各路径权限行为速查**：

| 操作 | 项目根目录 | `.claude/` 目录 | 消除方式 |
|------|-----------|----------------|----------|
| `mkdir` / `touch` | 无弹窗 | **弹窗** | 根目录：`Bash(cmd:*)`；`.claude/`：逐路径授权 |
| Write / Read 工具 | 无弹窗 | 无弹窗 | 全局 `Write(**)` `Read(**)` |
| `rm` / `rmdir` | 无弹窗 | **弹窗** | 根目录：`Bash(cmd:*)`；`.claude/`：逐路径授权 |
| `echo > file` | **弹窗** | **弹窗** | 只能逐路径授权，写入 `local.json` |

> **`.claude/` 下最佳实践**：写文件用 Write 工具，读文件用 Read 工具，可完全避免弹窗。mkdir/rm/rmdir 每条新路径需授权一次。

**`.claude/` 目录存放原则**：

| 放 `.claude/` 下 | 放项目根目录 |
|-------------------|-------------|
| Claude Code 自身配置（settings.json, CLAUDE.md） | 任务数据（00_local_task/） |
| Skills（只读，不频繁变更） | 实验代码、笔记、数据 |
| 规则/模板（git 同步，少量文件） | 所有需要 mkdir/rm 频繁操作的内容 |

> **原则**：只有 Claude Code 自身运行必需的配置才放 `.claude/`，业务数据一律放项目根目录。避免保护区弹窗干扰工作流。

**分组与排序**（`permissions.allow`）：

```
Bash 命令（字母序）
  conda → cp → curl → echo → find → git → jupyter → ls → mkdir → mv
  → nvidia-smi → ollama → pip → pytest → python → rm → rmdir
  → ruff → touch → uv

文件操作（字母序，紧邻）
  Edit(**) → Read(**) → Write(**)     ← `**` 递归匹配所有子目录

其他工具（字母序）
  Agent(*) → Glob(*) → Skill(*) → TaskCreate(*)
  → TaskGet(*) → TaskList(*) → TaskUpdate(*) → WebFetch(*)
```

`permissions.deny` 同样字母序。

**Why:** 之前 `settings.local.json` 堆积大量一次性路径，每次逐条弹窗。

**How to apply:**
- 工具权限弹窗 → 通配符 → `settings.json` allow 列表
- 安全拦截器弹窗 → "Yes, always allow" → 自动写 `settings.local.json`
- `.claude/` 目录弹窗 → 选"don't ask again for <项目根目录>"做项目级信任

### 3. 任务持久化（防中断丢失）
**必须执行**：收到多步骤任务时，先创建任务记录。
- **规则/模板**：`.claude/memory/tasks/`（git 同步）
- **任务数据（Claude + Cursor 共用）**：`00_local_task/tasks/{任务ID}/{任务ID}.md`（本地私有，不在 `.claude/` 下避免权限弹窗）
- **共用说明**：`00_local_task/local_data_guide.md`
- **Cursor 对齐**：`.cursor/rules/task-workflow.mdc`（与本文及 `0002_task-create` 一致；仅工具差异见 `local_data_guide` 差异表）
- **恢复机制**（双方读同一主文档）：

  | 环境 | 命令 |
  |------|------|
  | Claude Code | `继续 {任务ID}` |
  | Cursor | `继续 {任务ID}` 或 `@00_local_task/tasks/{任务ID}/{任务ID}.md` |

- **工作流**：`.claude/memory/tasks/task_tracking_rules.md`

### 4. 记忆分层维护
**设计原则：规则同步，数据本地**

| 层级 | 存放位置 | Git 同步 | 内容 |
|------|----------|----------|------|
| 规则层 | `.claude/memory/rules/` | ✅ 同步 | 项目规则、协作约定 |
| 模板层 | `.claude/memory/tasks/` | ✅ 同步 | 任务模板、工作流规则 |
| 数据层 | `00_local_task/` | ❌ 排除 | Claude/Cursor 共用任务数据、索引 |

### 5. 经验沉淀机制
- 每次学习/实验完成后，主动询问用户是否有经验值得沉淀
- 用户确认后，追加到本文件对应章节
