---
name: writing-skills
description: 创建新 skill 或修改已有 skill 时使用 — 融合 Superpowers 约定和项目标准的编写指南
allowed-tools: Read Write Edit Bash Glob
---

# Writing Skills

## 概述

如何编写一个同时适配 Superpowers 工作流和项目 skill 体系的新 skill。

**本指南融合:**
- Superpowers 约定 (HARD-GATE, checklist, chain-to-next, anti-pattern)
- 项目标准 (`rule_skill_format.md` 中的占位符规则, `allowed-tools` frontmatter)

## 两种 Skill 类型

### 类型 A: 工作流链 Skill
- 属于顺序流水线的一部分 (如 brainstorming → writing-plans)
- 末尾有 `必须调用的下一个 Skill: superpowers/<next-skill>`
- 包含 `<HARD-GATE>` 块用于不可协商的约束
- 定义了明确的终点状态（要调用的下一个 skill）

### 类型 B: 独立工具 Skill
- 独立，任何时刻可调用 (如 using-superpowers, writing-skills)
- 无链到下个
- 由用户明确请求或特定条件触发
- 自包含，无外部 skill 依赖

## SKILL.md 模板

```markdown
---
name: <skill名称>
description: <一行说明用途和触发条件>
allowed-tools: <Read Write Edit Bash Glob>
---

# <Skill 中文标题>

## 概述

<此 skill 做什么，核心原则>

<HARD-GATE>
<不可协商的约束 — 特定操作前的硬性停止条件>
</HARD-GATE>

## 何时使用

**始终:**
- <条件 1>
- <条件 2>

**例外 (询问人类伙伴):**
- <例外 1>

## 检查清单

1. **步骤名** — 说明
2. **步骤名** — 说明

## 过程流程 (可选)

<复杂流程的 Graphviz DOT 图>

## 执行过程

### 第 1 步: <名称>
<详细指令>

### 第 2 步: <名称>
<详细指令>

## 反模式: "<常见坏习惯>"

<为什么这有害，应该怎么做>

## 集成

**输入:** <此 skill 期望什么>
**输出:** <此 skill 产出什么>
**链路:** <下一个 skill，或 "终点 — 无链">

## 红灯 — 立即停止

- <标志流程违规的行为>
- <另一个红灯>

## 常见借口

| 借口 | 现实 |
|------|------|
| <常见借口> | <为什么是错的> |

## 牢记

- <关键原则>
- <另一个关键原则>
```

## 占位符规则

**项目标准 (来自 `rule_skill_format.md`):**

Skill 是模板。绝不硬编码项目特定值。使用占位符:

| 占位符 | 含义 |
|--------|------|
| `{任务ID}` | 任务标识符 |
| `{远程URL}` | 远程仓库地址 |
| `{默认分支}` | 主分支名 |

**规则:** 项目范围的值用项目占位符，工作流路径用 superpowers 约定。

## HARD-GATE 语法

```
<HARD-GATE>
不可协商的约束。不能被绕过、合理化或跳过。
在条件满足之前，skill 绝不得通过此门。
</HARD-GATE>
```

## 链到下一个的约定

**对类型 A skill**，"牢记"之前的最后一节必须是:

```markdown
**必须调用的下一个 Skill:** superpowers:<next-skill-name>
```

## 验证清单

声明新 skill 完成前:

- [ ] Frontmatter: `name` + `description` + `allowed-tools`
- [ ] HARD-GATE 存在于不可协商的约束处
- [ ] 检查清单覆盖所有必要步骤
- [ ] 反模式节识别了常见错误
- [ ] 链到下一个正确 (如为类型 A)
- [ ] 无硬编码的项目特定值 (如适用项目约定)
- [ ] 文件位于正确路径: `.claude/skills/0004_superpowers/<0NN_skill-name>/SKILL.md`
- [ ] 标题/术语保留英文，正文中文化

## 路径映射与任务绑定

**Skill 中保留上游逻辑路径格式**（便于同步），实际写入时映射到任务目录:

| Skill 中引用的逻辑路径 | 实际写入路径 |
|-----------------------|-------------|
| `docs/superpowers/specs/YYYY-MM-DD-<topic>.md` | `00_local_task/tasks/{任务ID}/specs/YYYY-MM-DD-<topic>.md` |
| `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` | `00_local_task/tasks/{任务ID}/plans/YYYY-MM-DD-<feature>.md` |

**任务绑定流程**（与 `0002_task-create` 的桥接）:
1. 调用任何 Superpowers Skill 前 → 检查是否有 active 任务
2. 无任务 → 先调 `0002_task-create` 创建
3. 所有产出文件存入 `00_local_task/tasks/{任务ID}/` 对应子目录
4. 每个阶段完成 → 同步更新任务文档 6 处 (TL;DR, 进度表, 当前操作, 已完成操作, 进度日志, 更新时间)

## 语言规则

- **标题/术语 → 保留英文原意** (如 Test-Driven Development, HARD-GATE, subagent)，确保术语精确性和国际通用
- **正文说明 → 翻译为中文**，降低阅读门槛
- **代码块/命令/文件路径 → 保留原文不变**
- **frontmatter `description` → 翻译为中文，`name` → 保留英文**
- **Superpowers 工作流产出的文档** (specs, plans, review) **使用中文**

## 外部 Skill 集成流程

将外部开源 Skill 仓库深度适配到本项目的标准化 10 步决策链。**前置:** 已存在 active 任务（否则先调 `0002_task-create`）。

### 0. 版本锚定

记录上游 commit SHA，写入 README 版本追踪表。用于后续增量同步。

**Superpower 实例:** 上游 `obra/superpowers`，集成 commit `6fd4507659784c351abbd2bc264c7162cfd386dc` (2026-05-29)。

### 1-4. 评估 → 格式分析 → 差异矩阵 → 分批

- 确认协议、规模、依赖 → ✅/⚠️/❌
- 提取 frontmatter 字段、正文结构、特殊元素
- 16 维差异矩阵（路径、命名、约束、语言、平台）
- 第 1 批核心链（最小闭环）→ 第 2 批质量层 → 第 3 批适配层

### 5+6. 命名适配 + 引用同步（同一批次）

父 Skill: `NNNN_功能名`。子 Skill: `0NN_原kebab-case名`，按工作流顺序编号。

**必须同步更新:** 所有子 SKILL.md 链式引用 + CLAUDE.md + README + 任务文档。

验证: `grep -rn "旧路径" .claude/ --include="*.md"`

### 7. 内容本地化

见上方「语言规则」节。

### 8. 桥接建立

与 `0002_task-create` 桥接：前置检查 → 路径映射 (`docs/superpowers/` → `00_local_task/tasks/{任务ID}/`) → 后置同步。

### 9. 上游同步

`git diff <锚定SHA>..upstream/main -- skills/` → 增量识别 → 新增走完整流程 / 修改 diff 合并 / 删除评估影响 → 更新锚定 SHA。

### 常见陷阱

| 陷阱 | 预防 |
|------|------|
| 命名变更后漏更新引用 | 步骤 5+6 同批次，grep 验证 |
| 术语被错误翻译 | 语言规则强制术语保留英文 |
| 忘记版本锚点 | 步骤 0 先于一切 |
| 输出路径未映射 | 桥接规则约束 |

## 牢记

- 每个 skill 都是一份契约 — 严格遵循
- HARD-GATE = 不可协商，即使有时间压力
- 链路必须正确 — 链路断裂 = 工作流断裂
- Skill 质量 > skill 数量
