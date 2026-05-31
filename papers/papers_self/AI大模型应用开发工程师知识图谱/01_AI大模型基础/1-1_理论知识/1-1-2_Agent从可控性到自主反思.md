# 1.1.2 Agent：从可控性到自主反思

> 1.1 理论知识 > 1. AI大模型基础

---

## 核心概念

### 是什么

**AI Agent（智能体）** 是一个能自主感知环境、制定计划、调用工具、执行行动的 AI 系统。它不只是回答问题，而是像人一样"思考→行动→观察→调整"。

**可控性** 指 Agent 的行为不跑偏——不做不该做的事、不输出违规内容。**自主反思** 指 Agent 能审视自己的输出，发现错误并自行修正。

打个比方：纯 LLM 像搜索引擎（你问我答），Agent 像一个实习生——你给目标，TA 自己规划步骤、上网查资料、写代码、检查结果、修正错误。

### 为什么重要

Agent 是 AI 从"工具"进化为"助手"的关键。但越自主越危险——一个能自己上网、发邮件、写代码的 Agent，如果产生幻觉或偏离目标，后果比一个错误的对话回答严重得多。所以"可控"和"自主"必须同步建设。

### 前置知识

- [1.1.1 提示工程与 RAG](1-1-1_从提示工程到RAG构建大模型的知识与交互.md)
- 后续：[2.2.1 Function Calling 与 MCP](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-1_Function_Calling与MCP.md)

---

## 原理讲解

### Agent 幻觉的三层成因

```
幻觉来源
   │
   ├── 知识边界模糊（不知道自己在不知道）
   │     模型对自己的知识范围没有明确认知，被问到盲区时会编造
   │
   ├── 推理链断裂（多步推理中某一步出错）
   │     像多米诺骨牌，第一步推错，后面全错
   │
   └── 工具误用（调用了错误的函数或参数）
         Agent 把工具名记错、参数填错、结果解读错
```

### 三板斧控制幻觉

| 方法 | 原理 | 类比 |
|------|------|------|
| **RAG / Tool-use 校验** | 不让 Agent 凭记忆作答，强制调用外部事实源 | 考试时可以翻书，不是闭卷 |
| **Function Calling + JSON 约束** | 工具调用用严格的 JSON Schema，输入输出格式固定 | 填表格而不是写作文，不会跑题 |
| **Human-in-the-Loop** | 关键节点（发邮件、删数据、付款）必须人工审批 | 实习生不能自己签合同 |

### 思维链（CoT）的原理

人不加思索会犯错，模型也一样。CoT 让模型在给出最终答案前，先把推理过程一步步写出来：

```
无 CoT："1.1 + 2.3 = ?"   → "3.4"     ← 可能错
有 CoT："1.1 + 2.3 = ?
         1 + 2 = 3
         0.1 + 0.3 = 0.4
         3 + 0.4 = 3.4
         答案：3.4"            ← 准确度大幅提升
```

CoT 的魔力：把隐式计算变成显式推理，每步都可审计，中间出错能定位。

### ReAct：思考+行动循环

ReAct（Reasoning + Acting）是 Agent 的核心框架，把 CoT 和工具调用组合成循环：

```
┌──────────────────────────────┐
│  Thought（思考）：分析当前状态，决定下一步
│       ↓
│  Action（行动）：调用工具/搜索/计算
│       ↓
│  Observation（观察）：读取工具返回的结果
│       ↓
│  判断：任务完成了？
│    否 → 回到 Thought（新一轮）
│    是 → Final Answer（给出最终答案）
└──────────────────────────────┘
```

**例子**——Agent 回答"昨天北京的天气适合跑步吗？"：

```
Thought: 需要查昨天北京天气
Action: search("2026-05-29 北京天气")
Observation: 多云，18-25°C，湿度45%，无降水

Thought: 判断是否适合跑步
- 温度18-25°C：适中
- 湿度45%：舒适
- 无降水：地面干燥
→ 适合跑步

Final Answer: 昨天北京多云，18-25°C，湿度适中无降水，非常适合户外跑步。
```

### 自主反思（Self-Reflection）

让 Agent 在做完每一步后问自己：**"我的推理对吗？有更好的方法吗？"**

实现方式：设计一个**评估提示（Critic Prompt）**，让 Agent 或另一个模型对已完成的步骤打分：

```
评估提示模板：
"请审查以下 Agent 的推理和行动：
{Agent的输出}
检查点：
1. 推理逻辑是否有跳跃？
2. 使用的工具是否正确？
3. 观察结果是否与结论一致？
4. 是否有更优的方案？

给出评分（1-5）和改进建议。"
```

---

## 代码实战

### 1. 最小 ReAct Agent

```bash
pip install openai
```

```python
# react_agent.py — ReAct 框架的最小实现
import openai
import json

client = openai.OpenAI()

# 模拟一个搜索工具
def search_tool(query: str) -> str:
    """模拟搜索引擎"""
    knowledge = {
        "北京天气": "多云 18-25°C 湿度45% 无降水",
        "上海天气": "小雨 15-20°C 湿度80%",
    }
    return knowledge.get(query, "未找到相关信息")

# ReAct 提示词模板
SYSTEM_PROMPT = """你是一个使用 ReAct 框架的智能助手。
回答问题时严格按以下格式：

Thought: {分析当前状态，决定下一步}
Action: {工具名: 输入参数}
Observation: {工具返回的结果}
...（可重复多轮）
Thought: {判断任务是否完成}
Final Answer: {最终答案}

可用工具：
- search(查询词): 搜索信息
"""

def react_agent(question: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    # 第一轮：生成 Thought + Action
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    text = response.choices[0].message.content
    print(f"=== Agent 推理过程 ===\n{text}\n")
    
    # 简单解析：如果调用了 search，执行并继续
    if "search(" in text:
        # 提取搜索词
        start = text.find("search(") + 7
        end = text.find(")", start)
        if start > 6 and end > start:
            query = text[start:end].strip().strip('"').strip("'")
            result = search_tool(query)
            
            # 把工具结果追加到对话
            messages.append({"role": "assistant", "content": text})
            messages.append({"role": "user", 
                "content": f"Observation: {result}\n请继续推理，给出 Final Answer。"})
            
            # 第二轮：基于观察生成最终答案
            final = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            final_text = final.choices[0].message.content
            print(f"=== 最终回答 ===\n{final_text}")
            return final_text
    
    return text

# 测试
react_agent("昨天北京的天气适合跑步吗？")
```

### 2. 自反思评估器

```python
# self_reflection.py — 用另一个 LLM 当"评委"审查 Agent 输出
import openai

client = openai.OpenAI()

CRITIC_PROMPT = """你是一位严格的质量审查员。
请审查以下 Agent 的推理和行动，逐项检查：

{agent_output}

检查清单：
1. 推理链是否完整？每一步是否有逻辑跳跃？
2. 工具调用是否正确？（工具名、参数、解读）
3. 结论是否有证据支撑？
4. 是否存在安全隐患？（不应执行的操作）

评分（1-5，5分为完美）：
"""

def critic_review(agent_output: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", 
            "content": CRITIC_PROMPT.format(agent_output=agent_output)}]
    )
    return response.choices[0].message.content

# 使用示例
agent_result = "Thought: 需要查天气\nAction: search('北京天气')\nFinal Answer: 适合跑步"
review = critic_review(agent_result)
print(f"评审结果：\n{review}")
```

### 3. 关键代码解读

| 代码段 | 设计意图 |
|--------|---------|
| `SYSTEM_PROMPT` 中强制格式 | ReAct 的核心——不让模型自由发挥，用格式约束它先想再做 |
| 解析 `search(` 手动注入 Observation | 生产环境用 Function Calling 的 JSON 格式更规范，这里展示原理 |
| `CRITIC_PROMPT` 独立评估 | 不依赖 Agent 自己说自己对——用另一个调用来审查，减少"自信的错" |

---

### 预期输出

运行上述代码后，终端应看到类似以下结果（具体数值因环境与输入而异）：

```
（示例）关键日志/打印行出现，且无 Traceback
任务状态: success
耗时: <N> ms
```

若报错，优先检查：依赖是否安装、API Key/本地服务是否可用、路径与 Python 版本是否匹配。

## 进阶方向

### 当前局限
- **基础 ReAct 只有一轮工具调用**：复杂任务（如"规划我的旅行"）需要多轮 Thought-Action-Observation
- **自反思不能修正所有错误**：如果模型根本没有相关知识，反思也无法弥补
- **成本高**：每个 Thought-Action 循环都是一次 API 调用，复杂任务可能 10 轮以上

### 下一步学什么
- [Function Calling 与 MCP（2.2.1）](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-1_Function_Calling与MCP.md) — 规范化工具调用
- [Agent 的自主规划与工具开发（2.2.2）](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-2_Agent的自主规划与工具开发.md) — 复杂任务分解

### 工业界最佳实践
- **安全围栏**：Agent 执行敏感操作前，必须过一道规则引擎（如：金额 > 1000 元 → 人工审批）
- **工具白名单**：不给 Agent 暴露所有 API，只给它需要的
- **速率限制**：设定每轮 Thought → Action 超时和最大循环次数，防止无限循环烧钱

---

## 常见问题

**Q1：Agent 和普通聊天机器人有什么区别？**

聊天机器人是"你问一句我答一句"，Agent 是"你给我一个目标，我自己拆解步骤、找资料、执行、检查、修正"。前者是工具，后者是助手。

**Q2：Function Calling 和直接写 prompt 调用工具有什么区别？**

直接写 prompt 是"请调用 search('北京天气')"，模型可能不听话或格式乱。Function Calling 是给模型一个 JSON Schema，模型返回严格的 `{"name":"search","arguments":{"query":"北京天气"}}`，可编程解析，不会格式错。

**Q3：Human-in-the-Loop 什么时候该介入？什么时候不该？**

**该介入**：涉及金钱交易、删除数据、发送对外消息、修改生产配置。**不该介入**：纯信息查询、数据分析、格式转换——这些让 Agent 自由发挥反而效率更高。

---

### 自检题

1. ReAct 框架的三个核心步骤是什么？每一步的作用？
   <details><summary>答案</summary>Thought（决定做什么）→ Action（执行工具调用）→ Observation（读取结果）。循环执行直到任务完成，输出 Final Answer</details>

2. 为什么 CoT（思维链）能提高推理准确度？
   <details><summary>答案</summary>把隐式计算变成显式推演，每步可审计。模型在写推理过程时也在"思考"，比直接跳结论更准确</details>

3. 只用 Function Calling 约束格式够不够？为什么还需要 Human-in-the-Loop？
   <details><summary>答案</summary>不够。Function Calling 只保证格式正确，不保证"该不该做"。HITL 在关键节点加入人的判断，防止 Agent 执行不应执行的操作</details>

---

## 延伸阅读

**推荐资料**（国内可访问）：

- [ReAct 论文解读（知乎）](https://docs.python.org/3/) — 中文解析 ReAct 框架原理和实验效果
- [WayToAGI — Agent 学习路线](https://waytoagi.feishu.cn/wiki/QPe5w5gWsiR1qxk4NAccX5A7nGf) — AI Agent 从入门到精通的系统教程（飞书文档，国内可直接访问）
- [Datawhale — LLM Agent 教程](https://github.com/datawhalechina) — 搜索 "Agent" 仓库，有完整的中文教程和代码

**国外资料**（可能需科学上网）：

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — ReAct 原始论文（Yao et al., 2022）
- [LangChain Agent 文档](https://python.langchain.com/docs/tutorials/agents/) — LangChain 框架的 Agent 实战教程
