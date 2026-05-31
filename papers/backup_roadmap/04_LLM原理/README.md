# 04 LLM 原理

> **阶段定位**：吃透 Transformer 架构。这是整个学习路线的核心——前 3 章铺路，就为理解这一章。
> **总时长**：约 4-6 周
> **前置依赖**：01 数学基础 + 03 深度学习基础（Attention 必须已理解）

---

## 4.1 Transformer 架构全景

**核心目标**：建立 Transformer 的完整心智模型——每个组件是什么、为什么、放在哪。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| 架构概览 | Encoder-Decoder 结构，GPT 只用 Decoder，BERT 只用 Encoder | 1 天 |
| Input Embedding | Token ID → 稠密向量，维度 d_model (如 768/4096) | 0.5 天 |
| Positional Encoding | 为什么"只加信息不够"——`I eat` vs `eat I` 语义不同 | 1 天 |
| 组件数据流 | Input → Embedding + Pos → N x (Attention + FFN) → Output | 1 天 |

**核心直觉**：Transformer 就是一堆矩阵乘法的堆叠，没有魔法，只有工程。

**推荐资源**：
- Andrej Karpathy [Let's build GPT from scratch](https://www.youtube.com/watch?v=kCc8FmEb1nY)（**必看**，跟着写一遍代码）
- Jay Alammar [The Illustrated GPT-2](http://jalammar.github.io/illustrated-gpt2/)

---

## 4.2 Self-Attention 深度剖析

**核心目标**：把 Q/K/V 的物理含义彻底搞透。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| Q 的生成 | 当前 token 通过 W_Q 投影 → "我要找什么" | 1 天 |
| K 的生成 | 所有 token 通过 W_K 投影 → "我能提供什么" | 0.5 天 |
| V 的生成 | 所有 token 通过 W_V 投影 → "我的实际内容" | 0.5 天 |
| Attention 计算 | Q 和所有 K 做点积 → Softmax → 加权求和 V | 1 天 |
| Multi-Head | 8/16/32 个头，拼接后线性投影，每个头关注不同模式 | 1 天 |
| Causal Mask | GPT 只能看到过去，不能"偷看"未来 | 0.5 天 |

**BIOS 类比回顾**：
- Q/K/V → HOB 的 Producer-Consumer：`Q = "给我内存信息"`, `K = GUID 匹配"我是内存 HOB"`, `V = 实际内存数据`
- Causal Mask → 代码写了一半，不能引用还没写的函数

---

## 4.3 Feed Forward Network (FFN)

**核心目标**：理解 FFN 是 GPT 的"知识存储器"。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| FFN 结构 | 两层 MLP + 激活：`W2 * GELU(W1 * x + b1) + b2` | 0.5 天 |
| 扩展比 | 中间层通常是输入层的 4x (如 768→3072→768) | 0.5 天 |
| 知识存储假说 | Attention 负责"检索"，FFN 负责"记忆"（事实性知识存在 FFN 权重里） | 1 天 |

**BIOS 类比**：
- FFN → BIOS ROM 中的静态配置数据（ACPI table、SMBIOS strings）
- Attention → 运行时的模块查找和调用
- 两者配合 → 查找表 (Attention) + 查到的数据 (FFN)

**推荐阅读**：
- [Transformer Feed-Forward Layers Are Key-Value Memories](https://arxiv.org/abs/2012.14913)（FFN 即 KV 存储的论文）

---

## 4.4 GPT vs BERT

**核心目标**：理解 Decoder-only 和 Encoder-only 的根本差异，以及各自的适用场景。

| 对比维度 | GPT (Decoder-only) | BERT (Encoder-only) |
|----------|-------------------|---------------------|
| 注意力方式 | Causal（单向，只看左边） | Bidirectional（双向，看全部） |
| 训练目标 | 预测下一个 token | 填空 (MLM) + 判断两句是否连贯 (NSP) |
| 擅长 | 文本生成、对话 | 文本理解、分类、NER |
| Head 数 | 通常 12-96 | 通常 12-24 |
| 典型应用 | 你正在用的 Claude 就是这个 | 情感分析、搜索排序 |

**BIOS 类比**：
- GPT → 写 BIOS code（一行行写，后面的代码不能依赖还没写的内容）
- BERT → 读 BIOS spec（可以前后翻页，完整理解一个章节）

---

## 4.5 LoRA (Low-Rank Adaptation)

**核心目标**：理解微调不用改全量参数——只训一个小矩阵就够。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| 为什么不 Full Fine-tune | 175B 参数全量训练 = 烧钱 + 灾难性遗忘 | 0.5 天 |
| LoRA 原理 | `W' = W + B*A`，只训练 B 和 A（低秩矩阵），冻结原始 W | 1 天 |
| 秩 (Rank) | rank=8/16/64，越小越省，但表达能力越低 | 0.5 天 |
| QLoRA | 更进一步：原始模型 4-bit 量化 + LoRA adapter | 0.5 天 |

**BIOS 类比**：
- LoRA → 只打一个 Override patch（不改原始 ROM，加一个小 patch）
- W' = W + B*A → 原始 DXE driver (W) + 你的 ODM customization patch (B*A)
- 秩的选择 → ODM customization 需要改多少东西？改得多就 rank 高一点

**动手实践**：
```python
from peft import LoraConfig, get_peft_model
# 只训练 adapter，原始模型冻结
lora_config = LoraConfig(r=8, lora_alpha=32, target_modules=["q_proj", "v_proj"])
model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()  # 看看只有百分之几的参数可训练
```

---

## 交叉引用

- Attention QKV 计算 → **03_深度学习基础** Attention 章节
- FFN 结构 → **03_深度学习基础** MLP 章节 + **01_数学基础** 矩阵乘法
- LoRA 的矩阵分解 → **01_数学基础** 低秩矩阵
- Tokenization → **03_深度学习基础** Tokenization → **05_应用开发** RAG Chunking

**对应知识图谱章节**：
- `01_AI大模型基础 / 1-2_实操基础`（大模型基本原理）
- `02_AI应用技术 / 2-3_模型训练与微调`（LLM 微调原理、数据工程、LoRA 实操）

---

## 推荐资源

| 资源 | 说明 | 优先级 |
|------|------|--------|
| [Karpathy nanoGPT](https://www.youtube.com/watch?v=kCc8FmEb1nY) | 2 小时从零写 GPT | ★★★ 必看 |
| [Karpathy makemore 系列](https://www.youtube.com/playlist?list=PLAqhIrjkxrVzFWr7G9gCu9RJMh0Cd_gIx) | 从 bigram 到 Transformer | ★★★ |
| [Annotated Transformer](http://nlp.seas.harvard.edu/2018/04/03/attention.html) | 逐行代码讲解 | ★★☆ |
| [HuggingFace NLP Course](https://huggingface.co/learn/nlp-course) | tokenizer 到 fine-tune 完整实战 | ★★☆ |
| [Lil'Log Transformer 系列](https://lilianweng.github.io/) | 工业级深入解读 | ★☆☆ 进阶 |

---

## 学习检查清单

- [ ] 能画出 Transformer Decoder 一个 Block 的完整结构
- [ ] 能手写 `softmax(QK^T / sqrt(d_k)) * V` 并解释每一步的物理含义
- [ ] 能说出 GPT (Decoder-only) 和 BERT (Encoder-only) 的至少 3 个关键区别
- [ ] 跟着 Karpathy 视频手写了 nanoGPT（或至少理解了核心代码）
- [ ] 理解了 LoRA 的数学原理：`W' = W + B*A`
- [ ] 能用 PEFT 库加载一个模型 + LoRA adapter，看到 trainable params 数量
- [ ] 读完了 [Annotated Transformer](http://nlp.seas.harvard.edu/2018/04/03/attention.html)（必做）
