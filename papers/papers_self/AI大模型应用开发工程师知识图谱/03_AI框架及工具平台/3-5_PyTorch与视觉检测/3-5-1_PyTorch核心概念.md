# 3.5.1 PyTorch核心概念

> 3.5.1 PyTorch核心概念 > 3.5 PyTorch与视觉检测 > 3. AI框架及工具平台

## 核心概念

- **是什么**：PyTorch 是 Meta（Facebook）开源的深度学习框架，以**动态计算图**和 **Pythonic API** 著称。它现在是学术界和 LLM 社区的事实标准——BERT、GPT、LLaMA、Diffusion 模型大多用 PyTorch 实现。
- **为什么重要**：和 TensorFlow 相比，PyTorch 的调试体验好太多（能直接 print 中间张量、用 pdb 断点），学习曲线也平滑。如果你只学一个深度学习框架，选 PyTorch。
- **前置知识**：Python 基础、理解张量（多维数组）概念、了解神经网络基本组件（参考 [3-4 神经网络基础与TensorFlow实战](../3-4_神经网络基础与TensorFlow实战.md)）。

### PyTorch 核心三件套

| 概念 | 作用 | 类比 NumPy |
|------|------|------------|
| **Tensor** | 可在 GPU 上运算的多维数组 | `np.ndarray` + GPU |
| **Autograd** | 自动求梯度，记录每一步运算 | 没有对应，需手动链式法则 |
| **nn.Module** | 神经网络层的基类，管理参数和计算 | 没有直接对应 |

## 原理讲解

### 1. 动态图 vs 静态图——PyTorch 的杀手锏

这是 PyTorch 和 TensorFlow 1.x 最大的区别：

```
静态图 (TF 1.x)                    动态图 (PyTorch)
先画好图纸再施工                    边施工边决定下一步

定义 → 编译 → 执行                  定义即执行
x = tf.placeholder(...)            x = torch.tensor([1.,2.])
y = x * 2 + 1        # 只是画图   y = x * 2 + 1        # 立刻计算！
with tf.Session():                 print(y)  # 可以随时看结果
    print(sess.run(y))
```

**动态图的优势**：
- **调试友好**：可以 `print(tensor)`、`pdb.set_trace()` 随时看中间结果
- **灵活**：支持变长输入、条件分支、循环——这在 NLP 中极其重要
- **Pythonic**：写 PyTorch 代码就像写普通 Python，不用学"框架的方式"

**静态图的优势**（TF/JAX）：预先优化，理论上更快，但开发效率低了不止一个档次。

### 2. Autograd——自动求导的秘密

PyTorch 会在每个 Tensor 运算时悄悄记录一个**计算图**：

```python
x = torch.tensor([2.0], requires_grad=True)
y = x ** 2           # 记录: y = x²
z = y * 3            # 记录: z = 3y = 3x²
z.backward()         # 反向传播，计算 dz/dx
print(x.grad)        # dz/dx = 6x = 12
```

`backward()` 时 PyTorch 从 z 出发，按链式法则自动算出每个节点的梯度。这就是"自动求导"。

### 3. nn.Module——所有模型的基类

```python
class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 1)  # 自动注册为模型参数
    
    def forward(self, x):
        return self.linear(x)           # 定义前向传播
```

`nn.Module` 自动管理：
- **参数收集**：`model.parameters()` 返回所有可训练参数
- **设备迁移**：`model.to('cuda')` 一键搬上 GPU
- **保存/加载**：`torch.save(model.state_dict(), 'model.pth')`

## 代码实战

> 依赖安装：`pip install torch torchvision numpy matplotlib`

### 示例1：Tensor 基础操作

```python
import torch
import numpy as np

# Tensor 创建
a = torch.tensor([1, 2, 3])           # 从列表创建
b = torch.zeros(3, 4)                 # 全零矩阵 3×4
c = torch.randn(2, 3)                 # 标准正态分布 2×3
d = torch.from_numpy(np.array([1,2])) # NumPy → Tensor
e = torch.arange(0, 10, 2)            # [0, 2, 4, 6, 8]

# GPU 运算
if torch.cuda.is_available():
    gpu_tensor = torch.randn(1000, 1000).cuda()
    result = gpu_tensor @ gpu_tensor.T  # GPU 矩阵乘法

# 基本运算
x = torch.tensor([1.0, 2.0, 3.0])
y = torch.tensor([4.0, 5.0, 6.0])
print(f"加法: {x + y}")          # [5, 7, 9]
print(f"点积: {torch.dot(x, y)}") # 32.0
print(f"逐元素乘: {x * y}")      # [4, 10, 18]

# 索引和切片（和 NumPy 几乎一样）
t = torch.arange(12).reshape(3, 4)
print(t[0, :])     # 第一行
print(t[:, -1])    # 最后一列
print(t[1:, 1:3])  # 切片
```

### 示例2：Autograd 自动求导

```python
import torch

# 线性回归：y = wx + b，手写梯度训练
torch.manual_seed(42)
w = torch.randn(1, requires_grad=True)
b = torch.randn(1, requires_grad=True)

# 模拟数据
X = torch.linspace(0, 10, 100)
y_true = 3 * X + 5 + torch.randn(100) * 2  # y = 3x + 5 + 噪声

# 训练
lr = 0.01
for epoch in range(500):
    # 前向：预测
    y_pred = w * X + b
    
    # 损失：MSE
    loss = torch.mean((y_pred - y_true) ** 2)
    
    # 反向：自动算梯度
    loss.backward()
    
    # 更新参数（no_grad 防止更新被记录到计算图）
    with torch.no_grad():
        w -= lr * w.grad
        b -= lr * b.grad
    
    # 清空梯度（否则会累加！）
    w.grad.zero_()
    b.grad.zero_()
    
    if epoch % 200 == 0:
        print(f"Epoch {epoch:3d} | Loss: {loss.item():.4f} | w: {w.item():.3f}, b: {b.item():.3f}")

print(f"\n真实值: w=3.0, b=5.0")
print(f"拟合值: w={w.item():.3f}, b={b.item():.3f}")
```

### 示例3：nn.Module 构建神经网络

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# 定义模型
class MLP(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, out_dim)
        )
    
    def forward(self, x):
        return self.net(x)

# 模拟数据
X = torch.randn(1000, 20)
y = (X[:, 0] + 2*X[:, 1] - X[:, 2] > 0).long()  # 二分类

dataset = TensorDataset(X, y)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

# 模型、损失、优化器
model = MLP(20, 64, 2)
criterion = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=0.001)

# 训练循环（标准模板）
for epoch in range(10):
    model.train()
    total_loss, correct, total = 0, 0, 0
    
    for batch_x, batch_y in loader:
        optimizer.zero_grad()        # 1. 清空梯度
        output = model(batch_x)      # 2. 前向传播
        loss = criterion(output, batch_y)  # 3. 计算损失
        loss.backward()              # 4. 反向传播
        optimizer.step()             # 5. 更新参数
        
        total_loss += loss.item()
        correct += (output.argmax(1) == batch_y).sum().item()
        total += batch_y.size(0)
    
    print(f"Epoch {epoch+1:2d} | Loss: {total_loss/len(loader):.4f} | Acc: {correct/total:.3f}")

# 保存和加载模型
torch.save(model.state_dict(), "./mlp_model.pth")
# 加载: model.load_state_dict(torch.load("./mlp_model.pth"))
```

### 示例4：DataLoader 高效数据管道

```python
from torch.utils.data import Dataset, DataLoader

# 自定义数据集
class MyDataset(Dataset):
    def __init__(self, data, labels, transform=None):
        self.data = data
        self.labels = labels
        self.transform = transform
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        x = self.data[idx]
        y = self.labels[idx]
        if self.transform:
            x = self.transform(x)
        return x, y

# 使用
data = torch.randn(500, 10)
labels = torch.randint(0, 3, (500,))

dataset = MyDataset(data, labels)
loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,        # 每个 epoch 打乱
    num_workers=2,       # 多进程加载
    pin_memory=True,     # 加速 GPU 传输
    drop_last=True       # 丢弃最后不完整的 batch
)

# 迭代
for batch_idx, (x, y) in enumerate(loader):
    pass  # x.shape = (32, 10), y.shape = (32,)
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

- 动态图在极端性能场景下可能不如 JAX/TensorFlow 的静态编译优化（但 PyTorch 2.0 的 `torch.compile` 正在追赶）
- 分布式训练配置比 TensorFlow 稍复杂（不过 PyTorch Lightning 简化了很多）

### 2. 下一步学习

| 主题 | 说明 | 相关节点 |
|------|------|----------|
| PyTorch 分布式训练 | 多 GPU/多机训练 | [3-5-2 分布式训练](3-5-2_PyTorch分布式训练.md) |
| 图像识别与缺陷检测 | CNN + 工业检测实战 | [3-5-3 图像识别](3-5-3_图像识别技术与缺陷检测.md) |
| YOLO 目标检测 | 从 YOLOv1 到 YOLOv12 | [3-5-4 YOLO](3-5-4_视觉检测模型YOLO.md) |
| PyTorch 2.0 新特性 | torch.compile, inductor | 官方文档 |

### 3. 工业界最佳实践

- **训练模板**：`zero_grad → forward → loss → backward → step` 五步标准流程
- **设备管理**：定义 `device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')`，然后统一 `model.to(device)`
- **混合精度**：`torch.cuda.amp` 自动混合精度训练，几乎无代价提速 2x+

## 常见问题

### 小白最常踩的坑

1. **忘记 `zero_grad()`**：PyTorch 梯度默认累加，不手动清零会导致梯度越来越大。每个 batch 开头必须 `optimizer.zero_grad()`
2. **`model.eval()` 忘切换**：训练时 Dropout 和 BatchNorm 行为不同，不切换会导致推理结果不准
3. **Tensor 形状不匹配**：最常见的报错 `RuntimeError: mat1 and mat2 shapes cannot be multiplied`。在 `forward()` 里加 `print(x.shape)` 排查

### 自检题

**Q1**：动态图和静态图的区别是什么？为什么 PyTorch 选择动态图？

<details><summary>答案</summary>

- 动态图：定义即执行，每次前向传播重新构建计算图。优势是灵活、调试友好（可以随时 print 和断点）
- 静态图：先定义完整计算图再编译执行。优势是运行时优化更充分，但不够灵活
- PyTorch 选择动态图因为开发体验好得多，契合研究和快速迭代的需求
</details>

**Q2**：PyTorch 标准训练循环的五步是什么？

<details><summary>答案</summary>

1. `optimizer.zero_grad()` — 清空梯度
2. `output = model(data)` — 前向传播
3. `loss = criterion(output, target)` — 计算损失
4. `loss.backward()` — 反向传播（计算梯度）
5. `optimizer.step()` — 更新参数
</details>

**Q3**：`with torch.no_grad():` 的作用是什么？什么时候用？

<details><summary>答案</summary>

禁用自动求导，不构建计算图。用于：
- 推理/评估时（不需要反向传播，省显存提速）
- 手动更新参数时（如上面的线性回归手写训练）
- 模型验证阶段：`model.eval()` 配合 `@torch.no_grad()`
</details>

## 延伸阅读

### 中文资料

- [PyTorch 官方中文文档](https://pytorch.apachecn.org/) — 社区维护的文档翻译
- [动手学深度学习 (d2l.ai)](https://zh.d2l.ai/) — 最好的 PyTorch 动手教程，李沐出品
- [B站：李沐《动手学深度学习》](https://space.bilibili.com/1567748478) — 视频版，跟练效果好
- [PyTorch 入门到实战（知乎专栏）](https://docs.python.org/3/) — 国人写的实战系列

### 英文资料（可能需科学上网）

- [PyTorch 官方教程](https://pytorch.org/tutorials/) — 入门、图像、NLP、部署全覆盖
- [PyTorch 文档](https://pytorch.org/docs/stable/) — API 参考
- [PyTorch YouTube 频道](https://www.youtube.com/@PyTorch) — 官方教程视频
- [d2l.ai（英文版）](https://d2l.ai/) — Dive into Deep Learning，经典开源书
