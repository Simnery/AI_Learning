# 1.3.3 SGLang深度优化：Radix缓存与复杂任务的极致吞吐

> 1.3 模型部署及高并发 > 1. AI大模型基础

---

## 核心概念


### 前置知识

- 建议先阅读本知识图谱同级目录中的先修节点（见进阶方向中的内部链接）。

### SGLang 是什么

SGLang 是专为**复杂 LLM 工作流**设计的推理框架。vLLM 擅长简单问答（"问一句答一句"），SGLang 擅长需要多步推理、工具调用的复杂任务（RAG、Agent、CoT）。

**核心创新**：RadixAttention + 结构化编程模型。

```
vLLM 思路：优化"一次推理"的速度 → 让每个请求尽可能快
SGLang 思路：优化"一系列推理"的共享 → 让相关请求尽可能不重复计算
```

### 为什么需要 SGLang

RAG 场景中，所有用户共享同一个 System Prompt + 检索出的文档前缀。传统方案每个请求都从头计算 KV Cache，SGLang 通过 RadixAttention 自动识别和复用这些共享前缀。

---

## 原理讲解

### Radix Tree（基数树）原理

Radix Tree 是一种空间优化的前缀树（Trie）。在 SGLang 中，每个节点的 key 是 token 序列，value 是对应的 KV Cache 页。

```
传统 KV Cache：              RadixAttention：
每个请求独立计算前缀            自动前缀检测和共享

请求1: "你是一个助手。今天     ┌── "你是一个助手。" ──┐
       天气如何？"             │  (KV Cache 共享)      │
                              ├── "今天天气如何？" ───┤ 请求1
请求2: "你是一个助手。Python   │                       │
       是什么？"               ├── "Python是什么？" ───┤ 请求2
                              ├── "深度学习是什么？" ─┤ 请求3
请求3: "你是一个助手。深度学   │                       │
       习是什么？"             └───────────────────────┘

共享部分只计算一次！
```

**Radix Tree 的节点合并规则**：
- 两个节点有共同前缀 → 创建一个父节点
- 子节点存储差异部分
- 匹配时从根遍历，沿途复用 KV Cache 页

### RadixAttention vs PagedAttention

| | PagedAttention (vLLM) | RadixAttention (SGLang) |
|---|---|---|
| **粒度** | 按页（16 tokens） | 按 token 序列前缀 |
| **共享机制** | 同一 prompt 前缀自动共享 | Radix Tree 自动检测所有请求的共同前缀 |
| **适用场景** | 独立请求、批量处理 | 共享前缀多的场景（RAG、Agent） |
| **缓存命中率** | 依赖请求顺序 | 按前缀结构命中，不依赖顺序 |

### Token Healing 技术

问题：SGLang 的 DSL 将一段程序拆成多个 `sgl.gen()` 调用，但 LLM 的输出是连续的。拆分可能导致"断裂"——前一段的最后一个 token 和后一段的第一个 token 不连贯。

Token Healing 在前后段之间"缝合"——让模型看到前段的末尾 token，确保生成连贯。

### SGLang vs vLLM 的选择指南

```
你的任务模式是什么？
   │
   ├── 大量独立、不相关的请求（如：千人各问各的）
   │     → vLLM，吞吐量最优
   │
   ├── 请求间有大量共享前缀（如：同一 System Prompt + 不同资料）
   │     → SGLang，前缀共享节省 30-50% 显存
   │
   └── 需要复杂控制流（先检索 → 分析 → 判断 → 回答）
         → SGLang，结构化编程模型更灵活
```

---

## 代码实战

### 1. SGLang 结构化编程

```bash
pip install "sglang[all]"
```

```python
# sglang_structured.py — SGLang DSL 演示
import sglang as sgl

# 定义结构化生成流程
@sgl.function
def rag_qa(s, context: str, question: str):
    """RAG 问答：先分析上下文，再回答"""
    s += sgl.system("你是一个严谨的问答助手，严格基于上下文回答。")
    s += sgl.user(f"上下文：\n{context}\n\n问题：{question}")
    
    # 阶段1：提取关键信息
    s += sgl.assistant("关键信息：")
    s += sgl.gen("key_info", max_tokens=100, stop=["\n\n"])
    
    # 阶段2：生成答案
    s += sgl.assistant("\n答案：")
    s += sgl.gen("answer", max_tokens=200, stop=["\n\n"])
    
    # 阶段3：评估置信度
    s += sgl.assistant("\n置信度（高/中/低）：")
    s += sgl.gen("confidence", max_tokens=10, 
                 choices=["高", "中", "低"])  # 约束输出只能选这三个

# 运行
context = "Transformer 架构由 Vaswani 等人在 2017 年提出，核心创新是用自注意力机制替代循环神经网络。"
question = "Transformer 的核心创新是什么？什么时候提出的？"

backend = sgl.Runtime(model_path="Qwen/Qwen2.5-7B-Instruct")
sgl.set_default_backend(backend)

result = rag_qa.run(context=context, question=question)
print(f"关键信息：{result['key_info']}")
print(f"答案：{result['answer']}")
print(f"置信度：{result['confidence']}")
```

### 2. Radix Tree 命中的实际效果

```python
# radix_demo.py — 演示前缀共享带来的加速
import sglang as sgl
import time

@sgl.function
def ask(s, question: str):
    s += sgl.system("你是知识渊博的AI助手，用简洁的语言回答问题。")
    s += sgl.user(question)
    s += sgl.assistant(sgl.gen("answer", max_tokens=100))

backend = sgl.Runtime(model_path="Qwen/Qwen2.5-7B-Instruct")
sgl.set_default_backend(backend)

questions = [
    "什么是 Python？",
    "什么是 JavaScript？",  # 与第1个共享 System Prompt 前缀
    "什么是 Golang？",      # 同样共享前缀
]

# 第一个请求：前缀未命中，需要计算
start = time.time()
result1 = ask.run(question=questions[0])
print(f"请求1（冷启动）：{time.time() - start:.2f}s")

# 后续请求：前缀命中，复用 KV Cache
for i, q in enumerate(questions[1:], 2):
    start = time.time()
    result = ask.run(question=q)
    print(f"请求{i}（前缀命中）：{time.time() - start:.2f}s")

# 预期：请求2和3的速度显著快于请求1
```

### 3. 关键代码解读

| 代码段 | 设计意图 |
|--------|---------|
| `sgl.gen("key_info", stop=["\n\n"])` | 用 `stop` 控制阶段边界——生成了双换行就停，进入下一阶段 |
| `choices=["高", "中", "低"]` | 约束输出范围——让 LLM 只在给定选项中选，不需要后处理正则匹配 |
| `sgl.system(...)` 放在函数开头 | 所有请求共享同一个 System Prompt → Radix Tree 自动缓存前缀 |

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
- **SGLang 生态不如 vLLM 成熟**：第三方集成（LangChain、LlamaIndex）支持较少
- **冷启动慢**：第一个无前缀的请求和 vLLM 速度相近，优势在于后续请求

### 下一步学什么
- [2.1 RAG 技术详解](../../02_AI应用技术/2-1_RAG理论知识+案例详解+实操/) — SGLang 在 RAG 场景的最佳实践
- [2.2 Agent 开发](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/) — 复杂 Agent 流程的推理优化

---

## 常见问题

**Q1：SGLang 和 vLLM 能一起用吗？**

不能在同一进程中。但可以在不同服务中分别部署：简单问答丢给 vLLM，复杂 RAG/Agent 流程丢给 SGLang，前端路由分发。

**Q2：Radix Tree 会占用多少额外显存？**

很少。Radix Tree 本身只存储 token 序列和指针，开销在 MB 级别。主要显存还是 KV Cache 页——共享后反而节省显存。

**Q3：什么时候不应该用 SGLang？**

请求几乎不共享前缀（如每个用户问完全不同的话题）、或者只有简单问答不需要控制流 → 用 vLLM 更简单高效。

---

### 自检题

1. RadixAttention 的"前缀共享"和 vLLM 的"相同 prompt 共享"有什么本质不同？
   <details><summary>答案</summary>vLLM 是精确匹配——两个请求的 prompt 必须完全相同时才共享前缀 KV Cache。RadixAttention 用 Radix Tree 管理，任何共同前缀（即使后续不同）都能自动识别和共享，不需要请求完全相同</details>

2. SGLang 的 DSL（`@sgl.function`）解决了什么问题？
   <details><summary>答案</summary>将复杂推理流程（检索→分析→判断→回答）结构化为可编程的步骤。每个 `sgl.gen()` 是独立的生成节点，可以设置不同的参数（温度、停止词、约束选项），而不是把所有内容混在一个 prompt 里</details>

3. Token Healing 解决的具体问题是什么？
   <details><summary>答案</summary>SGLang 的 DSL 将连续生成拆成多个 `sgl.gen()` 节点，节点之间的 token 可能不连贯。Token Healing 在节点边界处注入前一个节点的末尾 token 作为生成上下文，确保语义连贯</details>

---

## 延伸阅读

**推荐资料**（国内可访问）：

- [SGLang 深度解析（知乎）](https://docs.python.org/3/) — RadixAttention 的中文详细解析
- [SGLang GitHub](https://github.com/sgl-project/sglang) — 官方仓库，含完整示例和文档

**国外资料**（可能需科学上网）：

- [SGLang Paper](https://arxiv.org/abs/2312.07104) — SGLang 原始论文
- [vLLM vs SGLang 性能对比](https://blog.vllm.ai/2024/06/20/sglang-vs-vllm.html) — 官方博客的性能对比数据
