# 5.8.2 华为昇腾（Ascend）生态与CANN架构详解

> 5.8.2 昇腾CANN架构 > 5.8 昇腾部署DeepSeek > 5. 项目实战

## 核心概念

- **是什么**：昇腾（Ascend）是华为自研的 AI 计算芯片系列，CANN（Compute Architecture for Neural Networks）是其软件栈——类似 NVIDIA 的 CUDA。理解 CANN 架构是在昇腾上成功部署模型的前提。
- **为什么重要**：不使用 CUDA 意味着要适配一套全新的工具链。了解 CANN 的各层组件及其与 CUDA 的对应关系，能大幅降低迁移成本。昇腾 910B 的单卡 BF16 算力（320 TFLOPS）已接近 A100，但软件生态成熟度还有差距，需要清楚哪些操作有坑。
- **前置知识**：了解 CUDA 基本概念（GPU 编程、算子、显存管理）。推荐先看 [1.3.1 企业级部署](../../01_AI大模型基础/1-3_模型部署及高并发_——_理论知识+案例详解+实操/1-3-1_企业级AI部署从硬件选型到框架选择.md)。

### 昇腾硬件家族速览

| 芯片 | 定位 | BF16 算力 | 显存 | 适用场景 |
|------|------|----------|------|---------|
| 昇腾 310P | 推理/边缘 | 25 TFLOPS | 24GB | 边缘推理、视频分析 |
| 昇腾 910B | 训练/推理 | 320 TFLOPS | 64GB | 大模型训练、生产推理 |
| 昇腾 910C | 训练旗舰 | ~800 TFLOPS | 128GB | 超大模型训练（GPT-4级别） |

对于我们部署 DeepSeek V4 的场景，**910B 是主力卡**——单卡 64GB 显存，4卡组成 256GB 可以跑 V4 MoE 版本。

## 原理讲解

### CANN软件栈架构

```
应用层: PyTorch/TensorFlow (昇腾适配版)
   ↓
框架适配层: torch_npu (类似 torch.cuda)
   ↓
图编译层: ATC (Ascend Tensor Compiler, 类似 nvcc)
   ↓
运行时层: ACL (Ascend Computing Library, 类似 cuBLAS/cuDNN)
   ↓
驱动层: Ascend Driver
   ↓
硬件: 昇腾 NPU (910B/310P)
```

### 环境准备清单

```bash
# 1. 安装驱动和固件
# 参考华为官方文档: https://support.huawei.com/

# 2. 安装 CANN 工具包
# 包含: ACL库、ATC编译器、调试工具

# 3. 安装昇腾版 PyTorch
pip install torch-npu  # 替代 torch

# 4. 验证环境
python -c "import torch; import torch_npu; print(torch_npu.npu.is_available())"
# 预期: True
```

### CUDA → CANN 概念对应

| CUDA | CANN | 说明 |
|------|------|------|
| `torch.cuda` | `torch_npu` | 设备管理 |
| `cuda()/to('cuda')` | `npu()/to('npu')` | 模型迁移 |
| nvcc | ATC | 模型编译 |
| cuBLAS | ACL | 算子库 |
| TensorRT | AOE (Ascend Optimization Engine) | 推理优化 |

## 代码实战

```python
"""昇腾环境检测、模型迁移与性能对比 —— 从CUDA迁移到昇腾的完整检查清单"""

# pip install torch-npu  # 注意：不是 torch，是 torch-npu

import torch
import torch_npu
import time

# ============================================================
# 1. 环境检测
# ============================================================
def check_ascend_env():
    """检测昇腾环境——部署前第一件事"""
    print(f"NPU 可用: {torch_npu.npu.is_available()}")
    print(f"NPU 数量: {torch_npu.npu.device_count()}")
    
    for i in range(torch_npu.npu.device_count()):
        props = torch_npu.npu.get_device_properties(i)
        total_gb = props.total_memory / 1024**3
        print(f"  NPU {i}: {torch_npu.npu.get_device_name(i)}, 显存 {total_gb:.1f} GB")


# ============================================================
# 2. 模型迁移（和 CUDA 几乎一样）
# ============================================================
def migrate_model_to_npu(model: torch.nn.Module) -> torch.nn.Module:
    """将 PyTorch 模型迁移到 NPU
    
    CUDA 到昇腾的核心转换：torch.cuda → torch_npu, "cuda" → "npu"
    """
    device = torch.device("npu:0" if torch_npu.npu.is_available() else "cpu")
    model = model.to(device)
    return model


# ============================================================
# 3. 兼容性测试 —— 验证迁移后没有算子缺失
# ============================================================
def test_operator_compatibility():
    """测试关键算子是否在 NPU 上可用"""
    device = "npu:0" if torch_npu.npu.is_available() else "cpu"
    
    test_cases = {
        "matmul": lambda: torch.randn(100, 100, device=device) @ torch.randn(100, 100, device=device),
        "conv2d": lambda: torch.nn.Conv2d(3, 16, 3).to(device)(torch.randn(1, 3, 32, 32, device=device)),
        "attention": lambda: torch.nn.MultiheadAttention(64, 8).to(device)(
            torch.randn(10, 4, 64, device=device),
            torch.randn(10, 4, 64, device=device),
            torch.randn(10, 4, 64, device=device),
        ),
        "layer_norm": lambda: torch.nn.LayerNorm(64).to(device)(torch.randn(4, 10, 64, device=device)),
        "softmax": lambda: torch.softmax(torch.randn(4, 10, device=device), dim=-1),
    }
    
    for name, fn in test_cases.items():
        try:
            fn()
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")


# ============================================================
# 4. 性能对比（可选：在 A100 和 910B 上分别跑）
# ============================================================
def benchmark_matmul(device: str, size: int = 4096, warmup: int = 3, repeats: int = 10):
    """矩阵乘法性能测试——最基础的算子性能基准"""
    a = torch.randn(size, size, device=device)
    b = torch.randn(size, size, device=device)
    
    # warmup
    for _ in range(warmup):
        _ = a @ b
    torch.cuda.synchronize() if "cuda" in device else torch_npu.npu.synchronize()
    
    # benchmark
    t0 = time.time()
    for _ in range(repeats):
        _ = a @ b
    torch.cuda.synchronize() if "cuda" in device else torch_npu.npu.synchronize()
    
    elapsed = time.time() - t0
    tflops = 2 * size**3 * repeats / elapsed / 1e12
    print(f"  [{device}] {size}x{size} matmul: {elapsed/repeats*1000:.2f}ms, {tflops:.2f} TFLOPS")


# ===== 使用示例 =====
if __name__ == "__main__":
    check_ascend_env()
    
    # 测试算子兼容性
    print("\n算子兼容性测试:")
    test_operator_compatibility()
    
    # 简单模型迁移
    model = torch.nn.Sequential(
        torch.nn.Linear(128, 256),
        torch.nn.ReLU(),
        torch.nn.Linear(256, 10),
    )
    model = migrate_model_to_npu(model)
    x = torch.randn(4, 128).to("npu:0")
    output = model(x)
    print(f"\n模型迁移测试: input {x.shape} → output {output.shape}")
    
    # 性能测试（如果在 NPU 上）
    if torch_npu.npu.is_available():
        print("\nNPU 性能测试:")
        benchmark_matmul("npu:0", size=2048)

# ===== 预期输出（在昇腾 910B 上）=====
# NPU 可用: True
# NPU 数量: 4
#   NPU 0: Ascend 910B, 显存 64.0 GB
#   ...
# 算子兼容性测试:
#   ✅ matmul
#   ✅ conv2d
#   ✅ attention
#   ✅ layer_norm
#   ✅ softmax
# 模型迁移测试: input torch.Size([4, 128]) → output torch.Size([4, 10])
# NPU 性能测试:
#   [npu:0] 2048x2048 matmul: 1.23ms, 13.98 TFLOPS
```

## 进阶方向

### 当前技术的局限性

| 局限 | 说明 |
|------|------|
| 算子覆盖率 | torch_npu 尚未 100% 覆盖 PyTorch 所有算子，部分自定义算子需用 CANN 的 Ascend C 语言手写 |
| 社区生态 | 相比 CUDA 的 StackOverflow/GitHub 资源量，昇腾社区仍在成长，遇到问题搜索到答案的概率较低 |
| 性能调优门槛 | 昇腾的性能分析工具（Profiling）与 NVIDIA Nsight 差异大，调优学习曲线陡峭 |
| 模型兼容性 | 部分 HuggingFace 模型直接 `to("npu")` 可能报错，因为某些 CUDA 特有算子（如 FlashAttention 特定版本）无对应的 NPU 实现 |

### 下一步学什么

1. **[5.8.3 昇腾部署DeepSeek V4实战](5-8-3_实战演练——在昇腾NPU上部署DeepS.md)** — 动手在 NPU 上部署模型
2. **[1.3.3 SGLang深度优化](../../01_AI大模型基础/1-3_模型部署及高并发_——_理论知识+案例详解+实操/1-3-3_SGLang深度优化Radix缓存与复杂.md)** — 推理框架优化方法论，昇腾上同样适用
3. **[3.5.2 PyTorch分布式训练](../../03_AI框架及工具平台/3-5_PyTorch与视觉检测/3-5-2_PyTorch分布式训练.md)** — 多卡协同原理，昇腾上的 NPU 分布式通信同理

### 工业界最佳实践

- **双环境策略**：开发/调试用 CUDA 环境（NVIDIA 卡），确认代码没问题后迁移到昇腾验证，不要直接在生产昇腾上调试
- **提前验证算子**：迁移前用 `torch_npu` 的算子兼容列表检查代码中使用的 PyTorch API，提前识别不支持的算子
- **使用华为官方容器镜像**：华为提供预装 CANN + torch_npu + vLLM 的 Docker 镜像，比从零安装节省大量时间
- **性能对标**：在 A100 和 910B 上分别跑同一模型，做延迟/吞吐对比，明确昇腾的实际性能差距

---

## 常见问题

### 小白最常踩的 3 个坑

**坑 1：直接在昇腾上装标准 PyTorch**

标准 PyTorch 只支持 CUDA/CPU，不支持 NPU。必须安装昇腾适配版：`pip install torch-npu`。装完标准版再装 torch_npu 会导致冲突，建议用独立虚拟环境。

**坑 2：认为 .to("npu") 就能解决一切**

模型迁移不只是改设备名称。某些 CUDA 特定的算子（如 `F.scaled_dot_product_attention` 的特定参数组合）在 NPU 上可能不支持或者行为不同。迁移后必须跑一遍完整的正确性测试。

**坑 3：忽略 ATC 编译这一步**

CANN 的 ATC（Ascend Tensor Compiler）类似 nvcc，把模型图编译为昇腾可执行的 OM 格式。跳过 ATC 直接用 torch_npu 推理虽然也行（在线编译），但会牺牲大量性能——离线编译后再推理，延迟能降 30-50%。

### 自检题

**Q1**：CANN软件栈的五个层次从上到下是什么？<details><summary>答案</summary>应用层(PyTorch/TF)→框架适配层(torch_npu)→图编译层(ATC)→运行时层(ACL)→驱动层→NPU硬件。</details>

**Q2**：将PyTorch代码从CUDA迁移到昇腾，主要改动是什么？<details><summary>答案</summary>把`cuda`替换为`npu`：`torch.cuda`→`torch_npu`、`.cuda()`→`.npu()`、`'cuda'`→`'npu'`。大部分代码改动很少，`torch_npu`兼容PyTorch API。</details>

**Q3**：为什么不能直接装标准 PyTorch 就在昇腾上用？<details><summary>答案</summary>标准 PyTorch 只编译了 CUDA 和 CPU 后端，不包含 NPU 算子实现。必须安装华为适配的 `torch-npu` 包，它会注册 NPU 作为新的设备类型，并把 PyTorch 算子映射到 CANN 的 ACL 库。</details>

---

## 延伸阅读

- [华为昇腾社区官方文档](https://www.hiascend.com/document) — CANN 安装指南、算子清单、性能调优手册，最权威的一手资料
- [CANN 算子开发指南 (华为官网)](https://www.hiascend.com/document/detail/zh/canncommercial/601/) — 需要自定义算子时的参考文档
- [昇腾 PyTorch 适配指南 (Gitee)](https://gitee.com/ascend/pytorch) — torch_npu 的开源仓库，含算子支持列表和迁移 FAQ
- [从 CUDA 到 CANN：AI 框架迁移实战 (知乎)](https://docs.python.org/3/) — 中文迁移经验贴，含常见报错和解决方案
- [ModelZoo 昇腾模型库 (Gitee)](https://gitee.com/ascend/modelzoo) — 华为官方适配的预训练模型，含 DeepSeek 等多个主流模型
