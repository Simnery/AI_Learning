# 5.1 企业知识库（企业RAG大赛冠军项目）

> 5.1 企业RAG大赛冠军项目 > 5. 项目实战

## 核心概念

- **是什么**：本项目拆解一个企业 RAG 大赛的冠军方案——如何从零搭建一个企业级知识库问答系统，涵盖文档解析、检索、重排序、生成、调优全链路。核心是理解"冠军方案为什么比基线好"。
- **为什么重要**：RAG 是 LLM 应用中最成熟的落地范式。理解冠军方案的每个设计决策，比看 10 篇论文更有实战价值。你会知道每个组件选什么、参数怎么调、坑在哪里。
- **前置知识**：RAG 基础（参考 [2-1-2 RAG技术与应用](../02_AI应用技术/2-1_RAG理论知识+案例详解+实操/2-1-2_RAG技术与应用.md)）、Embedding与向量数据库（参考 [2-1-1 Embeddings和向量数据库](../02_AI应用技术/2-1_RAG理论知识+案例详解+实操/2-1-1_Embeddings和向量数据库.md)）。

## 原理讲解

### 1. 冠军方案架构：多路由+动态知识库

基线 RAG 是单一路径：文档→切分→向量化→检索→拼接→生成。冠军方案的核心改进是两个"动态"：

```
                            ┌─────────────────┐
用户提问 ──→ 路由判断 ──→  │  关键词路由       │ → BM25检索 → 文档片段
              │            │  (精确查询)        │
              │            ├───────────────────┤
              └────────────│  语义路由          │ → 向量检索 → 文档片段
                           │  (模糊查询)        │
                           ├───────────────────┤
                           │  混合路由          │ → BM25+向量 → 融合排序
                           │  (复杂查询)        │
                           └───────────────────┘
                                    ↓
                            多路结果融合（RRF）
                                    ↓
                            LLM 重排序（Rerank）
                                    ↓
                            父页面检索（Parent Retrieval）
                                    ↓
                            指令细化 → LLM 生成
```

### 2. 关键技术点解析

| 技术点 | 为什么重要 | 冠军做法 |
|--------|-----------|---------|
| 文档解析 | 解析质量决定知识库上限 | Docling + 表格序列化优化 |
| 检索策略 | 单一路由无法覆盖所有查询类型 | 多路由：关键词/语义/混合，按查询类型动态切换 |
| 重排序 | 向量检索的 Top-K 不一定是最好的 | LLM Reranking 精排前 10，准确率提升 15%+ |
| 父页面检索 | 小块检索精确但丢失上下文 | 先检索小块 → 追溯完整父页面 → 喂给 LLM |
| 结构化输出 | LLM 自由生成不可控 | 思维链 + JSON Schema 约束输出 |
| 指令细化 | 用户提问太随意 | 先让 LLM 优化提问，再检索 |

### 3. RAG 系统调参核心

| 参数 | 作用 | 调参方向 | 典型值 |
|------|------|---------|--------|
| chunk_size | 文档切分大小 | 太小缺上下文/太大检索不准 | 200-500 |
| chunk_overlap | 块间重叠 | 防止切断关键句子 | 10-20% |
| top_k | 检索返回数 | 太少信息不够/太多噪声 | 3-10 |
| temperature | 生成随机性 | RAG 用 0（确定性），创意用 0.7 | 0 |
| rerank_top_n | 重排序后保留数 | 平衡上下文窗口和有效性 | 3-5 |

## 代码实战

### 示例1：多路由检索器

```python
# pip install — 本示例仅用 Python 3.10+ 标准库

"""多路由检索器——根据查询类型自动选择检索策略"""
from typing import Literal

class MultiRouteRetriever:
    def __init__(self, bm25_index, vector_store, llm):
        self.bm25 = bm25_index
        self.vector = vector_store
        self.llm = llm
    
    def classify_query(self, query: str) -> Literal["keyword", "semantic", "hybrid"]:
        """判断查询类型"""
        prompt = f"""判断以下查询的类型，只输出一个词(keyword/semantic/hybrid)：
- keyword: 精确查找（人名/编号/日期/术语）
- semantic: 概念性问题（"如何""为什么""是什么"）
- hybrid: 既有精确条件又有语义需求

查询: {query}"""
        return self.llm.complete(prompt).strip()
    
    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        route = self.classify_query(query)
        print(f"路由: {route}")
        
        if route == "keyword":
            return self.bm25.search(query, top_k)
        elif route == "semantic":
            return self.vector.similarity_search(query, k=top_k)
        else:  # hybrid
            bm25_results = self.bm25.search(query, top_k)
            vector_results = self.vector.similarity_search(query, k=top_k)
            return self._rrf_fusion(bm25_results, vector_results, top_k)
    
    def _rrf_fusion(self, list_a, list_b, k: int):
        """RRF (Reciprocal Rank Fusion) 融合"""
        scores = {}
        for rank, doc in enumerate(list_a):
            scores[doc] = scores.get(doc, 0) + 1.0 / (60 + rank)
        for rank, doc in enumerate(list_b):
            scores[doc] = scores.get(doc, 0) + 1.0 / (60 + rank)
        return sorted(scores, key=scores.get, reverse=True)[:k]
```

### 示例2：LLM 重排序

```python
"""LLM Reranking——用 LLM 精排检索结果"""
def llm_rerank(query: str, docs: list[str], llm, top_n: int = 3) -> list[str]:
    prompt = f"""从以下文档片段中，选出与问题最相关的 {top_n} 条。

问题: {query}

文档片段:
{chr(10).join(f'[{i+1}] {doc[:300]}' for i, doc in enumerate(docs))}

输出最相关的 {top_n} 条序号，用逗号分隔，如: 3,1,5"""
    
    response = llm.complete(prompt)
    indices = [int(x.strip()) - 1 for x in response.split(",")]
    return [docs[i] for i in indices[:top_n]]
```

### 示例3：指令细化 + 结构化生成

```python
"""指令细化：优化用户的模糊提问"""
def refine_query(raw_query: str, llm) -> str:
    prompt = f"""将以下模糊问题改写为更精准的检索查询。
保留原意，但补充关键词、消除歧义、明确范围。

原始: {raw_query}
改写: """
    return llm.complete(prompt)

"""结构化输出：约束 LLM 按格式回答"""
def structured_answer(context: str, query: str, llm) -> dict:
    prompt = f"""根据以下上下文回答问题，输出 JSON:
{{"answer": "回答内容",
 "citations": ["引用的文档片段1", "片段2"],
 "confidence": 0.0-1.0,
 "follow_up": ["建议的追问1", "追问2"]}}

上下文: {context}
问题: {query}"""
    import json
    return json.loads(llm.complete(prompt))
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
| 文档解析精度 | 复杂表格、扫描件 PDF、手写内容的解析准确率仍有瓶颈，可能造成知识库"先天不足" |
| 路由判断准确性 | 查询分类器本身可能出错——把语义查询误判为关键词查询，导致检索路径错误 |
| 多轮对话 | 当前方案偏重单轮问答，多轮追问场景下上下文维护和历史理解是挑战 |
| 知识更新 | 企业文档频繁更新时，向量索引的增量更新和版本管理没有成熟方案 |

### 下一步学什么

1. **[2-1-4 RAG调优](../02_AI应用技术/2-1_RAG理论知识+案例详解+实操/2-1-4_RAG调优.md)** — 系统学习 RAG 的优化方法论
2. **[2-1-3 多模态RAG](../02_AI应用技术/2-1_RAG理论知识+案例详解+实操/2-1-3_RAG多模态数据处理.md)** — 处理图片、表格等非文本知识
3. **[5-7 LLM Wiki](../5-7_LLM_Wiki/)** — 构建结构化知识库的进阶方案

### 工业界最佳实践

- **A/B 测试检索策略**：同时上线两套检索方案，用真实用户反馈（点赞/踩/无反馈）评估效果差异
- **检索日志分析**：记录每次查询的路由类型、检索耗时、Top-K 文档 ID，离线分析检索质量
- **知识库健康度监控**：定期检查文档覆盖率、过期文档比例、embedding 漂移程度

## 常见问题

### 小白最常踩的 3 个坑

**坑 1：直接用 LangChain 默认参数，不做调优**

LangChain 默认 chunk_size=1000、chunk_overlap=200，这些值不是最优的。不同文档类型需要不同切分策略——技术文档适合小块（200-500）、法律合同适合大块（800-1500）。不调参数直接上线，检索准确率可能只有 60%。

**坑 2：向量检索返回 Top-5 就喂给 LLM，不做重排序**

向量检索的 "相似" 不等于 "相关"。Top-5 中可能有 2-3 条是噪声。加一层 LLM Reranking 精排，准确率提升 15-20%，代价只是多一次 LLM 调用（约 0.5s）。

**坑 3：只关注检索，忽略文档解析质量**

知识库的瓶颈往往不是检索算法，而是文档解析——PDF 表格被拆散、扫描件 OCR 出错、图片中的文字没提取。文档解析是 RAG 的"天花板"，解析质量差，后面怎么优化都白搭。

### 自检题

**Q1**：多路由检索比单一向量检索好在哪里？<details><summary>答案</summary>单一向量检索对所有查询一视同仁，但不同类型查询需要不同策略：精确查询适合关键词（BM25），概念查询适合语义（向量），复杂查询需要两者融合。多路由根据查询类型动态选择最优策略。</details>

**Q2**：LLM Reranking 为什么能提升准确率？<details><summary>答案</summary>向量检索用 embedding 相似度排序，但"相似"不等于"相关"。LLM 能理解语义细微差别，把"真正有用"的片段排到前面，过滤掉"相似但不相关"的噪声。</details>

**Q3**：RAG 系统调参中，chunk_size 过大和过小分别有什么问题？<details><summary>答案</summary>过大（>1000）：检索到的块噪声多、可能包含不相关内容，且拼接后容易超出 LLM 上下文窗口。过小（<100）：语义碎片化，缺少必要上下文，LLM 难以理解。一般 200-500 字是甜区。</details>

## 延伸阅读

- [LangChain RAG 教程](https://python.langchain.com/docs/tutorials/rag/)
- [RRF 论文](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- 第二章 RAG 系列节点（2-1-1 ~ 2-1-5）
