# Backup — 归档内容

原项目初始化时创建的脚手架和 Skills，暂不启用，归档备用。

## 归档 Skills（`skills_archive/`）

| Skill | 用途 |
|-------|------|
| `new-experiment` | 在 `projects/<domain>/` 下创建 ML 实验脚手架 |
| `explore-data` | 数据集快速浏览分析（CSV/JSON/Parquet/HuggingFace） |
| `model-eval` | 模型评估脚本生成与指标报告 |
| `paper-notes` | 论文阅读笔记结构化记录 |

> 解封：把 `skills_archive/` 重命名为 `skills/`，再在父级 `settings.json` 里加上对应的 `Skill(xxx)` 权限。

## 项目脚手架（`projects/`）

初始规划的领域子目录模板：`llm` `vision` `audio` `multimodal` `agents`

## 目录镜像

`checkpoints/` `data/` `notebooks/` `outputs/` `papers/` `scripts/` — 初始 `.gitkeep` / README，实际数据已在 `.claudeignore` 排除。
