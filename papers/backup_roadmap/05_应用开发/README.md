# 05 应用开发

> **阶段定位**：把前 4 章的理论变成能落地的产品。这里学的每一个技术你都在日常工作中用过（只是不知道叫这个名字）。
> **总时长**：约 6-8 周
> **前置依赖**：01-04 全部（至少理解 Transformer 和 Embedding）

---

## 5.1 RAG (Retrieval-Augmented Generation)

**核心目标**：理解 RAG = 先检索再生成——给 LLM 一本"参考书"，而不是让它裸答。

### 5.1.1 RAG Pipeline 全景

| 阶段 | 组件 | 你的选择 | 时间 |
|------|------|----------|------|
| 文档预处理 | PDF/文本 → 清洗 → 切块 | 2 天 |
| Chunking | Semantic / Recursive / Token-level | 2 天 |
| Embedding | text-embedding-3-small / bge-large-zh | 1 天 |
| 向量存储 | Chroma (入门) / FAISS (轻量) / Milvus (生产) | 1 天 |
| 检索 | 相似度搜索 + Rerank (Cohere / BGE-Reranker) | 2 天 |
| 生成 | 拼接 prompt → LLM 回答 | 1 天 |

**BIOS 类比**：
- RAG Pipeline → `BIOS_Knowledge_Library/` 项目：spec PDF → Embedding → 检索 → Claude 回答
- Chunking → 把 BIOS spec 按章节切分（一个 chapter 一个 chunk）
- 检索 → 用户在 BIOS Setup 界面按 F1 查帮助文本

### 5.1.2 RAG 进阶

| 技术 | 解决的问题 | 时间 |
|------|-----------|------|
| HyDE | 用户问得不好，先生成一个假设答案再检索 | 1 天 |
| Self-RAG | 模型自己判断是否需要检索，以及检索结果是否相关 | 1 天 |
| Graph RAG | 知识图谱 + RAG，处理多跳推理 | 2 天 |
| 多模态 RAG | 检索图片、表格、代码 | 选读 |

**推荐资源**：
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [LlamaIndex RAG Guide](https://docs.llamaindex.ai/en/stable/understanding/rag/)

---

## 5.2 Agent 架构

**核心目标**：理解 Agent = LLM + 工具 + 记忆 + 规划。你已经在用了。

### 5.2.1 Agent 核心组件

| 组件 | 说明 | BIOS 类比 | 时间 |
|------|------|-----------|------|
| Tool Definition | OpenAI Function Calling Schema / MCP 协议 | BIOS Skill 定义 | 1 天 |
| Tool Routing | LLM 判断调哪个工具 | Dispatcher 路由到对应 handler | 1 天 |
| Planning | ReAct / Plan-and-Execute | BIOS Boot Flow (PEI→DXE→BDS) | 2 天 |
| Memory | Vector Memory / Conversation Buffer | 3 层记忆系统 (rules/tasks/local) | 1 天 |
| Orchestration | LangChain Agent / LlamaIndex Agent | DXE Dispatcher | 1 天 |

### 5.2.2 Agent 关键协议

| 协议 | 说明 | 时间 |
|------|------|------|
| **MCP (Model Context Protocol)** | Anthropic 的标准化 tool 协议，你已在用 | 2 天 |
| **OpenAI Function Calling** | OpenAI 原生 tool call 格式 | 1 天 |
| **A2A (Agent-to-Agent)** | Google 的多 Agent 协作协议 | 选读 |

**你已有的 Agent 实践经验**：
- `.claude/skills/` 下 18 个 Skill → 这就是 Tool Definition + Tool Routing
- `@Code_Change_Rules_CN.md` + Cursorrules → 这就是 System Prompt Engineering
- 3 层记忆系统 → 这就是 Memory Hierarchy

---

## 5.3 API 与部署

**核心目标**：把模型变成可调用的 API 服务，处理并发和性能。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| 本地推理 | Ollama (入门) / vLLM (生产) — 对比选择 | 2 天 |
| API 服务 | FastAPI + async + GPU server | 2 天 |
| Streaming vs Batch | SSE (Server-Sent Events) vs 一次性返回 | 1 天 |
| 量化 (Quantization) | GPTQ / AWQ / GGUF — 4-bit/8-bit 的意义和损失 | 2 天 |
| 并发与限流 | 请求队列、Rate Limiting、GPU 显存管理 | 1 天 |

**BIOS 类比**：
- 本地推理 → 本地 build BIOS 不依赖远程（Ollama = 本地 build 环境）
- FastAPI → BMC Redfish REST API（HTTP 接口暴露服务）
- Streaming → SOL (Serial Over LAN) 实时输出 vs SEL (System Event Log) 离线批量
- 量化 → BIOS 镜像压缩（有损压缩，但能跑进 SPI ROM 的容量限制）

---

## 5.4 Prompt Engineering（回顾升华）

你已经掌握但应该理论化的技能：

| 技术 | 你已在用的 | 理论定位 |
|------|-----------|---------|
| System Prompt | `@Code_Change_Rules_CN.md` | 固定前缀注入，控制行为边界 |
| Few-Shot | 代码审查中的示例 | 给模型 2-5 个例子，它学会模式 |
| Chain-of-Thought | 复杂问题的分步分析 | "Let's think step by step" |
| Structured Output | Label 模板生成 | JSON Mode / Pydantic schema 约束 |

---

## 交叉引用

- RAG 的 Embedding → **03_深度学习基础** Embedding 章节
- RAG 的 Chunking 策略 → **03_深度学习基础** Tokenization 章节
- Agent 的 Tool Definition → **04_LLM原理** Function Calling 机制
- API 部署的 Quantization → **04_LLM原理** LoRA/QLoRA 量化方案

**对应知识图谱章节**：

| 本章节 | 知识图谱对应位置 |
|--------|-----------------|
| RAG 全部 | `02_AI应用技术 / 2-1_RAG理论知识+案例详解+实操` |
| Agent 全部 | `02_AI应用技术 / 2-2_Agent理论知识+案例详解+实操` |
| API 与部署 | `01_AI大模型基础 / 1-3_模型部署及高并发` |
| Prompt Engineering | `01_AI大模型基础 / 1-1_理论知识 / 1-1-1` |

---

## 推荐资源

| 资源 | 覆盖范围 | 优先级 |
|------|---------|--------|
| [DeepLearning.AI Short Courses](https://www.deeplearning.ai/short-courses/) | RAG/Agent/Function Calling 微课系列 | ★★★ |
| [Lil'Log Blog](https://lilianweng.github.io/) | Agent/RAG 工业级深度文章 | ★★★ |
| [LangChain 官方文档](https://python.langchain.com/) | RAG + Agent 框架 | ★★☆ |
| [Ollama 官方文档](https://ollama.com/) | 本地模型运行 | ★★☆ |
| [vLLM 官方文档](https://docs.vllm.ai/) | 高性能推理引擎 | ★☆☆ 进阶 |

---

## 学习检查清单

- [ ] 用 LangChain/LlamaIndex 跑通了一个完整的 RAG pipeline（文档→检索→回答）
- [ ] 理解了 Chunking 策略对检索质量的影响（chunk size 越大越全但越贵）
- [ ] 本地用 Ollama 跑了一个模型，并用 FastAPI 封成了 API
- [ ] 能用 Function Calling 让 Claude 调用你写的工具函数
- [ ] 理解了 MCP 协议的基本原理（Client-Server-Tool 三层模型）
- [ ] 了解了 Streaming vs Batch 的区别和使用场景
- [ ] 至少尝试了一种量化方案（GGUF/GGML），并测量了文件大小和推理速度的变化
