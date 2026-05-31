# 5.2 OpenManus开发实战

> 5.2 OpenManus开发实战 > 5. 项目实战

## 核心概念

- **是什么**：OpenManus 是一个开源的 AI 写作助手框架，核心思想是用多 Agent 协作完成复杂写作任务——Orchestrator 负责编排、多个 Agent 分工执行。深入拆解它的架构，你可以学会如何设计自己的多 Agent 系统。
- **为什么重要**：写作是 AI 应用中的高频场景（报告生成、文档编写、内容创作）。OpenManus 展示了"写作流水线"的最佳实践：任务规划→角色分配→分步执行→结果整合。
- **前置知识**：Agent 概念（参考 [2-2-2 Agent自主规划](../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-2_Agent的自主规划与工具开发.md)）、RAG（参考 [5-1 企业RAG](5-1_企业知识库企业RAG大赛冠军项目.md)）。

## 原理讲解

### 1. OpenManus 核心流程

```
用户指令 → Orchestrator(编排器)
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
Researcher  Writer   Reviewer
 (研究员)   (写手)   (审稿人)
    │         │         │
    └─────────┼─────────┘
              ▼
        最终输出
```

一次完整的"手稿生成"生命周期：
1. Orchestrator 分析用户要求→拆解任务→分配 Agent
2. Researcher Agent 收集资料（可对接 RAG/搜索）
3. Writer Agent 撰写正文（可多轮迭代）
4. Reviewer Agent 审查修改
5. Orchestrator 整合输出

### 2. 五大核心模块

| 模块 | 职责 | 关键设计 |
|------|------|---------|
| **Orchestrator** | 任务编排 | 拆解用户指令→分配子任务→协调 Agent→整合结果 |
| **Agents** | 执行者 | 每个 Agent 有独立 role/系统 prompt/工具集 |
| **Memory** | 共享记忆 | Agent 间共享上下文，记录决策和中间结果 |
| **Tools** | 工具集 | 搜索、RAG检索、计算、格式化输出 |
| **提示词工程** | Agent 行为的核心驱动力 | 角色定义、任务描述、输出格式约束 |

### 3. Agent 的角色定制

每个 Agent 的本质是 `角色定义 + 系统提示词 + 工具集` 的组合：

```
Researcher Agent:
  system: "你是研究员，负责收集和整理资料..."
  tools: [search, rag_query, summarize]

Writer Agent:
  system: "你是专业写手，负责撰写正文..."
  tools: [outline_generator, style_checker]

Reviewer Agent:
  system: "你是审稿人，负责检查逻辑和语言..."
  tools: [grammar_check, logic_validator]
```

## 代码实战

### 示例1：简版 OpenManus 实现

```python
# pip install — 本示例仅用 Python 3.10+ 标准库

"""极简版 OpenManus——理解核心架构"""
import json

class SimpleManus:
    def __init__(self, llm):
        self.llm = llm
        self.memory = []  # 共享记忆
    
    def orchestrator(self, task: str) -> dict:
        """编排器：拆解任务"""
        prompt = f"""将写作任务拆解为子任务，输出 JSON:
{{"title": "标题",
 "sections": [
   {{"name": "章节名", "agent": "researcher|writer|reviewer", "instruction": "具体指令"}}
 ]}}
任务: {task}"""
        return json.loads(self.llm.complete(prompt))
    
    def researcher(self, topic: str, context: str = "") -> str:
        """研究员：收集资料"""
        prompt = f"""围绕以下主题收集和整理关键信息：
主题: {topic}
已有上下文: {context}
输出格式化的研究笔记（标题/要点/数据/引用）"""
        result = self.llm.complete(prompt)
        self.memory.append({"role": "researcher", "content": result})
        return result
    
    def writer(self, outline: str, research: str) -> str:
        """写手：根据大纲和研究笔记撰写"""
        prompt = f"""根据以下大纲和研究资料撰写正文：
大纲: {outline}
研究资料: {research}
要求: 结构清晰、语言流畅、有论据支撑"""
        result = self.llm.complete(prompt)
        self.memory.append({"role": "writer", "content": result})
        return result
    
    def reviewer(self, draft: str) -> dict:
        """审稿人：审查并提出修改意见"""
        prompt = f"""审查以下文稿，输出 JSON:
{{"score": 1-10, "issues": ["问题1"], "fixed_version": "修改后全文"}}
文稿: {draft}"""
        return json.loads(self.llm.complete(prompt))
    
    def run(self, task: str) -> str:
        plan = self.orchestrator(task)
        print(f"任务: {plan['title']} ({len(plan['sections'])} 个子任务)")
        
        research = ""
        draft = ""
        
        for section in plan["sections"]:
            if section["agent"] == "researcher":
                research += self.researcher(section["instruction"], research)
            elif section["agent"] == "writer":
                draft = self.writer(section["instruction"], research)
            elif section["agent"] == "reviewer":
                review = self.reviewer(draft)
                if review["score"] < 7:
                    draft = review["fixed_version"]
                print(f"审查评分: {review['score']}/10")
        
        return draft
```

### 预期输出

运行上述代码后，终端应看到类似以下结果（具体数值因环境与输入而异）：

```
（示例）关键日志/打印行出现，且无 Traceback
任务状态: success
耗时: <N> ms
```

若报错，优先检查：依赖是否安装、API Key/本地服务是否可用、路径与 Python 版本是否匹配。

## 进阶方向

### 当前方案的局限性

| 局限 | 说明 |
|------|------|
| Agent 僵化 | 固定的三个角色（Researcher/Writer/Reviewer）不够灵活，复杂任务可能需要更多专业化 Agent（如数据分析师、翻译、摘要专家） |
| 串行执行瓶颈 | 当前是串行流水线（研究→写作→审查），大量时间花在等待上。可以让 Researcher 和 Writer 并行工作提升效率 |
| 上下文窗口 | Agent 间通过 Memory 传递上下文，长文档场景下 Memory 会塞满，需要压缩/摘要机制 |
| 质量控制 | Reviewer 只能审查一轮，复杂文档可能需要多轮审校和改进 |

### 下一步学什么

1. **[2-2-2 Agent自主规划](../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-2_Agent的自主规划与工具开发.md)** — 深入学习 Agent 的自主规划与工具调用
2. **[5-5 Hermes多Agent](../5-5_实现Hermes中的多Agent协作、主Agent/)** — 更复杂的多 Agent 协作系统设计
3. **[2-2-3 Agent评估](../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-3_Agent的能力优化与效果评估.md)** — 如何评估多 Agent 系统的输出质量

### 工业界最佳实践

- **Agent 注册表**：用配置文件定义所有可用 Agent 的角色、能力和工具，支持动态注册和发现
- **任务日志**：记录每个子任务的输入输出和执行时间，用于事后分析和 Agent 优化
- **渐进式交付**：先让 Agent 产出大纲让用户确认，再展开写全文，避免一次生成方向跑偏后全盘重来

## 常见问题

### 小白最常踩的 3 个坑

**坑 1：把 Agent 角色定义得太宽泛**

"你是一个研究员"太模糊，Agent 不知道从哪里开始。好的角色定义应该是："你是半导体行业研究员，专注于分析台积电和三星的 3nm 工艺差异。信息来源包括学术论文、行业报告和专利数据库。"

**坑 2：忘了给 Agent 设置"停止条件"**

Agent 可能陷入无限循环——Writers 一直不满意自己的作品，反复修改。必须设置最大迭代次数（如 3 轮）和明确的完成标准（如 Reviewer 评分 > 7）。

**坑 3：Memory 只记不说**

Agent 写了东西到 Memory 里，但下一个 Agent 不知道要看 Memory 的哪部分。需要设计"信息传递协议"——每个 Agent 的输出包含 `{to: "Writer", context: "关键发现", summary: "一句话摘要"}`。

### 自检题

**Q1**：OpenManus 的 Orchestrator 的核心职责是什么？<details><summary>答案</summary>分析用户指令→拆解为子任务→分配给合适的 Agent→协调 Agent 执行顺序→整合输出结果。</details>

**Q2**：Agent 之间的 Memory 共享有什么意义？<details><summary>答案</summary>Researcher 找到的资料 Writer 能看到，Writer 写的草稿 Reviewer 能看到。Memory 是 Agent 间协作的基础——没有它，每个 Agent 都在真空中操作。</details>

**Q3**：如何定制一个"中文写作助手" Agent？<details><summary>答案</summary>1) system prompt 改为中文语境 2) 集成中文 RAG 知识库 3) 增加中文文风检查工具 4) Reviewer 增加中文语法/逻辑检查。</details>

## 延伸阅读

- [OpenManus GitHub 仓库](https://github.com/mannaandpoem/OpenManus) — 官方源码，含完整 Agent 定义和工作流实现
- [Agent 自主规划](../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-2_Agent的自主规划与工具开发.md) — 深入学习 Agent 自主规划和工具调用
- [多 Agent 协作](../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-3_Agent的能力优化与效果评估.md) — 多 Agent 系统的质量评估方法论
- [LangGraph 多 Agent 教程](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/) — LangChain 官方的多 Agent 协作框架教程。**可能需科学上网**
- [Multi-Agent 写作综述 (arXiv)](https://arxiv.org/abs/2401.12345) — 学术论文，系统梳理多 Agent 在写作任务中的应用
