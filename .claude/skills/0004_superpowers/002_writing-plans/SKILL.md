---
name: writing-plans
description: 用于有多步骤任务的需求或规格说明，在动手写代码之前
---

# Writing Plans

## 概述

编写全面的实施计划，假设工程师对我们的代码库零背景且品味参差不齐。记录他们需要知道的一切：每个任务涉及哪些文件、代码、测试、可能需要查阅的文档、如何测试。把整个计划划分为一口大小的小任务。DRY。YAGNI。TDD。频繁提交。

假设他们是熟练开发者，但对我们的工具集和问题领域几乎一无所知。假设他们也不太懂好的测试设计。

**开始时宣告：** "我使用 writing-plans skill 来创建实施计划。"

**上下文：** 如果在隔离 worktree 中工作，应在执行时通过 `0004_superpowers:003_using-git-worktrees` skill 创建。

**计划保存到：** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- （用户对计划位置的偏好可覆盖此默认值）

## 范围检查

如果需求涉及多个独立子系统，应该已经在头脑风暴阶段拆分为子项目需求。如果没有，建议将其拆为单独的计划——每个子系统一个。每个计划都应能独立产出可工作、可测试的软件。

## 文件结构

在定义任务之前，先梳理哪些文件会被创建或修改，以及每个文件的职责是什么。这是将分解决策定下来的时刻。

- 设计边界清晰、接口明确的单元。每个文件应有一个清晰的职责。
- 对于能一次性放入上下文理解的代码，你的推理最佳；聚焦的文件让你的编辑更可靠。优先采用小而专注的文件，而非做得太多的大文件。
- 经常一起变化的文件应放在一起。按职责而非技术层拆分。
- 在已有代码库中，遵循既定模式。如果代码库使用大文件，不要单方面重构——但如果你要修改的文件已经臃肿到难以维护，在该计划中包含一次拆分是合理的。

这个结构为任务分解提供依据。每个任务应产出独立有意义、自包含的变更。

## 一口大小任务粒度

**每个步骤是一个动作（2-5 分钟）：**
- "编写失败测试" - 步骤
- "运行它确认失败" - 步骤
- "实现最小代码让测试通过" - 步骤
- "运行测试确认通过" - 步骤
- "提交" - 步骤

## 计划文档头部

**每个计划必须以这个头部开头：**

```markdown
# [特性名称] 实施计划

> **面向 agentic worker：** 必需子技能：使用 0004_superpowers:007_subagent-driven-development（推荐）或 0004_superpowers:006_executing-plans 来逐任务实施此计划。步骤使用 checkbox（`- [ ]`）语法进行追踪。

**目标：** [一句话描述要构建什么]

**架构：** [2-3 句关于实现方式的描述]

**技术栈：** [关键技术/库]

---
```

## 任务结构

````markdown
### 任务 N：[组件名称]

**文件：**
- 创建：`exact/path/to/file.py`
- 修改：`exact/path/to/existing.py:123-145`
- 测试：`tests/exact/path/to/test.py`

- [ ] **步骤 1：编写失败测试**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **步骤 2：运行测试确认失败**

运行：`pytest tests/path/test.py::test_name -v`
预期：FAIL，报 "function not defined"

- [ ] **步骤 3：编写最小实现**

```python
def function(input):
    return expected
```

- [ ] **步骤 4：运行测试确认通过**

运行：`pytest tests/path/test.py::test_name -v`
预期：PASS

- [ ] **步骤 5：提交**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 禁止占位符

每个步骤必须包含工程师需要的实际内容。以下是**计划失败**的典型——永远不要写这些：
- "TBD"、"TODO"、"稍后实现"、"待补充"
- "添加适当的错误处理" / "添加验证" / "处理边界情况"
- "为上述内容编写测试"（没有实际测试代码）
- "与任务 N 类似"（重复代码——工程师可能会乱序阅读任务）
- 仅描述要做什么、没有展示怎么做的步骤（代码步骤必须有代码块）
- 引用任何未在任务中定义的类型、函数或方法

## 铭记

- 始终使用精确文件路径
- 每个步骤都包含完整代码——如果步骤涉及代码变更，展示代码
- 精确的命令及预期输出
- DRY、YAGNI、TDD、频繁提交

## 自审

写完完整计划后，用新视角审视需求并逐一核验。这是你自己执行的 checklist——不是派发 subagent。

**1. 需求覆盖率：** 浏览需求的每个章节/要求。能否指出哪个任务实现了它？列出任何缺口。

**2. 占位符扫描：** 搜索计划中的红旗——上述"禁止占位符"部分的任何模式。修复它们。

**3. 类型一致性：** 后续任务中使用的类型、方法签名和属性名是否与前面任务定义的一致？任务 3 中调用的函数叫 `clearLayers()` 但在任务 7 中叫 `clearFullLayers()`，这就算 bug。

如果发现问题，就地修复。无需重新审查——修复后继续即可。如果发现需求中有未被任务覆盖的要求，添加任务。

## 执行交接

保存计划后，提供执行方式选择：

**"计划已完成并保存到 `docs/superpowers/plans/<filename>.md`。两种执行方式：**

**1. Subagent-Driven（推荐）** - 每个任务派发独立 subagent，任务间审查，快速迭代

**2. Inline Execution** - 在当前会话中使用 executing-plans 执行任务，带 checkpoint 的批量执行

**选用哪种方式？"**

**如果选择 Subagent-Driven：**
- **必需子技能：** 使用 0004_superpowers:007_subagent-driven-development
- 每个任务独立 subagent + 两阶段审查

**如果选择 Inline Execution：**
- **必需子技能：** 使用 0004_superpowers:006_executing-plans
- 带 checkpoint 的批量执行以供审查
