# 3. AI框架及工具平台

> **本章定位**：工具选型与动手层——把第 2 章的概念落到 LangChain、HuggingFace、PyTorch/TensorFlow 等具体框架上。

## 学习目标

学完本章你应能：

- 用 LCEL 或 LangChain 组装 RAG / Agent 链
- 对比 LangChain、LlamaIndex、AutoGen 并给出选型理由
- 使用 HuggingFace Pipeline / Trainer 完成推理与 LoRA 微调
- 完成一个 PyTorch 训练循环或 YOLO 检测小实验

## 建议学习顺序（约 3 周）

| 顺序 | 节点 | 说明 |
|:---:|------|------|
| 1 | [3-1 LangChain](3-1_LangChain多任务应用开发.md) | 与 2-1/2-2 对照阅读 |
| 2 | [3-2 框架选型](3-2_AI框架设计与选型.md) | 架构师视角 |
| 3 | [3-3 HuggingFace](3-3_HuggingFace生态实战从模型应用到高效微调.md) | 微调主战场 |
| 4 | [3-4 TensorFlow](3-4_神经网络基础与TensorFlow实战.md) | 可选，补传统 DL |
| 5 | [3-5-1 PyTorch核心](3-5_PyTorch与视觉检测/3-5-1_PyTorch核心概念.md) → 3-5-4 YOLO | CV 与 5-3/5-6 项目相关 |

## 先修 / 后继

- **先修**：[第 2 章](../02_AI应用技术/README.md) 2-1-1、2-3-1
- **后继**：[5-3 AI质检](../05_项目实战/5-3_AI质检.md)、[5-6 换脸](../05_项目实战/5-6_短剧视频逐帧换脸的显卡资源分配及排队系统/README.md)

## 本章验收清单

- [ ] 能画出 LangChain 六大组件关系图
- [ ] 能说出何时用 LlamaIndex 而非 LangChain
- [ ] 能跑通 HuggingFace `Trainer` + LoRA 示例
- [ ] （可选）能用 Ultralytics 训练/推理 YOLO

## 子模块目录

- [3.1 LangChain](3-1_LangChain多任务应用开发.md)
- [3.2 AI框架设计与选型](3-2_AI框架设计与选型.md)
- [3.3 HuggingFace生态](3-3_HuggingFace生态实战从模型应用到高效微调.md)
- [3.4 TensorFlow实战](3-4_神经网络基础与TensorFlow实战.md)
- **3.5 [PyTorch与视觉检测](3-5_PyTorch与视觉检测/README.md)** (4 篇)
