# 2.1.1 Embeddings和向量数据库

> 2.1 RAG理论知识+案例详解+实操 > 2. AI应用技术

---

## 核心概念

### 什么是 Embedding

**一句话**：Embedding 是把文字/图片/音频"翻译"成数字向量的技术——让计算机能"理解"语义。

打个比方：你有一堆书，但你不可能让计算机直接"读"书。Embedding 就像是给每本书贴上 GPS 坐标——主题相近的书坐标接近，主题无关的书坐标很远。计算机不懂书的内容，但能通过坐标距离判断"这两本书讲的是不是一回事"。

| 输入 | Embedding 后 | 含义 |
|------|-------------|------|
| "猫" | [0.23, 0.87, -0.41, ...] | 一个 768 维向量 |
| "狗" | [0.25, 0.83, -0.39, ...] | 和"猫"很接近 |
| "汽车" | [-0.71, 0.12, 0.65, ...] | 和"猫"距离很远 |

**为什么重要**：LLM 本身有长度限制（context window）。Embedding + 向量检索 可以让 LLM "记住"无限多的外部知识——这就是 RAG 的核心基础。

### 前置知识

- 线性代数基础：向量的概念、点积运算
- 对 LLM 的基本了解（Token、上下文窗口）
- 后续关联节点：[2.1.2 RAG技术与应用](2-1-2_RAG技术与应用.md)

---

## 原理讲解

### Word Embedding：从 One-Hot 到语义向量

**传统方式 One-Hot 编码**的问题：

```
词汇表: [猫, 狗, 苹果, 汽车]
"猫" → [1, 0, 0, 0]
"狗" → [0, 1, 0, 0]
# 问题: 所有词距离都一样，无法表达"猫和狗是相似的"
```

**Word2Vec（2013, Google）** 的革命性思想：

> 一个词的含义，由它周围的词决定。

```
句子: "我家的___很可爱，它会喵喵叫"
填空处大概率是"猫"——用上下文预测目标词，模型自动学会了语义。

训练结果：猫和狗的向量很接近，猫和汽车的向量很远。
```

**关键洞察**：Embedding 模型不是人为定义规则，而是从海量文本中"自动学习"语义关系。

### 余弦相似度：衡量语义距离的标尺

两个向量的相似度用**余弦相似度**衡量：

```
余弦相似度 = (A · B) / (|A| × |B|)

结果范围: [-1, 1]
  1: 方向完全一致（语义相同）
  0: 正交（无关）
 -1: 方向完全相反（语义相反）
```

**为什么不直接用欧几里得距离**？因为向量的"长度"可能受文本长度影响，余弦只看"方向"不看"大小"，更适合语义比较。

```python
import numpy as np

def cosine_similarity(a, b):
    """余弦相似度计算"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

cat = np.array([0.23, 0.87, -0.41])
dog = np.array([0.25, 0.83, -0.39])
car = np.array([-0.71, 0.12, 0.65])

print(f"猫 vs 狗: {cosine_similarity(cat, dog):.4f}")    # ≈ 0.98
print(f"猫 vs 汽车: {cosine_similarity(cat, car):.4f}")  # ≈ -0.15
```

### MTEB 榜单：Embedding 模型的"奥运会"

[MTEB](https://huggingface.co/spaces/mteb/leaderboard)（Massive Text Embedding Benchmark）是衡量 Embedding 模型好坏的权威榜单，包含 8 大类任务：

| 任务类型 | 衡量什么 | 典型场景 |
|---------|---------|---------|
| **Classification** | 文本分类能力 | 情感分析、主题分类 |
| **Clustering** | 聚类效果 | 新闻聚合、用户分群 |
| **Pair Classification** | 语义相似判断 | 重复检测、释义识别 |
| **Reranking** | 重排序精度 | 搜索结果优化 |
| **Retrieval** | 检索召回率 | **RAG 最看重的指标** |
| **STS** | 语义相似度（数值） | 句子对打分 |
| **Summarization** | 摘要质量评估 | 文本摘要 |
| **Bitext Mining** | 跨语言对齐 | 翻译对齐 |

**如何看 MTEB 榜单**：
1. 先看 `Retrieval` 得分——这是 RAG 场景最重要的指标
2. 关注模型大小（Small/Large）和向量维度（维度越高通常越强但越慢）
3. 中文场景优先看支持中文的模型（BGE、M3E、text2vec 等）

### 向量维度：越高不一定越好

| 维度 | 优势 | 劣势 |
|------|------|------|
| 低维（256-384） | 存储小、检索快 | 语义表达能力有限 |
| 中维（768-1024） | **性价比最优**，大部分场景够用 | — |
| 高维（1536-4096） | 精度最高 | 存储大、检索慢、成本高 |

**实用建议**：一般 RAG 场景用 768 维（如 BGE-Large、OpenAI text-embedding-3-small）即可，追求极致精度再上高维。

### 神奇的"俄罗斯套娃"（Matryoshka Embeddings）

OpenAI 的 `text-embedding-3` 系列支持 Matryoshka 表示：

> 一个 3072 维向量，可以直接截断到 256 维使用，无需重新训练！

```python
# Matryoshka 的核心思想
embedding_3072 = model.embed(text)  # 3072 维
embedding_256  = embedding_3072[:256]  # 直接截断，仍保持语义
# 用 256 维做检索，精度仅下降 ~2%，存储和速度提升 10 倍+
```

原理：训练时使用了特殊的损失函数，让模型学会"最重要的语义信息排在前面的维度"。就像俄罗斯套娃——外面最大的包含全部信息，里面最小的包含核心信息。

### 向量数据库：语义搜索引擎

**传统数据库**：
```
SELECT * FROM books WHERE title LIKE '%猫%'
# → 只能精确/模糊匹配文字，找不到"小猫咪饲养指南"
```

**向量数据库**：
```
search(query="猫科动物", top_k=10)
# → 返回语义相近的结果："猫粮推荐"、"猫咪疾病"、"布偶猫品种"...
#    即使标题里没有"猫科动物"这四个字也能找到
```

**向量数据库与传统数据库区别**：

| 维度 | 传统数据库（MySQL/PG） | 向量数据库（Milvus/FAISS） |
|------|----------------------|---------------------------|
| 查询方式 | 精确匹配、范围查询 | 近似最近邻（ANN） |
| 核心操作 | WHERE、JOIN、GROUP BY | 向量相似度搜索 |
| 数据格式 | 结构化（数字、字符串） | 非结构化 → 向量化 |
| 精确度 | 100% 精确 | 近似（可调精度/速度平衡） |
| 典型场景 | 订单查询、用户管理 | 语义搜索、推荐、去重 |

**主流向量数据库对比**：

| 数据库 | 定位 | 部署 | 适用规模 | 特点 |
|--------|------|------|:--------:|------|
| **FAISS** | 向量检索库 | 本地/内嵌 | 百万-十亿 | Meta 出品，纯向量检索，GPU 加速，无持久化 |
| **Milvus** | 分布式向量DB | 独立部署 | 十亿+ | 云原生，支持混合查询，国产开源 |
| **Pinecone** | 云托管向量DB | SaaS | 十亿+ | 免运维，Serverless，海外为主 |
| **Elasticsearch** | 全文搜索+向量 | 独立部署 | 千万-亿 | 8.0+ 支持向量，适合已有 ES 场景 |
| **Chroma** | 轻量向量DB | 本地/内嵌 | 百万 | 类 SQLite 体验，适合原型开发 |
| **Qdrant** | 高性能向量DB | 本地/云 | 百万-十亿 | Rust 编写，性能优异，过滤功能强 |

---

## 代码实战

### 环境准备

```bash
pip install sentence-transformers faiss-cpu numpy
# GPU 版: pip install faiss-gpu
```

### 实战 1：用 Embedding 模型做语义搜索（纯 Python，无需外部服务）

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# 1. 加载模型（自动下载，国内可加镜像 HF_ENDPOINT=https://hf-mirror.com）
MODEL = "BAAI/bge-small-zh-v1.5"  # BGE 中文小模型，384维，轻量好用
model = SentenceTransformer(MODEL)

# 2. 准备知识库
documents = [
    "Python 是一种解释型编程语言，语法简洁",
    "大语言模型通过 Transformer 架构实现上下文理解",
    "向量数据库用于存储和检索高维 Embedding 向量",
    "FAISS 是 Meta 开源的高效向量检索库",
    "余弦相似度是衡量两个向量方向一致性的指标",
]

# 3. 将文档转为向量（Embedding）
doc_embeddings = model.encode(documents, normalize_embeddings=True)
print(f"文档向量形状: {doc_embeddings.shape}")  # (5, 384)

# 4. 查询
query = "向量检索和语义搜索"
query_embedding = model.encode(query, normalize_embeddings=True)

# 5. 计算余弦相似度（已归一化，可直接点积）
similarities = np.dot(doc_embeddings, query_embedding)

# 6. 排序输出
for idx in np.argsort(similarities)[::-1]:
    print(f"[{similarities[idx]:.4f}] {documents[idx]}")

# 预期输出:
# [0.85] 向量数据库用于存储和检索高维 Embedding 向量
# [0.78] FAISS 是 Meta 开源的高效向量检索库
# [0.65] 余弦相似度是衡量两个向量方向一致性的指标
# [0.15] 大语言模型通过 Transformer 架构实现上下文理解
# [0.08] Python 是一种解释型编程语言，语法简洁
```

### 实战 2：FAISS 构建向量索引

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

# 模拟数据
documents = [
    "如何训练一个图像分类模型",
    "Transformer 注意力机制详解",
    "向量数据库 Milvus 部署教程",
    "Python 爬虫入门指南",
    "RAG 检索增强生成原理",
    "CNN 卷积神经网络基础",
    "LangChain 框架使用手册",
]

doc_embeddings = model.encode(documents, normalize_embeddings=True)
dim = doc_embeddings.shape[1]  # 384

# --- FAISS 索引操作 ---

# 方案A: Flat 索引（精确搜索，暴力计算，适合 < 10万 数据）
index = faiss.IndexFlatIP(dim)  # IP = Inner Product（内积 = 归一化后的余弦相似度）
index.add(doc_embeddings.astype('float32'))
print(f"Flat 索引中向量数: {index.ntotal}")

# 方案B: IVF 索引（倒排索引，速度与精度的平衡，适合百万级）
nlist = 4  # 聚类中心数（建议: sqrt(数据量)）
quantizer = faiss.IndexFlatIP(dim)
index_ivf = faiss.IndexIVFFlat(quantizer, dim, nlist)
index_ivf.train(doc_embeddings.astype('float32'))  # IVF 需要训练
index_ivf.add(doc_embeddings.astype('float32'))
# 检索时 nprobe 控制搜索范围（越大精度越高但越慢）
index_ivf.nprobe = 2

# --- 检索 ---
query = "如何做信息检索和搜索"
q_emb = model.encode([query], normalize_embeddings=True).astype('float32')

k = 3
distances, indices = index.search(q_emb, k)  # Flat 检索
print(f"\n查询: {query}")
print("=" * 50)
for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
    print(f"Top{i+1} [相似度={dist:.4f}] {documents[idx]}")

# 预期输出:
# Top1 [相似度=0.82xx] RAG 检索增强生成原理
# Top2 [相似度=0.76xx] 向量数据库 Milvus 部署教程
# Top3 [相似度=0.35xx] LangChain 框架使用手册
```

### 实战 3：不同 Embedding 模型效果对比

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# 测试句子对
pairs = [
    ("我喜欢吃苹果", "苹果是一种水果"),           # 语义相关
    ("我喜欢吃苹果", "苹果公司发布了新iPhone"),    # 字面相同，语义不同
    ("猫是一种宠物", "狗是人类的朋友"),           # 同类，相似
    ("猫是一种宠物", "深度学习改变了AI领域"),      # 无关
]

# 可选模型列表
models_to_test = [
    "BAAI/bge-small-zh-v1.5",       # BGE 中文小模型
    "shibing624/text2vec-base-chinese",  # text2vec 中文
    "moka-ai/m3e-base",             # M3E 中文
]

for model_name in models_to_test:
    model = SentenceTransformer(model_name)
    print(f"\n{'='*50}")
    print(f"模型: {model_name}")
    for t1, t2 in pairs:
        emb = model.encode([t1, t2], normalize_embeddings=True)
        sim = np.dot(emb[0], emb[1])
        print(f"  [{sim:.4f}] {t1} ⇄ {t2}")

# 观察要点：
# 1. 第1、2对：模型能否区分"水果苹果"和"公司苹果"（需要好的语义理解）
# 2. 第3对：同类句子相似度应该高
# 3. 第4对：无关句子相似度应该低
```

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

### Embedding 模型的趋势

1. **多语言模型**：一份模型同时支持中英日韩，如 `BGE-M3`
2. **多模态 Embedding**：文字+图片联合向量化，如 CLIP 系列
3. **Matryoshka 表示**：一次生成，多维度使用，存储成本大幅降低
4. **LLM 即 Embedder**：直接用 GPT/Claude 的 hidden states 做 Embedding（成本高但效果好）

### 向量数据库选型决策树

```
数据量 < 100万 且 不需要持久化？
  └─ Yes → FAISS（最简方案）

数据量 100万-1亿 且 需要生产级稳定性？
  └─ Yes → Milvus / Qdrant

已有 Elasticsearch 集群？
  └─ Yes → ES 8.x 向量插件（复用已有基础设施）

不想管运维？
  └─ Yes → Pinecone / Zilliz Cloud（Milvus 云）

快速原型验证？
  └─ Yes → Chroma / LanceDB（嵌入模式）
```

### 后续学习路径

- [2.1.2 RAG技术与应用](2-1-2_RAG技术与应用.md) — Embedding 的"上层应用"，学习完整 RAG 流程
- [2.1.4 RAG调优](2-1-4_RAG调优.md) — 检索效果的精细化调优
- [3.5.1 PyTorch核心概念](../../03_AI框架及工具平台/3-5_PyTorch与视觉检测/3-5-1_PyTorch核心概念.md) — 深入理解 Embedding 模型训练

---

## 常见问题

### 小白最常踩的 3 个坑

1. **忘记归一化**
   - 错误：直接用 `faiss.IndexFlatL2` 而不归一化，余弦相似度和 L2 距离混用
   - 正确：先 `normalize_embeddings=True` 或手动 L2 归一化，再用内积 `IndexFlatIP`

2. **用错了模型维度**
   - 错误：换了 Embedding 模型但没重建 FAISS 索引，维度不匹配
   - 正确：每次换模型后重新 `build_index()`，在初始化时记录 `dim` 常量

3. **把向量数据库当关系数据库用**
   - 错误：试图用向量数据库存储所有业务数据，频繁更新删除
   - 正确：向量数据库只存向量+ID，原始数据存传统数据库；ID 做关联

### 自检题

**Q1**：为什么余弦相似度比欧几里得距离更适合衡量语义相似度？

> **答案**：因为向量的长度可能受文本长度影响（长文本生成的 Embedding 模长可能更大），但余弦只看方向不看大小。比如"猫"和"猫猫猫猫"（重复 4 遍）意思相同，余弦相似度仍然很高，但欧几里得距离会很大。

**Q2**：FAISS 的 `IndexFlatIP` 和 `IndexFlatL2` 有什么本质区别？RAG 应用该用哪个？

> **答案**：IP 做内积（等价于归一化后的余弦相似度），L2 做欧几里得距离。RAG 场景通常用内积 `IndexFlatIP`，但前提是 Embedding 已经 L2 归一化。归一化后 IP 和余弦完全等价。

**Q3**：向量维度从 1024 降到 256，效果会差很多吗？

> **答案**：如果用 Matryoshka Embedding（如 text-embedding-3-large），从 3072 截到 256 精度仅下降 ~2%。如果简单用 PCA 降维非 Matryoshka 模型，精度下降会更显著（5-15%）。因此如果要降维，优先选择原生支持 Matryoshka 的模型。

---

## 延伸阅读

### 中文资料（推荐，无需科学上网）

- [BGE 中文 Embedding 模型](https://huggingface.co/BAAI/bge-small-zh-v1.5) — 智源研究院出品，中文语义检索首选
- [MTEB 排行榜](https://huggingface.co/spaces/mteb/leaderboard) — HuggingFace 上实时更新的 Embedding 模型评测榜单
- [Milvus 官方文档](https://milvus.io/docs/zh) — 向量数据库 Milvus 的中文文档
- [FAISS 入门教程 - CSDN](https://so.csdn.net/so/search?q=FAISS%20%E5%85%A5%E9%97%A8) — 国内外 FAISS 教程汇总，适合快速上手

### 英文资料（可能需科学上网）

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings) — OpenAI 官方 Embedding 文档，含 Matryoshka 用法
- [FAISS Wiki (GitHub)](https://github.com/facebookresearch/faiss/wiki) — FAISS 官方 Wiki，索引选型指南
- [Sentence-Transformers 文档](https://www.sbert.net/) — 最流行的 Embedding 框架，支持 5000+ 预训练模型
