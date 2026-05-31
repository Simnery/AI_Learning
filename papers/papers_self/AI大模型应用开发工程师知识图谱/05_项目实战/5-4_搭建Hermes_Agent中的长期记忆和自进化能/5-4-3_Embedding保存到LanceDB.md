# 5.4.3 Embedding保存到LanceDB

> 5.4.3 Embedding保存到LanceDB > 5.4 Hermes长期记忆 > 5. 项目实战

## 核心概念

- **是什么**：LanceDB 是一个专为 AI 工作负载设计的嵌入式向量数据库——无需独立服务，直接在应用中嵌入使用，支持向量检索+全文检索+元数据过滤的混合查询。Hermes 用它来持久化存储和检索记忆的 Embedding。
- **为什么重要**：记忆的四层结构只是组织方式，真正让记忆"可检索"的是向量化+LanceDB。相比 FAISS（进程内但无持久化）和 Chroma（持久化但性能一般），LanceDB 既支持本地持久化又性能优秀。

### 前置知识

- 建议先学 [2-2-1 Function Calling](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-1_Function_Calling与MCP.md)、[2-1-1 Embeddings](../../02_AI应用技术/2-1_RAG理论知识+案例详解+实操/2-1-1_Embeddings和向量数据库.md)。


## 原理讲解

### 混合检索策略

```
用户查询 → Embedding向量
              ↓
    ┌─────────┼─────────┐
    ▼         ▼         ▼
向量检索   全文检索   元数据过滤
(语义相似) (关键词)   (时间/类型/层级)
    │         │         │
    └─────────┼─────────┘
              ▼
        RRF 融合排序
              ▼
        Top-K 结果
```

### LanceDB vs 其他方案

| 维度 | LanceDB | FAISS | Chroma |
|------|---------|-------|--------|
| 部署方式 | 嵌入进程 | 嵌入进程 | 独立服务 |
| 持久化 | ✅ 自动 | ❌ 需手动 | ✅ 自动 |
| 混合检索 | ✅ 原生 | ❌ 仅向量 | ✅ 支持 |
| 过滤查询 | ✅ SQL风格 | ❌ | ✅ |
| 性能 | 高 | 极高 | 中 |


### 3. LanceDB 表设计（Hermes 记忆库）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | UUID |
| layer | int | 0–3 颗粒度 |
| content | string | 记忆正文 |
| vector | float[] | 768/1024 维 |
| created_at | timestamp | 用于衰减排序 |

**检索**：新任务来时 `hybrid_search(query)` = 向量 Top-K + layer≥2 过滤。

### 4. 增量写入流程

```
5-4-2 输出 memory_records → batch embed → lancedb.table.add()
旧记录相似度>0.9 → merge 而非 duplicate
```

## 代码实战

```python
# pip install numpy lancedb

import lancedb
import numpy as np

class LanceDBMemoryStore:
    def __init__(self, db_path: str = "./hermes_memory"):
        self.db = lancedb.connect(db_path)
        self._ensure_table()
    
    def _ensure_table(self):
        """创建记忆表（如果不存在）"""
        if "memories" not in self.db.table_names():
            import pyarrow as pa
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("tier", pa.int32()),      # 1-4层
                pa.field("content", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), 1536)),
                pa.field("type", pa.string()),     # preference/decision/lesson
                pa.field("score", pa.float32()),
                pa.field("created_at", pa.string()),
            ])
            self.db.create_table("memories", schema=schema)
    
    def add_memory(self, tier: int, content: str, embedding: list[float], 
                   mem_type: str, score: float):
        """添加一条记忆"""
        import uuid
        self.db["memories"].add([{
            "id": str(uuid.uuid4()),
            "tier": tier, "content": content,
            "embedding": embedding, "type": mem_type,
            "score": score, "created_at": datetime.now().isoformat()
        }])
    
    def hybrid_search(self, query: str, query_embedding: list[float], 
                      tier: int = None, top_k: int = 5) -> list[dict]:
        """混合检索：向量+元数据过滤"""
        table = self.db["memories"]
        
        # 向量检索
        vector_results = table.search(query_embedding).metric("cosine").limit(top_k * 2)
        if tier:
            vector_results = vector_results.where(f"tier = {tier}")
        vector_hits = vector_results.to_list()
        
        # 全文检索（LanceDB 支持的 FTS）
        try:
            fts_results = table.search(query, query_type="fts").limit(top_k).to_list()
        except Exception:
            fts_results = []
        
        # RRF 融合
        return self._rrf_fusion(vector_hits, fts_results, top_k)
    
    def _rrf_fusion(self, list_a, list_b, k: int):
        scores = {}
        for rank, item in enumerate(list_a):
            scores[item["id"]] = scores.get(item["id"], 0) + 1/(60+rank)
        for rank, item in enumerate(list_b):
            scores[item["id"]] = scores.get(item["id"], 0) + 1/(60+rank)
        merged = sorted(scores, key=scores.get, reverse=True)[:k]
        all_items = {i["id"]: i for i in list_a + list_b}
        return [all_items[mid] for mid in merged if mid in all_items]
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

- **Embedding 模型固定**：当前用单一 embedding 模型，不同记忆类型（代码 vs 对话 vs 偏好）可能需要不同的 embedding 策略
- **索引重建成本**：LanceDB 在数据量变大（百万级）后索引重建耗时，需要增量索引策略
- **跨模态记忆**：当前只存文本 embedding，不支持代码片段、图表等结构化内容的向量检索
- **多用户隔离**：单表结构不支持多用户，生产环境需要按 user_id 分区

### 下一步学什么

1. **[5-4-4 用户新任务唤醒记忆](5-4-4_用户新任务唤醒记忆.md)** — Embedding 存好后如何在任务中检索和使用
2. **[2-1-1 Embeddings和向量数据库](../../02_AI应用技术/2-1_RAG理论知识+案例详解+实操/2-1-1_Embeddings和向量数据库.md)** — 向量检索的多种算法和优化
3. **[2-1-4 RAG调优](../../02_AI应用技术/2-1_RAG理论知识+案例详解+实操/2-1-4_RAG调优.md)** — 混合检索和重排序的系统方法论

### 工业界最佳实践

- **Embedding 版本管理**：不同版本的 embedding 模型产生的向量不兼容，需要在元数据中记录 embedding_model_version
- **定期重建索引**：记忆量超过 10 万条后，每月跑一次全量索引重建，保持检索性能
- **冷热数据分离**：近 30 天的记忆放热存储（LanceDB 本地），30 天以上的放冷存储（对象存储），按需加载

---

## 常见问题

### 小白最常踩的 3 个坑

**坑 1：忘了建索引，检索越来越慢**

LanceDB 支持创建索引加速检索。如果不建索引，数据量超过 1 万条后全表扫描会非常慢。`table.create_index()` 是最容易忘记但最重要的一行代码。

**坑 2：Embedding 维度不一致**

换 embedding 模型后维度从 1536 变成 768，旧数据的 1536 维向量和新数据的 768 维向量无法一起检索。解决办法：要么保留旧 embedding 模型做查询，要么全量重建 embedding。

**坑 3：把 LanceDB 当 MySQL 用，做复杂 JOIN 和子查询**

LanceDB 是为向量检索优化的，不是关系数据库。复杂 SQL 查询（JOIN、子查询、GROUP BY）应该在应用层做，LanceDB 只负责向量检索+简单元数据过滤。

### 自检题

**Q1**：LanceDB 相比 FAISS 和 Chroma 的优势是什么？<details><summary>答案</summary>相比 FAISS：原生持久化、混合检索（FAISS仅向量）。相比 Chroma：嵌入部署（无独立服务）、性能更高。LanceDB 是嵌入式的、支持SQL风格过滤的向量数据库。</details>

**Q2**：混合检索如何融合向量检索和全文检索的结果？<details><summary>答案</summary>用 RRF（Reciprocal Rank Fusion）：对每条结果，根据它在两个列表中的排名分别计算分数 1/(60+rank)，最终取总分最高的前K条。60是平滑常数，防止排名靠前的结果过度主导。</details>

**Q3**：为什么需要混合检索而不只用向量检索？<details><summary>答案</summary>向量检索擅长语义相似但可能漏掉精确关键词匹配；全文检索能找到精确词但不懂语义。混合检索取两者之长——用户搜"numpy"能找到所有包含这个词的记忆（全文），同时也能找到"数组计算"相关记忆（语义）。</details>

---

## 延伸阅读

- [LanceDB 官方文档](https://lancedb.github.io/lancedb/) — 完整的 API 参考和最佳实践指南
- [向量数据库选型对比 (知乎)](https://docs.python.org/3/) — 中文社区主流向量数据库的横向对比
- [RRF 融合算法论文](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) — RRF 的理论基础和数学原理
