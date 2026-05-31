# 03 深度学习基础

> **阶段定位**：从"ML 黑箱"到"理解神经网络内部"。这是通向 LLM 的桥。
> **总时长**：约 3-4 周
> **前置依赖**：01_数学基础 + 02_ML基础（至少跑通过 MNIST MLP）

---

## 3.1 神经网络核心 (Neural Networks)

**核心目标**：理解神经网络的数学本质——一连串的矩阵乘法 + 非线性激活。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| 神经元与层 | 输入层→隐藏层→输出层，权重矩阵 W，偏置 b | 1 天 |
| 激活函数 | Sigmoid、ReLU、GELU 的区别与为什么需要非线性 | 1 天 |
| 多层感知机 (MLP) | 堆叠多层，表达能力随深度增加 | 1 天 |
| Universal Approximation | 足够宽的 MLP 可以拟合任意连续函数 | 选读 |

**BIOS 类比**：
- 神经网络层级 → DXE Dispatcher 层层调度：一个 module 的输出是下一个的输入
- 激活函数 → Chipset GPIO 的高低电平触发，非线性的开关决策
- 权重矩阵 → ACPI table 中的数值表，决定了系统的行为

**动手实践**：用 PyTorch 手写一个 3 层 MLP，逐层 print 每一层的输入/输出 shape。

---

## 3.2 反向传播 (Backpropagation)

**核心目标**：理解梯度的链式传播——这是所有深度学习训练的数学基础。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| 链式法则 | `dz/dx = dz/dy * dy/dx`，误差从输出层逐层回传 | 1 天 |
| 计算图 | PyTorch 的动态计算图，`requires_grad` 的作用 | 1 天 |
| 手算一次 BP | 对一个 2-层网络手动推导梯度更新（纸笔） | 1 天 |

**BIOS 类比**：
- Backpropagation → SMM SMI 的嵌套调用回溯：SMI handler 调用子函数，子函数又调用子函数，错误码一层层传回来
- 链式法则 → BIOS 启动流程的依赖链：PEI→DXE→BDS，每一阶段出错都要追溯到根源

**推荐资源**：
- 3Blue1Brown [深度学习](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi) 第 3-4 集（backprop 可视化）
- Andrej Karpathy [micrograd](https://github.com/karpathy/micrograd)（200 行代码实现自动微分）

---

## 3.3 Embedding

**核心目标**：理解"高维向量表示"——文本、图像、声音都变成数字，这是 LLM 的入口。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| One-hot vs Dense | One-hot 的维度灾难，Dense embedding 的语义压缩 | 0.5 天 |
| Word2Vec | CBOW、Skip-gram，`king - man + woman = queen` | 1 天 |
| Embedding Layer | 本质是一个查找表（Lookup Table），输入 ID 返回向量 | 0.5 天 |
| 语义空间 | 相似词在空间中距离近，方向代表语义关系 | 0.5 天 |

**BIOS 类比**：
- Embedding → UEFI Protocol GUID：一串数字 (128-bit) 代表一个"功能"。两个相似的 protocol（如 `gEfiPciIoProtocolGuid` vs `gEfiPciRootBridgeIoProtocolGuid`）在功能上也相近
- 语义空间 → 所有 BIOS module 按功能聚类的二维平面投影

---

## 3.4 Tokenization

**核心目标**：理解文本如何被切成 LLM 能处理的"最小单元"。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| 为什么需要 Tokenization | 文本→整数序列，否则模型无法处理 | 0.5 天 |
| BPE (Byte Pair Encoding) | 高频词=短 token，低频词=多个 subword token | 1 天 |
| Tokenizer 实战 | 用 HuggingFace tokenizer 编码/解码，观察 token ID | 0.5 天 |
| Token 数量与成本 | 更多 token → 更长的上下文 → 更贵 | 0.5 天 |

**BIOS 类比**：
- Tokenization → 日志解析中的 Token 拆分：`"ERROR: DIMM_A1: Training failed at step 3"` 被拆成 `["ERROR", "DIMM_A1", "Training", "failed", "step", "3"]`
- BPE → UEFI string 拆成 protocol 短 ID（高频）和长 GUID（低频需完整记录）

**动手实践**：
```python
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("gpt2")
print(tok("BIOS POST Code 0x55 = Memory Initialization"))
# 观察每个 token 及其 ID，数清楚 token 数量
```

---

## 3.5 Attention 机制

**核心目标**：这是 LLM 的心脏。必须先理解"普通 Attention"，再上 Transformer。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| 为什么需要 Attention | RNN 瓶颈：长序列信息丢失 | 0.5 天 |
| QKV 框架 | Query = 我想找什么，Key = 我有什么，Value = 实际内容 | 2 天 |
| Scaled Dot-Product | `softmax(QK^T / sqrt(d_k)) * V` —— 逐行理解公式 | 1 天 |
| 多头注意力 (Multi-Head) | 多个 QKV 组并行，每个"头"关注不同方面 | 1 天 |

**BIOS 类比**：
- QKV → HOB (Hand-Off Block) 的 Producer-Consumer 机制：PEI 产生 HOB (K/V)，DXE 需要某类 HOB (Q)，通过 GUID 匹配获取
- 多头注意力 → 看一份 BIOS spec 时，同时关注"内存初始化"、"PCI 枚举"、"ACPI 表"三个维度
- Softmax 归一化 → 把多个 code review 意见聚合成一个最终决策

**推荐资源**：
- [Annotated Transformer](http://nlp.seas.harvard.edu/2018/04/03/attention.html)（逐行代码讲解，这一篇读透就够了）
- Jay Alammar [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)（图解，直观）

---

## 交叉引用

- Backpropagation 的链式法则 → **01_数学基础** 导数章节
- Embedding 的矩阵乘法 → **01_数学基础** 线性代数章节
- Attention 的 QKV → **04_LLM原理** 中 Transformer 架构的核心组件
- Tokenization → **05_应用开发** 中 RAG 的 Chunking 策略直接依赖

**对应知识图谱章节**：
- `01_AI大模型基础 / 1-2_实操基础`（大模型基本原理与 API）
- `03_AI框架及工具平台 / 3-4_神经网络基础与TensorFlow实战`

---

## 学习检查清单

- [ ] 能画出 3 层 MLP 的前向传播计算图（带维度标注）
- [ ] 能手算一个简单 2 层网络的 Backpropagation（纸笔推导梯度）
- [ ] 能解释 Embedding Layer 的本质是一个查表操作
- [ ] 用 HuggingFace tokenizer 编码一段英文/中文，理解 token 切分规则
- [ ] 能默写 Attention 公式: `softmax(QK^T / sqrt(d_k)) * V`
- [ ] 能解释多头注意力的"多头"分别代表什么
- [ ] 跑通 Karpathy 的 [micrograd](https://github.com/karpathy/micrograd) 并理解自动微分
