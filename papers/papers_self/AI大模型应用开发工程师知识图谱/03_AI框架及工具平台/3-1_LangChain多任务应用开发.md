# 3.1 LangChain：多任务应用开发

> 3.1 LangChain 多任务应用开发 > 3. AI框架及工具平台

## 核心概念

- **是什么**：LangChain 是一个开源框架，专门用来构建基于大语言模型（LLM）的应用。它把常见的 LLM 开发模式（链式调用、工具使用、记忆管理、RAG）封装成标准化组件，让你像搭积木一样组合出复杂应用。
- **为什么重要**：直接调 LLM API 只能做简单的"一问一答"。实际应用需要多步推理、查数据库、调外部工具、记住上下文——这些 LangChain 都帮你处理好了，不用从头造轮子。
- **前置知识**：Python 基础、了解 LLM API 调用方式（参考 [1-2-1 AI基本原理及API使用](../01_AI大模型基础/1-2_实操基础/1-2-1_AI大模型基本原理及API使用.md)）、理解 RAG 基本概念（参考 [2-1-2 RAG技术与应用](../02_AI应用技术/2-1_RAG理论知识+案例详解+实操/2-1-2_RAG技术与应用.md)）。

### LangChain 六大核心组件

| 组件 | 职责 | 一句话理解 |
|------|------|-----------|
| **Models** | 对接各种 LLM（OpenAI、ChatGLM、Ollama 等） | "大脑" |
| **Prompts** | 管理提示词模板，支持变量插值、Few-Shot | "指令" |
| **Memory** | 存储对话历史，让模型"记住"之前的交互 | "记忆" |
| **Indexes** | 管理文档加载、切分、向量化、检索 | "知识库" |
| **Chains** | 把多个组件串联成执行流程 | "流水线" |
| **Agents** | 让 LLM 自主决定调用哪些工具、按什么顺序 | "决策者" |

## 原理讲解

### 1. LangChain 的工作原理

LangChain 的核心思想是**组件化 + 管道化**。你可以把每个组件想象成一个乐高积木，Chain 就是把这些积木拼在一起的说明书：

```
用户输入 → Prompt模板(填充变量) → LLM调用 → 输出解析 → 返回结果
```

LCEL（LangChain Expression Language）用 `|` 管道符串联组件，底层自动处理回调、流式输出、异步等：

```
chain = prompt | model | output_parser
```

### 2. Agent 的工作原理（ReAct 模式）

Agent 不按固定流程执行，而是**观察→思考→行动→观察**的循环：

```
用户: "今天北京天气怎么样？告诉我适合穿什么"

Agent 思考: 需要先查天气 → 调用天气API工具
Agent 观察: 得到"25°C，晴"
Agent 思考: 25°C适合穿薄外套 → 生成最终回答
Agent 回答: "今天北京25°C，晴天，建议穿薄外套或长袖T恤"
```

这个模式叫 **ReAct**（Reasoning + Acting）：模型一边推理一边调用工具，直到能回答为止。

### 3. RAG 在 LangChain 中的实现

```
文档加载 → 文本切分 → 向量化(Embedding) → 存入向量库(Index)
                                                    ↓
用户提问 → 向量检索(Retrieve) → 拼接上下文 + 提问 → LLM生成答案
```

### 4. Memory 机制

LangChain 支持多种记忆类型：

| 类型 | 特点 | 适用场景 |
|------|------|----------|
| ConversationBufferMemory | 存全部历史，越来越长 | 短对话 |
| ConversationSummaryMemory | 自动摘要压缩 | 长对话 |
| ConversationBufferWindowMemory | 只保留最近 K 轮 | Token 敏感场景 |
| VectorStoreRetrieverMemory | 存入向量库，语义检索 | 海量历史 |

## 代码实战

> 依赖安装：`pip install langchain langchain-openai langchain-community faiss-cpu python-dotenv`

### 示例1：第一个 LCEL 链

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

os.environ["OPENAI_API_KEY"] = "your-api-key"  # 或用 dotenv 加载

# 1. 定义 Prompt 模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，用{style}的风格回答问题。"),
    ("user", "{question}")
])

# 2. 创建模型
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 3. 输出解析器
parser = StrOutputParser()

# 4. 用 LCEL 串联成链
chain = prompt | model | parser

# 5. 调用
result = chain.invoke({
    "role": "小学数学老师",
    "style": "生动有趣",
    "question": "为什么1+1=2？"
})
print(result)
# 预期输出: 一段生动有趣的数学解释，适合小学生理解
```

### 示例2：RAG 知识问答（从零搭建）

```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ---- 第一步：准备知识库 ----
# 假设你有一个 knowledge.txt，内容是产品手册
loader = TextLoader("knowledge.txt", encoding="utf-8")
documents = loader.load()

# 切分文档（每块200字符，重叠20字符）
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, chunk_overlap=20
)
chunks = text_splitter.split_documents(documents)

# 向量化并存入 FAISS
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)

# ---- 第二步：构建 RAG 链 ----
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

template = """根据以下上下文回答问题。如果不知道，就说不知道，不要编造。

上下文：
{context}

问题：{question}
回答："""

prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI(model="gpt-3.5-turbo")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# ---- 第三步：提问 ----
answer = rag_chain.invoke("产品支持哪些支付方式？")
print(answer)
```

### 示例3：Agent——让 LLM 自主调用工具

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate

# 定义工具1：计算器（纯 Python 实现）
@tool
def calculator(expression: str) -> str:
    """计算数学表达式，例如 '2+3*4'"""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算出错: {e}"

# 定义工具2：模拟知识库查询
@tool
def query_product_db(product_name: str) -> str:
    """查询产品信息，输入产品名称，返回库存和价格"""
    db = {
        "机械键盘": "库存: 150, 价格: ¥399",
        "无线鼠标": "库存: 80, 价格: ¥199",
        "显示器": "库存: 30, 价格: ¥2499",
    }
    return db.get(product_name, "未找到该产品")

tools = [calculator, query_product_db]

# 创建 Agent
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的助手，可以使用工具来回答问题。"),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 测试1：需要计算
result = executor.invoke({"input": "机械键盘买3个加2个无线鼠标，总共多少钱？"})
print(result["output"])

# 测试2：需要查库+计算
result = executor.invoke({"input": "显示器库存的一半是多少？"})
print(result["output"])
```

### 示例4：带记忆的多轮对话

```python
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationChain

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 使用摘要记忆——长对话自动压缩
memory = ConversationSummaryMemory(
    llm=llm,
    return_messages=True,
    max_token_limit=500,  # 摘要控制在500 token内
)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 多轮对话
print(conversation.predict(input="我叫小明，是一名Python初学者"))
print(conversation.predict(input="帮我设计一个3天的Python学习计划"))
print(conversation.predict(input="我刚才说我叫什么？我的水平如何？"))
# 预期: 模型能记住"小明"和"初学者"
```

### 示例5：搭建故障诊断 Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
import subprocess
import platform

@tool
def check_disk_space() -> str:
    """检查磁盘剩余空间"""
    import shutil
    total, used, free = shutil.disk_usage("/")
    return f"总空间: {total//(2**30)}GB, 已用: {used//(2**30)}GB, 剩余: {free//(2**30)}GB"

@tool
def check_processes(keyword: str = "") -> str:
    """查看系统进程，keyword 为空则显示 CPU 占用最高的5个进程"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["tasklist", "/fo", "csv", "/nh"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            return "\n".join(lines[:10])  # 返回前10行
        else:
            result = subprocess.run(
                ["ps", "aux", "--sort=-%cpu"],
                capture_output=True, text=True, timeout=5
            )
            return "\n".join(result.stdout.strip().split("\n")[:10])
    except Exception as e:
        return f"检查进程失败: {e}"

tools = [check_disk_space, check_processes]

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一位资深运维工程师。用户报告系统问题时，请：
1. 先用工具收集诊断信息
2. 分析可能的原因
3. 给出解决建议
始终用中文回答。"""),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = executor.invoke({"input": "我的电脑运行很慢，帮我诊断一下"})
print(result["output"])
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

### 1. 当前局限性

- **复杂工作流**：简单的 Chain 和 Agent 难以表达条件分支、循环、并行等复杂逻辑 → 用 **LangGraph** 解决
- **可观测性差**：Agent 执行过程是黑盒，出错难排查 → 用 **LangSmith** 追踪每一步
- **生态碎片化**：社区包质量参差不齐，API 变动频繁

### 2. 下一步学习

| 主题 | 说明 | 相关节点 |
|------|------|----------|
| LangGraph | 状态图驱动的 Agent 工作流 | 本文进阶内容 |
| LangSmith | LLM 应用调试与监控平台 | 本文进阶内容 |
| LlamaIndex | 更适合数据密集型 RAG 的框架 | [3-2 AI框架设计与选型](3-2_AI框架设计与选型.md) |
| MCP 协议 | Agent 与工具的标准通信协议 | [2-2-1 Function Calling与MCP](../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-1_Function_Calling与MCP.md) |

### 3. 工业界最佳实践

- **不要过度抽象**：简单场景直接用 API + LCEL，复杂再上 Agent
- **LangSmith 必开**：生产环境一定要追踪调用链，否则 Agent 随机性会让你无从排查
- **工具设计要原子化**：每个工具只做一件事，描述清楚，减少 Agent 误判

## 常见问题

### 小白最常踩的坑

1. **API Key 硬编码**：不要把 key 写死在代码里，用 `.env` 文件 + `python-dotenv` 加载，或者用环境变量
2. **文档切分不当**：RAG 中 `chunk_size` 太小导致上下文不完整，太大导致检索不精准。一般从 200-500 开始试
3. **Agent 无限循环**：Agent 有时候会反复调用工具得不到结果。设置 `max_iterations` 参数（默认10）限制执行步数

### 自检题

**Q1**：LangChain 的六大核心组件是什么？分别负责什么？

<details><summary>答案</summary>

- Models：对接 LLM，统一调用接口
- Prompts：管理提示词模板
- Memory：存储和检索对话历史
- Indexes：文档加载、切分、向量化、检索
- Chains：串联多个组件形成执行流程
- Agents：让 LLM 自主选择调用哪些工具
</details>

**Q2**：ReAct 模式的全称是什么？它的核心循环是怎样的？

<details><summary>答案</summary>

ReAct = Reasoning + Acting（推理 + 行动）。核心循环：Thought（思考下一步做什么）→ Action（调用工具）→ Observation（观察工具返回结果）→ 回到 Thought，直到能回答用户问题。
</details>

**Q3**：LCEL 中用 `|` 管道符串联组件时，底层自动处理了哪些能力？（至少说3个）

<details><summary>答案</summary>

1. **同步/异步兼容**：`invoke()` / `ainvoke()` 自动适配
2. **流式输出**：`stream()` 自动将每个组件的输出流式传递
3. **回调追踪**：所有组件的输入/输出自动触发回调（LangSmith 集成）
4. **错误传播**：链中任一组件的异常会自动包装堆栈信息
5. **并行执行**：`RunnableParallel` 自动并发调用
</details>

## 延伸阅读

### 中文资料

- [LangChain 官方文档（中文翻译）](https://docs.langchain.com.cn/) — 社区维护的中文文档，入门必读
- [LangChain 实战：从入门到放弃再到精通](https://docs.python.org/3/) — 知乎专栏，踩坑经验分享
- [B站：LangChain 零基础入门教程](https://search.bilibili.com/all?keyword=LangChain%E5%85%A5%E9%97%A8) — 视频讲解，适合跟练
- [LangGraph 中文教程](https://github.com/langchain-ai/langgraph/tree/main/docs/docs/how-tos) — 官方 How-To 指南，代码即文档

### 英文资料（可能需科学上网）

- [LangChain 官方文档](https://python.langchain.com/docs/) — 最权威的 API 参考和教程
- [LangChain YouTube 频道](https://www.youtube.com/@LangChain) — 官方视频教程，含 Office Hours Q&A
- [LangSmith 文档](https://docs.smith.langchain.com/) — LLM 应用可观测性平台
- [LangGraph 官方教程](https://langchain-ai.github.io/langgraph/tutorials/) — Agent 工作流最佳实践
