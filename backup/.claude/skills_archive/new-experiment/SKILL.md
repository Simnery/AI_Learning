---
name: new-experiment
description: 创建一个新的 ML 实验/项目脚手架。当用户要求新建实验、创建项目时调用。
allowed-tools: Read Write Edit Bash Glob
---

# 新建 ML 实验项目

在 `projects/<domain>/<project-name>/` 下创建完整的实验项目脚手架。

## 目录结构

```
projects/<domain>/<project-name>/
├── README.md         # 实验名称、目的、方法论、预期结果
├── main.py           # 主入口脚本（含 argparse）
├── model.py          # 模型定义
├── train.py          # 训练逻辑
├── data.py           # 数据加载与预处理
├── config.yaml       # 超参数与配置
└── pyproject.toml    # uv/pip 依赖管理
```

## 领域选项

`llm`, `vision`, `audio`, `multimodal`, `agents`, `rl`, `nlp`, `cv`

## 流程

1. 与用户确认实验名称、目标、领域
2. 在对应 `projects/<domain>/` 下创建目录
3. 依次生成所有脚手架文件
