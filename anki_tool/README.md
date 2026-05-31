# Anki 英语学习卡片工具

## 目录结构

```
anki_tool/
├── templates/                    # 模板备份
│   ├── 00_model_template.json    # 笔记类型完整定义
│   └── 01_sample_cards.json      # 5 张示例卡片数据
├── cards/                        # 知识图谱卡片数据源
│   ├── ch1_cards.json            # Ch1 大模型基础 (133)
│   ├── ch2_cards.json            # Ch2 应用技术 (61)
│   ├── ch3_cards.json            # Ch3 框架工具 (99)
│   ├── ch4_cards.json            # Ch4 研发新范式 (35)
│   ├── ch5_cards.json            # Ch5 项目实战 (65)
│   └── ch6_cards.json            # Ch6 面试辅导 (46)
├── scripts/                      # 可执行工具
│   ├── anki_regen.py             # 批量导入 JSON→Anki
│   ├── anki_edit.py              # 单卡编辑（改音频/释义/例句）
│   ├── anki_add.py               # 交互式添加单卡
│   ├── anki_model.py             # 笔记类型管理
│   └── anki_sync.py              # 同步 JSON 某字段到 Anki
├── export/                       # 导出的牌组备份
└── README.md
```

## 快速使用（cd 到 anki_tool/ 目录）

```bash
cd anki_tool/

# 导入整章卡片
python scripts/anki_regen.py cards/ch1_cards.json --deck "01-AI大模型基础"

# 同步 Notes 修改到 Anki（不动音频）
python scripts/anki_sync.py cards/ch1_cards.json Notes

# 修复某卡音频
python scripts/anki_edit.py RAG --audio ""

# 交互式添加新词
python scripts/anki_add.py

# 管理笔记类型
python scripts/anki_model.py
```

## 笔记类型

**English Word** — 7 字段：Word | Pronunciation | Audio | Definition | ExampleEN | ExampleCN | Notes
