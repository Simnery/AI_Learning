---
name: model-eval
description: 模型评估——生成评估脚本和指标报告。当用户要求评估模型、看指标时调用。
allowed-tools: Read Write Edit Bash
---

# 模型评估

## 流程

1. 确认模型路径和评估数据集
2. 根据任务类型选择指标：
   - **分类**: Accuracy, Precision, Recall, F1, AUC-ROC, Confusion Matrix
   - **回归**: MSE, MAE, RMSE, R²
   - **生成**: BLEU, ROUGE, Perplexity
   - **检测**: mAP, IoU
3. 生成评估脚本
4. 运行评估并生成中文指标报告
5. 可选的错误分析（bad case）

## 规则

- 支持从 checkpoint 加载模型
- 支持 GPU/CPU 指定
