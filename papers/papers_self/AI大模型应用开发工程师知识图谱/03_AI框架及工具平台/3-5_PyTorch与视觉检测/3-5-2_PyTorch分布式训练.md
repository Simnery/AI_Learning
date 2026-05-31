# 3.5.2 PyTorch分布式训练

> 3.5.2 PyTorch分布式训练 > 3.5 PyTorch与视觉检测 > 3. AI框架及工具平台

## 核心概念

- **是什么**：分布式训练就是让多张 GPU（或多台机器）同时训练一个模型。PyTorch 提供了 `DataParallel`（DP，简单但慢）、`DistributedDataParallel`（DDP，推荐）和 `FSDP`（全分片，大模型专用）等多种并行策略。
- **为什么重要**：一张 GPU 24GB 显存只能训练约 7B 参数的模型。要想训练更大模型或更快出结果，必须分布式。Transformer 时代的 Scaling Law 就是靠分布式训练堆出来的。
- **前置知识**：PyTorch 基础（参考 [3-5-1 PyTorch核心概念](3-5-1_PyTorch核心概念.md)）、神经网络训练基本流程。

### 三种并行方式对比

| 方式 | 原理 | 显存效率 | 速度 | 适用 |
|------|------|---------|------|------|
| **DP** | 单机多 GPU，主卡聚合梯度 | 差（主卡瓶颈） | 慢 | 简单 demo，不推荐 |
| **DDP** | 多进程单 GPU，AllReduce 同步梯度 | 中等 | 快 | **生产环境首选** |
| **FSDP** | 模型参数/梯度/优化器分片到各卡 | 最优 | 中 | 7B+ 大模型训练 |

## 原理讲解

### 1. DDP 工作原理

```
┌─────────────────────────────────────────────────┐
│                   DDP 训练流程                    │
│                                                  │
│  GPU 0: [数据块0] → 前向 → 反向 → 本卡梯度       │
│  GPU 1: [数据块1] → 前向 → 反向 → 本卡梯度       │──→ AllReduce 平均梯度
│  GPU 2: [数据块2] → 前向 → 反向 → 本卡梯度       │
│  GPU 3: [数据块3] → 前向 → 反向 → 本卡梯度       │
│                                                  │
│  每张卡拿到平均梯度 → 各自更新参数（参数保持一致） │
└─────────────────────────────────────────────────┘
```

关键点：DDP 每张卡有完整模型副本，数据切分到不同卡，反向传播后用 **AllReduce** 把所有卡的梯度求平均，保证每张卡的参数更新完全一致。

### 2. FSDP——训练超大模型

DDP 的问题是每张卡都要存完整模型，当模型 > 单卡显存时就跑不了。FSDP 把模型参数、梯度、优化器状态都切分到不同卡上：

```
DDP: 每卡存完整模型                   FSDP: 每卡只存 1/N 模型
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ 完整  │ │ 完整  │ │ 完整  │ │ 完整  │   │ 1/4  │ │ 1/4  │ │ 1/4  │ │ 1/4  │
│ 模型  │ │ 模型  │ │ 模型  │ │ 模型  │   │ 模型  │ │ 模型  │ │ 模型  │ │ 模型  │
└──────┘ └──────┘ └──────┘ └──────┘   └──────┘ └──────┘ └──────┘ └──────┘
   4×24GB = 96GB → 最大 ~24GB/卡         4×24GB → 最大 ~96GB 模型！
```

### 3. PyTorch Lightning 简化了什么

Lightning 把训练模板代码（训练/验证/测试循环、日志、checkpoint、DDP 启动）全部封装，你只需写模型和数据：

```
纯 PyTorch:        300 行（模型 + 训练循环 + DDP 逻辑 + 日志...）
Lightning:          50 行（只写模型 + 数据，其余自动）
```

## 代码实战

> 依赖安装：`pip install torch torchvision pytorch-lightning`

### 示例1：DDP 从零上手（单机多 GPU）

```python
import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, TensorDataset
import os

# ---- 初始化分布式环境 ----
def setup(rank, world_size):
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def cleanup():
    dist.destroy_process_group()

# ---- 训练函数（每个进程执行） ----
def train(rank, world_size):
    setup(rank, world_size)
    
    # 模型 + DDP 包装
    model = nn.Sequential(
        nn.Linear(20, 64), nn.ReLU(),
        nn.Linear(64, 32), nn.ReLU(),
        nn.Linear(32, 2)
    ).to(rank)
    
    ddp_model = DDP(model, device_ids=[rank])
    
    # 数据 + 分布式采样器
    X = torch.randn(4000, 20)
    y = torch.randint(0, 2, (4000,))
    dataset = TensorDataset(X, y)
    sampler = torch.utils.data.distributed.DistributedSampler(
        dataset, num_replicas=world_size, rank=rank
    )
    loader = DataLoader(dataset, batch_size=32, sampler=sampler)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(ddp_model.parameters(), lr=0.001)
    
    for epoch in range(3):
        sampler.set_epoch(epoch)  # 每个 epoch 重新打乱
        total_loss, correct, total = 0, 0, 0
        
        ddp_model.train()
        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(rank), batch_y.to(rank)
            optimizer.zero_grad()
            loss = criterion(ddp_model(batch_x), batch_y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            correct += (ddp_model(batch_x).argmax(1) == batch_y).sum().item()
            total += batch_y.size(0)
        
        if rank == 0:
            print(f"Epoch {epoch+1} | Loss: {total_loss/len(loader):.4f} | Acc: {correct/total:.3f}")
    
    cleanup()

if __name__ == "__main__":
    world_size = torch.cuda.device_count()  # 自动检测 GPU 数量
    torch.multiprocessing.spawn(train, args=(world_size,), nprocs=world_size)
```

### 示例2：PyTorch Lightning 简化版

```python
import pytorch_lightning as pl
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# 只需定义模型 + 数据 + 训练逻辑
class LitModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(20, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 2)
        )
        self.criterion = nn.CrossEntropyLoss()
    
    def forward(self, x):
        return self.net(x)
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        acc = (logits.argmax(1) == y).float().mean()
        self.log("train_loss", loss, prog_bar=True)
        self.log("train_acc", acc, prog_bar=True)
        return loss
    
    def configure_optimizers(self):
        return torch.optim.AdamW(self.parameters(), lr=0.001)

# 数据
X = torch.randn(4000, 20)
y = torch.randint(0, 2, (4000,))
dataset = TensorDataset(X, y)
loader = DataLoader(dataset, batch_size=32)

# 训练——一行启动，自动处理 DDP/日志/checkpoint
trainer = pl.Trainer(
    max_epochs=5,
    accelerator="gpu",          # 自动检测 GPU
    devices="auto",             # 自动使用所有 GPU
    strategy="ddp",             # 自动启用 DDP
    log_every_n_steps=10,
    enable_progress_bar=True,
)

model = LitModel()
trainer.fit(model, loader)
print("训练完成！")
```

### 示例3：FSDP 训练大模型

```python
import torch
import torch.nn as nn
from torch.distributed.fsdp import (
    FullyShardedDataParallel as FSDP,
    ShardingStrategy
)
import torch.distributed as dist
import os

def fsdp_train(rank, world_size):
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)
    
    # 模拟一个大模型（实际使用时替换为 LLaMA 等）
    model = nn.Sequential(
        nn.Linear(4096, 4096), nn.ReLU(),
        nn.Linear(4096, 4096), nn.ReLU(),
        nn.Linear(4096, 4096), nn.ReLU(),
        nn.Linear(4096, 2),
    ).to(rank)
    
    # FSDP 包装——自动分片参数/梯度/优化器
    fsdp_model = FSDP(
        model,
        sharding_strategy=ShardingStrategy.FULL_SHARD,  # 全分片
        device_id=rank,
    )
    
    # 正常训练即可，FSDP 透明处理通信
    optimizer = torch.optim.AdamW(fsdp_model.parameters(), lr=0.001)
    X = torch.randn(1000, 4096).to(rank)
    y = torch.randint(0, 2, (1000,)).to(rank)
    
    fsdp_model.train()
    for step in range(100):
        optimizer.zero_grad()
        loss = nn.CrossEntropyLoss()(fsdp_model(X), y)
        loss.backward()
        optimizer.step()
        
        if step % 20 == 0 and rank == 0:
            print(f"Step {step:3d} | Loss: {loss.item():.4f}")

if __name__ == "__main__":
    world_size = torch.cuda.device_count()
    torch.multiprocessing.spawn(fsdp_train, args=(world_size,), nprocs=world_size)
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

- DDP 要求每张卡存完整模型，不适合 7B+ 参数模型
- FSDP 通信开销比 DDP 大（因为参数要动态 all-gather），小模型用 DDP 更快
- Lightning 封装虽好，遇到需要定制分布式通信逻辑的场景仍需回到纯 PyTorch

### 2. 下一步学习

| 主题 | 说明 | 相关节点 |
|------|------|----------|
| DeepSpeed ZeRO | 微软的分布式训练优化（比 FSDP 更成熟） | 官方文档 |
| 模型并行 vs 数据并行 | 把模型层切分到不同卡 | HuggingFace 文档 |
| PyTorch 2.0 torch.compile | 静态图编译加速分布式 | PyTorch 官方 Blog |
| 图像识别 | CNN 实战训练 | [3-5-3 图像识别](3-5-3_图像识别技术与缺陷检测.md) |

### 3. 工业界最佳实践

- **小模型（<7B）**：DDP + PyTorch Lightning，最简单可靠
- **大模型（7B-70B）**：FSDP 或 DeepSpeed ZeRO-3
- **超大模型（70B+）**：张量并行 + 流水线并行 + 数据并行混合使用
- **监控**：用 `torch.cuda.memory_summary()` 或 `nvidia-smi dmon` 监控显存

## 常见问题

### 小白最常踩的坑

1. **只在一张卡上跑**：写了 DDP 代码但用 `python train.py` 启动，而不是 `torchrun --nproc_per_node=N train.py`。正确姿势是用 `torchrun` 或 `torch.multiprocessing.spawn`
2. **NCCL 通信死锁**：不同进程间的数据形状/batch 数量不一致导致 AllReduce 永远等不到。确保所有卡处理相同数量的样本
3. **Lightning 版本兼容**：PyTorch Lightning 大版本间 API 变化大（1.x → 2.x），锁版本学习

### 自检题

**Q1**：DDP、DP、FSDP 分别代表什么？各自的使用场景是什么？

<details><summary>答案</summary>

- DP（DataParallel）：单机多 GPU 简单方案，主卡聚合瓶颈，不推荐
- DDP（DistributedDataParallel）：多进程 + AllReduce 梯度同步，每卡完整模型，**生产首选**
- FSDP（FullyShardedDataParallel）：参数/梯度/优化器全分片，训练超大模型用
</details>

**Q2**：DDP 中 DistributedSampler 的作用是什么？为什么每 epoch 要调用 `sampler.set_epoch(epoch)`？

<details><summary>答案</summary>

DistributedSampler 确保每张卡拿到不同且不重复的数据子集。`set_epoch(epoch)` 在每个 epoch 开始时改变 shuffle 的随机种子，保证不同 epoch 间数据顺序不同，避免模型过拟合于固定的数据顺序。
</details>

**Q3**：PyTorch Lightning 帮你自动处理了哪些事情？（至少说 4 个）

<details><summary>答案</summary>

1. 多 GPU 启动（DDP spawn）
2. 日志记录和进度条（TensorBoard、WandB 集成）
3. 模型 Checkpoint 自动保存和恢复
4. 混合精度训练（`precision="16-mixed"`）
5. 早停和 LR Scheduler
6. 梯度裁剪
</details>

## 延伸阅读

### 中文资料

- [PyTorch DDP 官方教程（中文翻译）](https://pytorch.apachecn.org/tutorials/intermediate/ddp_tutorial.html) — 详细的多 GPU 训练指南
- [B站：PyTorch分布式训练实战](https://search.bilibili.com/all?keyword=PyTorch+分布式训练+DDP) — 视频跟练
- [PyTorch Lightning 中文文档](https://lightning.ai/docs/pytorch/stable/) — 官方文档，英文但示例足

### 英文资料（可能需科学上网）

- [DDP 官方教程](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html) — 必读入门
- [FSDP 官方文档](https://pytorch.org/docs/stable/fsdp.html) — 大模型训练指南
- [DeepSpeed GitHub](https://github.com/microsoft/DeepSpeed) — 微软的分布式训练优化库
- [Lightning 官方文档](https://lightning.ai/docs/pytorch/stable/) — 标准化训练框架
