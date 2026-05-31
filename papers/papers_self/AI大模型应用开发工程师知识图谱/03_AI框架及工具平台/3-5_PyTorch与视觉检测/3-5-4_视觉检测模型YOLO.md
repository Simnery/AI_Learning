# 3.5.4 视觉检测模型YOLO

> 3.5.4 视觉检测模型YOLO > 3.5 PyTorch与视觉检测 > 3. AI框架及工具平台

## 核心概念

- **是什么**：YOLO（You Only Look Once）是最经典的单阶段目标检测算法，从 2015 年的 v1 发展到现在的 v12。Ultralytics 是 YOLO 最流行的实现，10 行代码就能完成训练和推理。目标检测 = 找出图中所有感兴趣物体，给出类别 + 边界框。
- **为什么重要**：YOLO 把目标检测从"实验室论文"变成了"工业级工具"——速度快（实时）、精度高、上手简单。在工业缺陷检测、安防监控、自动驾驶、医疗影像中广泛应用。
- **前置知识**：PyTorch 基础（参考 [3-5-1 PyTorch核心概念](3-5-1_PyTorch核心概念.md)）、CNN 基础（参考 [3-5-3 图像识别与缺陷检测](3-5-3_图像识别技术与缺陷检测.md)）。

### YOLO 一句话理解

把目标检测从"两步走"（先找候选区 → 再分类）变成"一步到胃"（直接预测类别+位置）：

```
传统两阶段:  区域提议 → CNN特征提取 → 分类 + 边框回归  （慢）
YOLO单阶段:  整图 → CNN → 直接输出所有目标的类别+位置  （快！）
```

## 原理讲解

### 1. YOLO 核心思想

YOLO 把输入图片划分为 S×S 个网格。每个网格负责预测落在自己范围内的物体：

```
┌───┬───┬───┬───┐
│   │   │   │   │   每个网格预测:
├───┼───┼───┼───┤   - B 个边界框 (x, y, w, h, confidence)
│   │ 🐱│   │   │   - C 个类别概率
├───┼───┼───┼───┤
│   │   │   │   │   狗在 (3, 2) 网格 → 预测框中心 (3.2, 2.1)
├───┼───┼───┼───┤   框大小 (1.5, 1.8) → 还原到原图尺寸
│   │   │   │ 🐕│
└───┴───┴───┴───┘
```

### 2. YOLO 版本演进

| 版本 | 年份 | 核心改进 | 关键创新 |
|------|------|---------|---------|
| v1 | 2015 | 开创单阶段检测 | 把检测变成回归问题 |
| v2 | 2016 | 精度大幅提升 | 引入 Anchor Box、BatchNorm |
| v3 | 2018 | 多尺度检测 | FPN（特征金字塔）三尺度输出 |
| v5 | 2020 | **工程化巅峰** | 社区驱动，Ultralytics 实现，工业界最爱 |
| v8 | 2023 | 无锚框（Anchor-Free） | 更简洁，精度速度双提升 |
| v10 | 2024 | NMS-Free | 端到端，去掉后处理步骤 |
| v11-12 | 2025 | 注意力机制增强 | Transformer 模块集成 |

> 实用建议：大多数场景用 **YOLOv8** 或 **YOLOv11**（成熟稳定）；追求最新用 v12；嵌入式设备用 YOLOv8-nano。

### 3. 关键概念：Anchor Box vs Anchor-Free

```
Anchor-Based (v3-v7):              Anchor-Free (v8+):
预定义 N 种框的宽高比              直接预测关键点/中心点
┌──┐ ┌────┐ ┌──┐                 ┌─────────────┐
│  │ │    │ │  │                 │   ☐ → 中心点 │
└──┘ └────┘ └──┘                 │   ↓ 宽高偏移 │
选择最匹配的那个                    └─────────────┘
需要调参                          无超参数
```

### 4. mAP——目标检测的核心指标

**mAP（mean Average Precision）**是目标检测的标准评估指标：
- **Precision**：你检测出来的"物体"，有多少是真的
- **Recall**：图里所有的真物体，你找出了多少
- **mAP@0.5**：IoU ≥ 0.5 就算检测正确（最常用）
- **mAP@0.5:0.95**：更多 IoU 阈值的平均（COCO 标准，更严格）

## 代码实战

> 依赖安装：`pip install ultralytics opencv-python matplotlib`

### 示例1：YOLO 10 行代码完成推理

```python
from ultralytics import YOLO
import cv2

# 加载预训练模型（自动下载）
model = YOLO("yolo11n.pt")  # n=nano, s=small, m=medium, l=large, x=xlarge

# 单张图片检测
results = model("https://ultralytics.com/images/bus.jpg")

# 显示结果
for r in results:
    print(f"检测到 {len(r.boxes)} 个物体")
    # 每个检测框: [x1, y1, x2, y2, confidence, class]
    for box in r.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        name = model.names[cls_id]
        xyxy = box.xyxy[0].tolist()
        print(f"  {name}: {conf:.2f} @ ({xyxy[0]:.0f}, {xyxy[1]:.0f}, {xyxy[2]:.0f}, {xyxy[3]:.0f})")

# 保存带标注的图片
results[0].save("output.jpg")
print("已保存到 output.jpg")
```

### 示例2：YOLO 训练自定义数据集

```python
from ultralytics import YOLO

# 1. 准备数据
# 数据目录结构:
# dataset/
# ├── images/
# │   ├── train/  (训练图片)
# │   └── val/    (验证图片)
# ├── labels/
# │   ├── train/  (标注文件，每行: class_id x_center y_center w h，值为归一化0-1)
# │   └── val/
# └── data.yaml   (配置文件)

# data.yaml 内容:
# path: ./dataset
# train: images/train
# val: images/val
# names:
#   0: scratch    # 划痕
#   1: crack      # 裂纹
#   2: stain      # 污点

# 2. 加载模型
model = YOLO("yolo11n.pt")  # 从预训练权重开始（迁移学习）

# 3. 训练
results = model.train(
    data="dataset/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    lr0=0.001,           # 初始学习率
    patience=10,         # 早停等待轮数
    device="cuda",       # 或 "cpu"
    name="defect_detector",
    exist_ok=True        # 覆盖同名实验
)

# 4. 评估
metrics = model.val()
print(f"mAP@0.5: {metrics.box.map50:.4f}")
print(f"mAP@0.5:0.95: {metrics.box.map:.4f}")

# 5. 导出为 ONNX（部署用）
model.export(format="onnx")  # 生成 best.onnx
```

### 示例3：钢铁表面缺陷检测项目

```python
import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt

# 模拟钢铁表面图片生成（替代真实工业相机采集）
def generate_steel_image(with_defect=False):
    """生成 640×640 的模拟钢铁表面图"""
    img = np.ones((640, 640, 3), dtype=np.uint8) * 180  # 灰色背景
    
    # 添加金属纹理
    noise = np.random.randint(-15, 15, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # 添加光照不均
    x = np.linspace(0, 1, 640)
    gradient = (1 - 0.3 * x**2).reshape(1, 640, 1)
    img = np.clip(img * gradient, 0, 255).astype(np.uint8)
    
    if with_defect:
        # 随机位置生成"划痕"
        cx, cy = np.random.randint(100, 540, 2)
        cv2.line(img, (cx-40, cy), (cx+40, cy+np.random.randint(-5, 5)),
                 (40, 40, 40), thickness=np.random.randint(2, 5))
    
    return img

# 生成几张示例图看看效果
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for i, ax in enumerate(axes):
    img = generate_steel_image(with_defect=(i > 0))
    ax.imshow(img)
    ax.set_title("良品" if i == 0 else "缺陷品")
    ax.axis('off')
plt.savefig("steel_samples.png")
plt.close()
print("示例图片已保存: steel_samples.png")
```

### 示例4：YOLO + 视频流实时检测

```python
from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")

# 视频文件或摄像头（0 = 默认摄像头）
cap = cv2.VideoCapture(0)

# 设置只检测特定类别（人=0, 车=2, 在 COCO 数据集中）
target_classes = [0, 2]  # 只检测人和车

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # 推理
    results = model(frame, conf=0.5, classes=target_classes, verbose=False)
    
    # 绘制检测结果
    annotated = results[0].plot()
    
    # FPS 计算（简化）
    speed = results[0].speed  # 预处理 + 推理 + 后处理时间(ms)
    fps = 1000 / (sum(speed.values()) + 1e-8)
    cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("YOLO 实时检测", annotated)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("检测结束")
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

- YOLO 对小目标（<16×16 像素）检测效果差——需要高分辨率输入或 SAHI（切片推理）
- 密集场景下容易出现漏检——考虑用 YOLO + Tiled Inference
- 训练数据依赖强——工业场景每种缺陷都需要足够的标注样本

### 2. 下一步学习

| 主题 | 说明 | 相关节点 |
|------|------|----------|
| YOLO 自定义训练全流程 | 数据标注 → 训练 → 评估 → 部署 | 本文项目的完整版 |
| 目标跟踪 (ByteTrack) | YOLO + 跟踪实现视频计数 | Ultralytics 文档 |
| 实例分割 (YOLO-Seg) | 不仅框出物体，还分割轮廓 | Ultralytics 文档 |
| 模型压缩部署 | TensorRT/ONNX/NCNN 加速 | [1-3-1 企业级AI部署](../../01_AI大模型基础/1-3_模型部署及高并发_——_理论知识+案例详解+实操/1-3-1_企业级AI部署从硬件选型到框架选择.md) |

### 3. 工业界最佳实践

- **数据标注**：用 LabelImg、Roboflow、CVAT 等工具，导出 YOLO 格式
- **预训练 + 微调**：永远从 COCO 预训练权重开始（`yolo11n.pt`），不要从头训练
- **数据增强**：YOLO 内置 Mosaic、MixUp、HSV 变换，默认开启即可
- **模型选择**：nano 用于实时/嵌入式，small/medium 用于平衡，x 用于追求精度

## 常见问题

### 小白最常踩的坑

1. **标注格式搞错**：YOLO 要求归一化坐标（0-1），不是像素坐标。转换公式：`x_center/img_width, y_center/img_height, w/img_width, h/img_height`
2. **显存不够**：默认 batch=16 可能爆显存。减小 `batch` 或图片 `imgsz`，或用 nano 模型
3. **预训练权重不匹配**：用 `yolo11n.pt` 训练但 `nc`（类别数）变了会自动丢弃分类头，这是正常的，不用担心

### 自检题

**Q1**：YOLO 的核心思想是什么？为什么叫"You Only Look Once"？

<details><summary>答案</summary>

核心思想：将目标检测从两阶段（先找候选区域→再分类）变成单阶段——整张图只经过一次 CNN 前向传播，直接输出所有目标的类别和边界框。所以叫"You Only Look Once"（只看一眼）。
</details>

**Q2**：YOLO 数据标注的格式是什么？类别的边界框怎么表示？

<details><summary>答案</summary>

标注格式：`class_id x_center y_center width height`，五个值都归一化到 [0, 1]：
- `class_id`：类别编号（0, 1, 2...）
- `x_center, y_center`：框中心点坐标（除以图片宽高）
- `width, height`：框的宽高（除以图片宽高）
</details>

**Q3**：mAP@0.5 和 mAP@0.5:0.95 的区别是什么？

<details><summary>答案</summary>

- mAP@0.5：IoU（预测框与真实框的重叠度）≥ 0.5 就算检测正确。标准较宽松，工业界常用
- mAP@0.5:0.95：在 0.5 到 0.95 之间以 0.05 为步长取 10 个 IoU 阈值，分别计算 AP 再取平均。COCO 标准，更严格
</details>

## 延伸阅读

### 中文资料

- [Ultralytics 官方文档](https://docs.ultralytics.com/zh/) — 中文版文档，训练/验证/导出全覆盖
- [YOLO 系列演进史（知乎）](https://docs.python.org/3/) — 从 v1 到 v12 的完整梳理
- [B站：YOLOv8 实战教程](https://search.bilibili.com/all?keyword=YOLOv8+训练+自定义) — 视频实操，跟着做
- [钢铁表面缺陷检测实战（博客）](https://blog.csdn.net/search?q=YOLO+缺陷检测) — CSDN 上的实战文章

### 英文资料（可能需科学上网）

- [Ultralytics YOLO 文档](https://docs.ultralytics.com/) — 最全的 YOLO 教程
- [YOLO GitHub 仓库](https://github.com/ultralytics/ultralytics) — 源码 + Issue 讨论
- [YOLOv8 论文](https://arxiv.org/abs/2305.09972) — 技术细节
- [Roboflow Universe](https://universe.roboflow.com/) — 海量公开数据集，可直接导出 YOLO 格式
