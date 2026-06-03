---
name: executing-plans
description: 当你有书面的实现计划需要在独立会话中以 review checkpoint 方式执行时使用
---

# Executing Plans

## 概述

加载计划，批判性审查，执行所有任务，完成后报告。

**开始时声明：**"我将使用 executing-plans skill 来实现这个计划。"

**注意：** 告诉你的合作伙伴，Superpowers 在能够访问 subagent 时效果更好。如果运行在支持 subagent 的平台（如 Claude Code 或 Codex），其工作质量将显著提升。如果有 subagent 可用，请使用 0004_superpowers:007_subagent-driven-development 代替本 skill。

## 流程

### 步骤 1：加载并审查计划
1. 读取计划文件
2. 批判性审查——识别计划中的任何疑问或顾虑
3. 如有顾虑：在开始前向你的合作伙伴提出
4. 如无顾虑：创建 TodoWrite 并继续

### 步骤 2：执行任务

对每个任务：
1. 标记为 in_progress
2. 严格按照每一步执行（计划中已将步骤拆为小块）
3. 按指定要求运行验证
4. 标记为 completed

### 步骤 3：完成开发

所有任务完成并验证后：
- 声明："我将使用 finishing-a-development-branch skill 来完成这项工作。"
- **必需子 Skill：** 使用 0004_superpowers:012_finishing-a-development-branch
- 按照该 skill 的指引验证测试、展示选项、执行选择

## 何时停止并寻求帮助

**出现以下情况立即停止执行：**
- 遇到阻塞（缺少依赖、测试失败、指令不清晰）
- 计划存在关键缺陷导致无法开始
- 不理解某条指令
- 验证反复失败

**请求澄清，而不是猜测。**

## 何时回到之前的步骤

**回到审查阶段（步骤 1），当：**
- 合作伙伴根据你的反馈更新了计划
- 基本方法需要重新思考

**不要强行突破阻塞——停止并询问。**

## 牢记
- 首先批判性审查计划
- 严格按照计划步骤执行
- 不要跳过验证
- 当计划要求时引用相关 skill
- 遇到阻塞就停止，不要猜测
- 未获得显式用户同意，永远不要在 main/master 分支上开始实现

## 集成

**必需的工作流 skill：**
- **0004_superpowers:003_using-git-worktrees** - 确保隔离工作区（创建一个或验证已有的）
- **0004_superpowers:002_writing-plans** - 创建本 skill 要执行的计划
- **0004_superpowers:012_finishing-a-development-branch** - 所有任务完成后完成开发
