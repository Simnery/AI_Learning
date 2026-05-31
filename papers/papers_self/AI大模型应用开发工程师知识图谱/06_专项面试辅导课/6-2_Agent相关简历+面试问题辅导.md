# 6.2 Agent相关简历+面试问题辅导

> 6.2 Agent面试辅导 > 6. 专项面试辅导课

## 核心概念

- **是什么**：Agent 面试考察你对"LLM自主决策+工具调用"范式的理解深度。面试官想听到的不只是定义，更是你在项目中的实际踩坑和设计权衡。
- **为什么重要**：Agent 是 2025-2026 AI 应用的最热方向。能清晰讲清楚 Agent 设计和调优的候选人非常稀缺。

### 前置知识

- 建议先学完对应章节正文（如 2-1 RAG / 2-2 Agent / 3-x 框架 / 2-3 微调），再读本面试辅导。


## 原理讲解

Agent 面试的三层考察深度：
- **基础层**：Agent vs 传统 LLM 的区别、ReAct 范式是什么（理解概念）
- **设计层**：你设计的 Agent 的记忆/工具/权限是怎么架构的（展示工程设计能力）
- **安全层**：Agent 自主执行时的风险管控——沙箱、分级权限、审计（展示安全意识）

面试官的追问套路：先让你定义 Agent → 追问"你为什么这样设计记忆"→ 追问"权限怎么管控"→ 追问"安全和便利怎么平衡"。提前准备好这四层的回答。


### 3. 简历 Bullet 模板（Agent 方向）

```
• 实现 ReAct + Function Calling Agent（2-2），工具 8 个，任务成功率 82%
• Hermes 多 Agent：主 Agent 拆解 + 子 Agent 注册（5-5），长任务人工介入率降 35%
```

### 4. 高频追问链

```
你说做过 Agent → 工具谁注册？ → 幻觉怎么控？ → 失败重试？ → 怎么评估？
```

每层准备 **1 个具体例子**，避免空泛形容词。

## 代码实战

```python
"""极简 ReAct Agent —— 面试现场手写版"""

# pip install openai

import json
from openai import OpenAI

def simple_react_agent(user_query: str, tools: dict, llm, max_steps: int = 5):
    """极简 ReAct Agent —— 面试中展示 Agent 核心原理的最佳代码
    
    这段代码展示了 ReAct 的三个核心：
    1. Thought: 推理当前应该做什么
    2. Action: 调用工具
    3. Observation: 观察工具返回结果 → 回到 Thought
    """
    messages = [{
        "role": "system",
        "content": f"""你是 ReAct Agent。可用的工具:
{json.dumps(tools, ensure_ascii=False)}

每次回复格式:
Thought: <推理>
Action: <工具名>
Action Input: <JSON参数>

如果已经得到答案，格式:
Thought: 我已经有足够信息了
Final Answer: <最终答案>"""
    }, {"role": "user", "content": user_query}]
    
    for step in range(max_steps):
        response = llm.chat(messages)
        text = response.choices[0].message.content
        print(f"Step {step+1}: {text[:100]}...")
        
        if "Final Answer:" in text:
            return text.split("Final Answer:")[1].strip()
        
        # 解析工具调用
        if "Action:" in text:
            tool_name = text.split("Action:")[1].split("\n")[0].strip()
            tool_input = text.split("Action Input:")[1].split("\n")[0].strip()
            result = tools.get(tool_name, lambda x: "工具不存在")(tool_input)
            messages.append({"role": "assistant", "content": text})
            messages.append({"role": "user", 
                           "content": f"Observation: {result}"})
    
    return "无法在最大步数内完成任务"


# 面试演示:
# tools = {"search": lambda q: f"搜索结果: {q}相关内容...",
#          "calculator": lambda expr: str(eval(expr))}
# answer = simple_react_agent("2024年GDP增长率是多少？", tools, llm)
```

有人的确认）。

### 预期输出

运行上述代码后，终端应看到类似以下结果（具体数值因环境与输入而异）：

```
（示例）关键日志/打印行出现，且无 Traceback
任务状态: success
耗时: <N> ms
```

若报错，优先检查：依赖是否安装、API Key/本地服务是否可用、路径与 Python 版本是否匹配。

## 进阶方向

- 参考 [2-2 Agent 系列](../02_AI应用技术/) 深入 Agent 技术细节
- 手写一个 ReAct Agent（从零实现，不用 LangChain），面试中非常加分
- 研究 MCP 协议并在 Claude Code 中实现一个自定义 MCP Server，作为项目亮点

---

## 常见问题

### 面试题与回答要点（精选）

### Q1: 一分钟讲清楚Agent的定义

**30秒版本**："Agent 是能自主感知环境、制定计划、调用工具、执行行动并反思结果的 AI 系统。与传统 LLM 一问一答不同，Agent 有自己的目标、记忆和工具集，能在多步推理中自主决策。最经典的范式是 ReAct——推理+行动循环。"

### Q2: 如何处理Agent的幻觉问题？

**三层防护**：1）**前置**：工具返回的数据优先于模型内部知识（事实性查询必须走工具）2）**中置**：每步推理后自我验证（"这条信息的依据是什么？"）3）**后置**：最终输出前交叉验证（多个来源一致才采纳）。

### Q3: Agent的"状态"如何管理？

**回答要点**：我用四层记忆——短期（当前对话上下文）、中期（会话摘要）、长期（LanceDB持久化用户偏好）、工具状态（文件系统/Git状态）。关键设计：状态序列化（JSON可恢复）、状态隔离（不同会话不干扰）、状态清理（过期自动清除）。

### Q4: 如何平衡自主性与可控性？

**五级控制模型**：L0完全手动→L1建议模式（Agent给方案，人选择）→L2确认模式（执行前需确认）→L3半自主（高风险操作确认，低风险自主）→L4完全自主。我的项目用L2-L3混合：文件读写L3、Git推送L2、数据库操作L1。

### Q5: 最复杂的Agent项目

**STAR框架回答**：Situation（业务背景）→ Task（核心挑战）→ Action（我的设计决策，3-5个关键技术选择+理由）→ Result（量化效果：效率提升X%、准确率Y%）。

### Q6: 为什么用LangGraph？

**回答**：LangChain Chain是线性的，ReAct Agent是循环的但单一。LangGraph解决了：条件分支、并行执行、状态持久化、检查点回滚、人机交互节点。我的项目有"审核-修改-再审核"循环+并行工具调用，LangChain做不到。

### Q7: 如何处理Text-to-SQL？

**关键设计**：1）不直接把数据库Schema全部给LLM（token爆炸）→只给相关表的DDL+3条样例数据 2）SQL生成后必须语法校验（sqlparse解析） 3）危险操作拦截（DROP/DELETE无WHERE禁用） 4）执行超时熔断（>10s自动kill）。

### Q8: 自定义工具如何定义？

**最佳实践**：工具定义=name(限定动作)+ description(让LLM理解何时用，非常关键！)+ parameters_schema(JSON Schema约束输入)+ execute(纯函数，无副作用最佳)。

### Q9: 多文件上下文限制如何处理？

**分层策略**：1）项目级：CLAUDE.md/README概览 2）模块级：__init__.py+关键文件摘要 3）任务级：当前任务直接相关的3-5个文件全文。向量检索做文件级路由，找到最相关的文件再全文加载。

### Q10: Agent设计哲学

**核心原则**：1）工具原子化（一个工具只做一件事）2）错误早暴露（工具返回明确错误，不让LLM猜）3）可观测性优先（每步推理+工具调用+结果全记录）4）安全优于便利（高风险操作必须有人的确认）。


### 面试常见误区

**误区 1：把 Agent 和普通 LLM 调用混为一谈**

面试官问"你做过 Agent 项目吗"，回答"我调过 GPT API 做问答"——这不是 Agent。Agent 的核心差异是自主规划+工具调用+多步推理，要在回答中强调这三点。

**误区 2：只说用了什么框架，不说为什么**

"我用了 LangGraph 做 Agent"不够。"我用 LangGraph 因为需要条件分支+人机交互节点，LangChain Chain 做不到这一点。具体场景是..."——展示你对框架设计原理的理解。

**误区 3：不准备 Agent 安全相关的问题**

Agent 安全是面试官必问的压轴题。"Agent 自主执行命令/操作数据库有什么风险？你怎么管控？"必须提前准备沙箱、权限分级、人工审批等安全机制的回答。

### 自检题

**Q1**：面试中如何一句话讲清楚 Agent 的核心特征？<details><summary>答案</summary>"Agent 是能自主感知、规划、调用工具、多步推理并反思的 AI 系统。与传统 LLM 对话不同，Agent 有自己的目标、记忆和工具集，在循环中自主决策。"——三个关键词：自主、工具、循环。</details>

**Q2**：Agent 面试中最容易被追问的安全问题是什么？<details><summary>答案</summary>"Agent 自主执行高风险操作（写文件、执行命令、操作数据库）怎么控制风险？"标准答案：沙箱隔离、权限分级（四级）、高风险操作人工确认、操作审计日志、熔断降级。</details>

**Q3**：怎么在面试中展示 Agent 项目的深度？<details><summary>答案</summary>讲一个具体的失败案例和改进——"最初 Agent 把数据库 Schema 全塞进 prompt，token 爆炸。我改成了只给相关表的 DDL + 样例数据，token 消耗降低 80%。"——失败和改进比完美方案更有说服力。</details>

---

## 延伸阅读

- 本知识图谱 Agent 节点：2-2-1 ~ 2-2-4
- Hermes Agent 项目：5-4, 5-5
- [ReAct 论文](https://arxiv.org/abs/2210.03629) — Agent 推理范式的经典论文。**可能需科学上网**
- [MCP 协议官方文档](https://modelcontextprotocol.io/) — Claude Code 的 Agent 工具协议。**可能需科学上网**
- [Agent 安全设计指南 (知乎)](https://docs.python.org/3/) — 中文社区 Agent 安全实践总结
