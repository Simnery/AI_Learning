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

**Skill 命名规则**：`NNNN_功能名`，4 位数字前缀控制排序，如 `0000_hello`、`0001_git-commit`、`0002_task-create`。新建 skill 时按功能分组递增编号。

**Skill 编写规范**：所有 Skill 必须用占位符（`{任务ID}` `{远程URL}`），禁止硬编码具体值。详见 `.claude/memory/rules/rule_skill_format.md`。

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
