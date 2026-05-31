# 3.4 神经网络基础与TensorFlow实战

> 3.4 神经网络基础与TensorFlow > 3. AI框架及工具平台

## 核心概念

- **是什么**：神经网络是深度学习的基石——模仿人脑神经元连接的计算模型，通过多层非线性变换从数据中自动学习规律。TensorFlow 是 Google 开源的深度学习框架，Keras 是它的高层 API，让你用几行代码就能搭建和训练神经网络。
- **为什么重要**：不管你后面学 CNN、RNN、Transformer，底层都是神经网络的基本构件（前向传播、损失函数、梯度下降、反向传播）。不理解这些基础，调参就是玄学。
- **前置知识**：高中数学（导数、矩阵乘法），Python 基础。

### 神经网络核心组件

| 组件 | 作用 | 大白话 |
|------|------|--------|
| **神经元** | 接收输入，加权求和，激活输出 | 一个简单的"是/否"决策单元 |
| **层（Layer）** | 多个神经元组成 | 一层提取一个级别的特征 |
| **激活函数** | 引入非线性 | 没有它，多层网络 = 一层网络 |
| **损失函数** | 衡量预测和真实的差距 | 告诉模型"你错得有多离谱" |
| **优化器** | 根据损失调整权重 | "往哪走能减小错误"的指南针 |
| **反向传播** | 从输出层往回传梯度 | 把错误责任分配到每个参数 |

## 原理讲解

### 1. 一个神经元是怎么工作的

```
输入    权重     加权和     激活       输出
x₁ ──→ w₁ ──┐
              ├──→ z = Σwᵢxᵢ + b ──→ σ(z) ──→ y
x₂ ──→ w₂ ──┘
              b (偏置)
```

数学表达：`y = σ(w₁x₁ + w₂x₂ + b)`，其中 σ 是激活函数（如 ReLU、Sigmoid）。

### 2. 激活函数——为什么必须要非线性

如果没有激活函数（或将就用线性函数），多层网络等价于单层：

```
Layer2(Layer1(x)) = W₂(W₁x) = (W₂W₁)x = W_new · x  ← 还是线性！
```

常用激活函数：

| 函数 | 公式 | 特点 | 使用场景 |
|------|------|------|---------|
| ReLU | max(0, x) | 简单高效，缓解梯度消失 | 隐藏层首选 |
| Sigmoid | 1/(1+e⁻ˣ) | 输出 (0,1)，两头梯度接近 0 | 二分类输出层 |
| Tanh | (eˣ-e⁻ˣ)/(eˣ+e⁻ˣ) | 输出 (-1,1)，零中心 | RNN 中常用 |
| GELU | x·Φ(x) | 平滑版 ReLU | Transformer 标配 |

### 3. 训练 = 不断重复这三步

```
┌──────────────────────────────────────┐
│             训练循环                  │
│                                      │
│  前向传播 → 计算损失 → 反向传播       │
│      ↑                      ↓        │
│      └──── 更新参数 ←───────┘        │
└──────────────────────────────────────┘
```

- **前向传播**：输入 → 网络 → 预测值
- **计算损失**：预测值 vs 真实值 → 一个数（loss）
- **反向传播**：从 loss 出发，用链式法则逐层算梯度 ∂loss/∂w
- **更新参数**：w_new = w_old - learning_rate × 梯度

### 4. 优化器对比

| 优化器 | 核心改进 | 适用 |
|--------|---------|------|
| SGD | 基础版，每次用一部分数据算梯度 | 基准线 |
| SGD + Momentum | 加惯性，跳过局部最优点 | 比纯 SGD 快 |
| Adam | 自适应学习率 + 动量 | **默认首选** |
| AdamW | Adam + 权重衰减解耦 | Transformer 微调标配 |

## 代码实战

> 依赖安装：`pip install numpy tensorflow scikit-learn pandas matplotlib`

### 示例1：NumPy 从零手写神经网络

```python
import numpy as np

# ---- 生成模拟数据 ----
np.random.seed(42)
X = np.random.randn(200, 3)  # 200 个样本，3 个特征
y = (X[:, 0] + 2 * X[:, 1] - X[:, 2] > 0).astype(float).reshape(-1, 1)

# ---- 网络参数 ----
input_size, hidden_size, output_size = 3, 4, 1

W1 = np.random.randn(input_size, hidden_size) * 0.01
b1 = np.zeros((1, hidden_size))
W2 = np.random.randn(hidden_size, output_size) * 0.01
b2 = np.zeros((1, output_size))

def relu(x): return np.maximum(0, x)
def relu_deriv(x): return (x > 0).astype(float)
def sigmoid(x): return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
def bce_loss(y_pred, y_true):
    return -np.mean(y_true * np.log(y_pred + 1e-8) + (1-y_true) * np.log(1-y_pred + 1e-8))

# ---- 训练 ----
lr = 0.1
for epoch in range(2000):
    # 前向传播
    z1 = X @ W1 + b1
    a1 = relu(z1)
    z2 = a1 @ W2 + b2
    a2 = sigmoid(z2)
    
    loss = bce_loss(a2, y)
    
    # 反向传播
    dz2 = (a2 - y) / len(y)                   # loss 对输出层的梯度
    dW2 = a1.T @ dz2
    db2 = np.sum(dz2, axis=0, keepdims=True)
    
    da1 = dz2 @ W2.T
    dz1 = da1 * relu_deriv(z1)                 # ReLU 导数
    dW1 = X.T @ dz1
    db1 = np.sum(dz1, axis=0, keepdims=True)
    
    # 更新参数
    W1 -= lr * dW1; b1 -= lr * db1
    W2 -= lr * dW2; b2 -= lr * db2
    
    if epoch % 500 == 0:
        acc = ((a2 > 0.5) == y).mean()
        print(f"Epoch {epoch:4d} | Loss: {loss:.4f} | Acc: {acc:.3f}")

# 预期输出: Loss 从 0.69 降到 <0.1，Acc > 95%
```

### 示例2：Keras 快速搭建神经网络

```python
import tensorflow as tf
from sklearn.model_selection import train_test_split
import numpy as np

# 生成模拟回归数据
np.random.seed(42)
X = np.random.randn(1000, 8)
y = X[:, 0] * 2.5 + X[:, 1] * (-1.2) + X[:, 2] * 0.8 + np.random.randn(1000) * 0.1

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Keras Sequential 模型——层叠积木
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(8,)),
    tf.keras.layers.Dropout(0.2),           # 防过拟合
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1)                # 回归输出，无激活函数
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='mse',
    metrics=['mae']
)

history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=50,
    batch_size=32,
    verbose=0
)

loss, mae = model.evaluate(X_test, y_test, verbose=0)
print(f"测试集 MSE: {loss:.4f}, MAE: {mae:.4f}")
# 预期 MAE < 0.3
```

### 示例3：Keras 二手车价格预测实战

```python
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 模拟二手车数据
np.random.seed(42)
n = 2000
data = pd.DataFrame({
    'year': np.random.randint(2005, 2024, n),
    'mileage': np.random.randint(5000, 200000, n),
    'brand_encoded': np.random.randint(0, 10, n),
    'engine_size': np.random.choice([1.5, 2.0, 2.5, 3.0], n),
    'condition': np.random.choice([1, 2, 3, 4, 5], n, p=[0.05, 0.1, 0.3, 0.35, 0.2]),
})
# 模拟价格公式：越新越贵，里程越高越便宜
data['price'] = (
    (data['year'] - 2005) * 800
    - data['mileage'] * 0.05
    + data['engine_size'] * 5000
    + data['condition'] * 3000
    + np.random.randn(n) * 5000
)

# 预处理
features = ['year', 'mileage', 'brand_encoded', 'engine_size', 'condition']
X = data[features].values
y = data['price'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

# 构建模型
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(5,)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(
    optimizer=tf.keras.optimizers.AdamW(learning_rate=0.001),
    loss='mse',
    metrics=['mae']
)

# 早停——验证集 loss 不再下降就停止
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss', patience=10, restore_best_weights=True
)

history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=100,
    batch_size=32,
    callbacks=[early_stop],
    verbose=1
)

# 预测几条看看
preds = model.predict(X_test[:5], verbose=0)
for i in range(5):
    print(f"预测: ¥{preds[i][0]:.0f} | 真实: ¥{y_test[i]:.0f} | 误差: {abs(preds[i][0]-y_test[i]):.0f}")
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

- Keras 封装太好，对底层训练逻辑的理解可能不够深入。需要时用 `tf.GradientTape` 写自定义训练循环
- TensorFlow 在 NLP 领域逐渐被 PyTorch 超越，学术界和 LLM 社区更倾向 PyTorch
- 但 TensorFlow Serving 在生产部署上仍有一席之地（与 K8s 集成好，性能稳定）

### 2. 下一步学习

| 主题 | 说明 | 相关节点 |
|------|------|----------|
| PyTorch 对比学习 | 学术界/LLM 社区主流框架 | [3-5 PyTorch与视觉检测](3-5_PyTorch与视觉检测/README.md) |
| CNN/RNN/Transformer | 经典深度学习架构 | [1-1-1 提示工程→RAG](../01_AI大模型基础/1-1_理论知识/1-1-1_从提示工程到RAG构建大模型的知识与交互.md) |
| TensorFlow Serving | 生产环境模型部署 | [1-3-1 企业级AI部署](../01_AI大模型基础/1-3_模型部署及高并发_——_理论知识+案例详解+实操/1-3-1_企业级AI部署从硬件选型到框架选择.md) |

### 3. 工业界最佳实践

- **入门用 Keras**：代码少、易调试，适合快速验证想法
- **进阶用 PyTorch**：灵活性强，LLM 和大模型社区的标准
- **生产部署**：TensorFlow Serving + Docker + K8s 是成熟方案
- **BatchNormalization + Dropout**：标配防止过拟合组合

## 常见问题

### 小白最常踩的坑

1. **不归一化数据**：特征数值范围差异大（如年份 2005-2024，里程 5000-200000），不归一化会导致梯度不稳定。务必用 `StandardScaler` 或 `MinMaxScaler`
2. **学习率设太大/太小**：太大 loss 不收敛（NaN），太小训练不动。可以先用 0.001（Adam 默认）试，不行再调
3. **过拟合不处理**：训练集 loss 很低但验证集 loss 很高。加 Dropout、BatchNormalization、EarlyStopping 三件套

### 自检题

**Q1**：为什么神经网络需要激活函数？如果所有激活函数都是线性的会怎样？

<details><summary>答案</summary>

激活函数引入非线性，使神经网络能学习复杂模式。如果所有激活函数都是线性的，多层网络等价于单层线性变换，失去了"深度"的意义——无法拟合非线性数据分布。
</details>

**Q2**：反向传播的核心思想是什么？它依赖于哪个数学法则？

<details><summary>答案</summary>

核心思想：将输出层的误差通过链式法则逐层传递回前面的层，让每个参数都能得到"这个参数对最终错误贡献了多少"的梯度。依赖微积分中的链式法则：∂L/∂W₁ = ∂L/∂a₂ · ∂a₂/∂z₂ · ∂z₂/∂a₁ · ∂a₁/∂z₁ · ∂z₁/∂W₁。
</details>

**Q3**：Adam 优化器为什么比纯 SGD 效果好？

<details><summary>答案</summary>

1. **自适应学习率**：每个参数有不同的学习率（经常更新的参数学习率小，稀疏参数学习率大）
2. **动量**：积累历史梯度方向，像滚雪球一样加速收敛
3. **二阶矩估计**：用梯度方差做归一化，更稳定
</details>

## 延伸阅读

### 中文资料

- [3Blue1Brown 神经网络视频（B站字幕版）](https://search.bilibili.com/all?keyword=3Blue1Brown+神经网络) — 最好的视觉化理解反向传播
- [TensorFlow 官方中文教程](https://www.tensorflow.org/tutorials?hl=zh-cn) — Google 官方，从基础到部署
- [Keras 中文文档](https://keras-zh.readthedocs.io/) — 社区翻译的 Keras 文档
- [神经网络从零搭建（知乎系列）](https://docs.python.org/3/) — 纯 NumPy 实现系列

### 英文资料（可能需科学上网）

- [Deep Learning Book (Goodfellow)](https://www.deeplearningbook.org/) — 花书，第6章前馈网络
- [Stanford CS231n](https://cs231n.github.io/) — 计算机视觉课的神经网络基础部分
- [TensorFlow 官方教程](https://www.tensorflow.org/tutorials) — 最权威的 TF 学习资源
- [Neural Networks from Scratch (YouTube)](https://www.youtube.com/watch?v=aircAruvnKk) — 3Blue1Brown 出品的经典视频
