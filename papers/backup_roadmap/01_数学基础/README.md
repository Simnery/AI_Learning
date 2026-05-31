# 01 数学基础

> **阶段定位**：AI/ML 的底层语言。不需要数学系水平，但要能"读懂"公式和直觉。
> **总时长**：约 2 周
> **策略**：按需补，不贪多——遇到不懂的公式再回头翻这章。

---

## 1.1 线性代数 (Linear Algebra)

**核心目标**：理解向量、矩阵乘法、点积是神经网络的基本运算单元。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| 向量与矩阵 | 什么是向量（1D array）、矩阵（2D array），维度/形状（shape）的含义 | 1 天 |
| 矩阵乘法 | A(m,n) x B(n,k) = C(m,k)，为什么维度必须对齐 | 2 天 |
| 点积 (Dot Product) | 两个向量的相似度度量——**这就是 Attention 的计算核心** | 1 天 |
| 转置与范数 | 矩阵转置的物理意义，L1/L2 范数 | 1 天 |

**BIOS 类比**：
- 矩阵乘法 → PEI/DXE Phase Table 的结构体指针偏移
- 向量相似度 → 两个 BIOS module hash 的对比匹配

**推荐资源**：
- 3Blue1Brown [线性代数本质](https://www.3blue1brown.com/topics/linear-algebra)（视频，可视化极佳）
- Gilbert Strang "Introduction to Linear Algebra" 第 1-3 章（选读）

**动手实践**：用 NumPy 做矩阵乘法，感受 `(64, 768) x (768, 512) = (64, 512)` 的形状变换。这就是 Embedding → Attention 投影的实际操作。

---

## 1.2 微积分 (Calculus)

**核心目标**：理解导数 = 变化率，梯度下降 = 一步步沿着最陡的方向下山。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| 导数 | 函数在某点的变化率，`dy/dx` 的含义 | 1 天 |
| 偏导数 | 多变量函数，对单个变量求导 | 1 天 |
| 梯度下降 | `W = W - lr * d(loss)/dW`，逐次逼近最小值 | 1 天 |

**BIOS 类比**：
- 梯度下降 → 反复调整 Memory Reference Code 参数直到 POST 通过
- 学习率 (lr) → 每次调参数的步长，太大跳过最优值，太小收敛太慢

**推荐资源**：
- 3Blue1Brown [微积分本质](https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr) 第 1-3 集
- StatQuest [Gradient Descent Step-by-Step](https://www.youtube.com/watch?v=sDv4f4s2SB8)

---

## 1.3 概率论 (Probability)

**核心目标**：理解条件概率、Softmax——大模型输出"哪个 token"的本质。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| 条件概率 | P(A|B) = P(A,B) / P(B)，贝叶斯公式 | 1 天 |
| 概率分布 | 离散分布 vs 连续分布，概率密度 | 1 天 |
| Softmax | 把任意实数值向量 → 概率分布（所有值和为 1） | 1 天 |

**BIOS 类比**：
- 条件概率 → "如果 SMBIOS table 有 Type 17，那么它报告的内存频率在 3200-5600 之间的概率是多少？"
- Softmax → POST card 显示错误码时，候选故障原因的概率分布

**推荐资源**：
- StatQuest 概率系列
- Andrej Karpathy 手写 GPT 视频中 Softmax 实现的逐行讲解

---

## 1.4 统计学 (Statistics)

**核心目标**：理解交叉熵（Cross-Entropy）——训练 LLM 时最小化的那个 loss 的本质。

| 子主题 | 你必须搞懂的内容 | 时间 |
|--------|------------------|------|
| 均值与方差 | 描述数据的中心和离散程度 | 0.5 天 |
| 最大似然估计 | 给定数据，最可能的模型参数是什么 | 0.5 天 |
| 交叉熵 (Cross-Entropy) | 两个概率分布之间的"距离"，越大越不像 | 1 天 |

**BIOS 类比**：
- 交叉熵 → 你设置的 DRAM timing 和 JEDEC spec 之间的"偏差"
- 训练 loss 下降 → 反复 tune memory margin 直到抓到的错误越来越少

**推荐资源**：
- StatQuest [Cross Entropy](https://www.youtube.com/watch?v=6ArSys5q48U)

---

## 交叉引用

- 所学数学工具将直接用于 **03_深度学习基础** 中的 Backpropagation 推导
- 交叉熵是 **04_LLM原理** 中 Transformer 训练 loss 的核心
- 矩阵乘法 + Softmax 组合 = **04_LLM原理** 中 Attention 计算的完整实现

**对应知识图谱章节**：`01_AI大模型基础 / 1-1_理论知识` (papers_original 路径)

---

## 学习检查清单

- [ ] 能用 NumPy 完成任意两个矩阵的乘法，且理解维度约束
- [ ] 能口述梯度下降的 3 个核心步骤（算梯度、更新权重、迭代）
- [ ] 能手算一个简单的 Softmax：[2.0, 1.0, 0.1] → 概率分布
- [ ] 能解释为什么 LLM 训练用交叉熵 loss，而不是均方误差（MSE）
- [ ] 看到 `torch.nn.CrossEntropyLoss()` 不再害怕
