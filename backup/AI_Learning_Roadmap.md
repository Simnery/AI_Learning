# AI 系统学习路线图

> **学习者画像**: BIOS 固件工程师 → AI 应用开发
> **基础**: 无 AI 理论，但具备丰富的 AI 工具集成实践经验
> **学习风格**: 实践驱动，自下而上

---

## 0. 你已掌握的 AI 能力（概念映射）

| 你做的 BIOS 项目实践 | 对应的 AI/ML 概念 |
|---|---|
| `BIOS_Knowledge_Library/` | **RAG (检索增强生成)** |
| `.claude/skills/` 下 18 个 Skill | **Agent / Tool Use / Function Calling** |
| `.cursorrules` + `Code_Change_Rules_CN.md` | **System Prompt Engineering / Constitutional AI** |
| Label 生成 (`CP-SY-YYYYMMDD-V001`) | **Template-based Generation / Structured Output** |
| 3 层记忆系统 (rules/tasks/local) | **Memory Hierarchy / Context Management** |
| BIOS 模块分析文档 | **Knowledge Distillation** |
| Code Change 标记 | **Diff Format / Sequence Labeling** |
| `HOW_TO_USE_AI_RULES.md` 三层方案 | **AI Safety / Prompt Injection 防护** |

**结论**: 你已经在做 AI 应用开发了，只是用的是 "手工 Prompt Engineering" 而非 "算法理解驱动"。

---

## 1. 第一阶段：AI/ML 基础理论（4-6 周）

### 1.1 数学基础「按需补，不贪多」

| 内容 | 优先级 | 时间 |
|------|--------|------|
| 线性代数：矩阵乘、向量、点积 | ⭐⭐⭐ | 1 周 |
| 微积分：导数、梯度下降 | ⭐⭐⭐ | 3 天 |
| 概率：条件概率、贝叶斯、softmax | ⭐⭐ | 3 天 |
| 统计：均值/方差、交叉熵 | ⭐⭐ | 2 天 |

**推荐资源**:
- [3Blue1Brown 线性代数](https://www.3blue1brown.com/topics/linear-algebra)
- [StatQuest 机器学习](https://www.youtube.com/@statquest)
- [Andrej Karpathy - Let's build GPT from scratch](https://www.youtube.com/watch?v=kCc8FmEb1nY)

### 1.2 ML 基础概念

| 概念 | BIOS 类比 |
|------|----------|
| 监督学习 vs 无监督学习 | 有 Spec 的开发 vs 逆向分析 |
| 损失函数 (Loss) | POST Code 报错——告诉你偏差多大 |
| 梯度下降 | 反复调参数直到 POST 过 |
| 过拟合 | 代码只在 CRB 能跑，量产全挂 |
| 训练/验证/测试集 | 开发调测 / QA 验证 / 客户验收 |

### 1.3 深度学习基础

| 概念 | BIOS 类比 |
|------|----------|
| 神经网络 (NN) | DXE Dispatcher — 层层传递 |
| Backpropagation | SMM SMI 的嵌套调用回溯 |
| Embedding | UEFI Protocol GUID → 实际功能函数 |
| Tokenization | 日志解析中的 Token 拆分 |
| Attention (QKV) | HOB 的 Producer-Consumer |

---

## 2. 第二阶段：LLM 原理（4-6 周）

| 组件 | 核心问题 |
|------|---------|
| Input Embedding | Token 在向量空间中的位置关系 |
| Positional Encoding | 为什么需要位置编码 |
| Self-Attention | Q/K/V 的物理含义，多头的作用 |
| Feed Forward (FFN) | GPT 的"知识"存在哪 |
| GPT vs BERT | Decoder-only vs Encoder-only |
| LoRA | 只打一个 Override patch |

---

## 3. 第三阶段：AI 应用开发核心技术（6-8 周）

### 3.1 RAG

| RAG 组件 | 标准做法 |
|----------|---------|
| Document Corpus | 原始文档 |
| Chunking | Sematic/Recursive/Token-level 切分 |
| Embedding | text-embedding-3-small / bge-large |
| Vector Store | Chroma / FAISS / Milvus |
| Retrieval | Similarity Search + Rerank |

### 3.2 Agent 架构

| Agent 概念 | 标准方案 |
|-----------|---------|
| Tool Definition | OpenAI Function Calling Schema / MCP |
| Tool Routing | LLM 判断调用哪个 tool |
| Orchestration | LangChain Agent / LlamaIndex Agent |
| Memory | Vector Memory / Conversation Buffer |

### 3.3 API 与部署

| 概念 | BIOS 类比 |
|------|----------|
| vLLM / Ollama | 本地构建运行 |
| FastAPI + GPU Server | BMC Redfish API |
| Streaming vs Batch | SOL 实时串口 vs SEL 离线批量 |
| Quantization | BIOS 镜像压缩 |

---

## 4. 第四阶段：项目实战

### 推荐项目顺序
1. **BIOS 智能问答系统**（RAG 入门）— Ollama + Chroma + LangChain
2. **BIOS 日志智能分析器**（Agent）— FastAPI + Agent + 历史日志向量库
3. **代码 Review Agent**（Agent + Tool Use）— 自动验证代码规则
4. **向量化 BIOS Spec 检索** — PDF Parsing + Embedding + RAG

---

## 5. 推荐学习顺序

```
优先级 ★★★（立刻开始）
  ├── Andrej Karpathy "Let's build GPT" 视频
  ├── 3Blue1Brown 神经网络 3 集
  ├── 本地装 Ollama，跑一个模型
  └── 项目 1：BIOS 知识库做成 RAG

优先级 ★★（前 3 周内）
  ├── Transformer 架构完整理解
  ├── Tokenization / Embedding 原理
  ├── PyTorch 手写 MLP 做 MNIST
  └── Fine-tuning 入门（LoRA）

优先级 ★（1-2 个月内）
  ├── RLHF / DPO 原理
  ├── Diffusion 模型初步
  ├── MCP 协议深入
  └── 模型量化与推理优化
```

---

## 6. 核心资源索引

| 资源 | 适合阶段 | 特点 |
|------|---------|------|
| [3Blue1Brown 深度学习](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi) | 第 1 阶段 | 数学可视化 |
| [StatQuest ML](https://www.youtube.com/@statquest) | 第 1 阶段 | 10-15 分钟/概念 |
| [Karpathy Zero to Hero](https://www.youtube.com/playlist?list=PLAqhIrjkxrVzFWr7G9gCu9RJMh0Cd_gIx) | 第 1-2 阶段 | 逐行写代码 |
| [HuggingFace NLP Course](https://huggingface.co/learn/nlp-course) | 第 2 阶段 | tokenizer 到 fine-tune |
| [Annotated Transformer](http://nlp.seas.harvard.edu/2018/04/03/attention.html) | 第 2 阶段 | Attention 逐行讲解 |
| [Lil'Log Blog](https://lilianweng.github.io/) | 第 3 阶段 | Agent/RAG 工业解读 |
| [DeepLearning.AI Short Courses](https://www.deeplearning.ai/short-courses/) | 全程 | 1-2 小时微课 |
| [fast.ai Practical DL](https://course.fast.ai/) | 第 1-2 阶段 | Top-down 教学 |

---

> 当你学完 Transformer 的 Attention 回头看 `@Code_Change_Rules_CN.md` 时，你会恍然大悟：原来 Claude 是这样"关注"我那 50KB 规则文档的。
