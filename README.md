# AI Learning

AI 大模型、算法、技术应用的系统学习工程。基于"AI大模型应用开发工程师"知识图谱，涵盖从基础理论到项目实战的完整学习路线。

## 项目结构

```
├── papers/               # 学习资料（知识图谱 + 扩展内容）
│   ├── papers_original/  # 官方知识图谱（知乎来源，6章）
│   └── papers_self/      # 个人扩展内容（66文件，6章）
├── anki_tool/            # Anki 英语学习卡片工具
│   ├── cards/            # 知识图谱卡片数据源 (JSON)
│   ├── scripts/          # 制卡/编辑/同步脚本
│   └── templates/        # 笔记类型模板
├── backup/               # 备用学习路线（BIOS 类比，4阶段）
└── .claude/              # Claude Code 配置（Skills / Rules / Memory）
```

## 学习路线

### 主路线：AI大模型应用开发工程师（6章）

| 章节 | 内容 | 论文数 |
|------|------|--------|
| 01 AI大模型基础 | 提示工程、RAG、Agent、多模态、模型部署、高并发 | 11 |
| 02 AI应用技术 | RAG、Agent、Function Calling、MCP、模型训练与微调 | 13 |
| 03 AI框架及工具平台 | LangChain、HuggingFace、PyTorch、TensorFlow | 9 |
| 04 AI研发新范式 | AI Coding 范式变革、大型项目重构、团队协作 | 11 |
| 05 项目实战 | 企业RAG、OpenManus、Agent长期记忆、昇腾部署 | 16 |
| 06 专项面试辅导 | RAG/Agent/框架/微调面试与简历辅导 | 4 |

### 备用路线：BIOS 类比学习（4阶段）

早期自设计路线，将 AI 学习类比为计算机启动过程：基础理论 → LLM 原理 → 应用开发 → 项目实战。

## Anki 英语卡片工具

基于 AnkiConnect 的英语学习卡片管理工具，6章知识图谱共 **439 张**卡片。

```bash
# 导入整章卡片
python anki_tool/scripts/anki_regen.py anki_tool/cards/ch1_cards.json --deck "01-AI大模型基础"

# 修改卡片音频/释义
python anki_tool/scripts/anki_edit.py RAG --audio ""

# 同步修改到 Anki
python anki_tool/scripts/anki_sync.py anki_tool/cards/ch1_cards.json Notes
```

## 技术栈

| 领域 | 工具/框架 |
|------|-----------|
| 深度学习 | PyTorch, Transformers, Diffusers |
| 数据处理 | NumPy, Pandas, Datasets |
| LLM 应用 | LangChain, LlamaIndex, Ollama |
| 向量检索 | FAISS, Chroma |
| 包管理 | uv, pip |

## 开始使用

```bash
git clone https://gitee.com/Learning-Lab/AI_Learning.git
cd AI_Learning

# 学习资料入口
# 主路线: papers/papers_self/AI大模型应用开发工程师知识图谱.md
# 备用路线: backup/AI_Learning_Roadmap.md
```

## 许可证

Apache License 2.0 — 详见 [LICENSE](LICENSE)（英文原文，具有法律效力）和 [LICENSE_CN](LICENSE_CN)（中文参考译文）
