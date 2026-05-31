# 06 项目实战

> **阶段定位**：把前 5 章学到的东西，以 BIOS 工程师的视角"编译链接"成 4 个能跑的项目。
> **总时长**：约 8-12 周（与 04、05 阶段并行推进）
> **前置依赖**：01 数学基础 + 02 ML 基础（可并行）；03-05 的对应模块按需补。

---

## 项目总览

4 个项目从简单到复杂，每个项目背后有明确的学习目标。

| # | 项目 | 难度 | 核心技术 | BIOS 价值 |
|---|------|------|---------|----------|
| 1 | BIOS 智能问答系统 | ★★☆ | RAG | 日常问答 spec 不用翻书 |
| 2 | BIOS 日志智能分析器 | ★★★ | Agent + RAG | 日志分析从人工变自动 |
| 3 | 代码 Review Agent | ★★★☆ | Agent + Tool Use | 自动验证代码规则 |
| 4 | 向量化 BIOS Spec 检索 | ★★★☆ | PDF Parse + RAG | 全量 spec 可检索 |

---

## 项目 1：BIOS 智能问答系统

> **目标**：本地搭建完整的 RAG 问答系统，用你自己的 BIOS 文档当知识库。
> **预计时间**：2-3 周

### 技术栈
- **LLM**: Ollama (llama3 / qwen2.5 / deepseek-r1)
- **Embedding**: bge-large-zh-v1.5 / text-embedding-3-small
- **向量数据库**: Chroma (入门) → FAISS (进阶)
- **框架**: LangChain / LlamaIndex（任选其一）

### 实现步骤

| 步骤 | 内容 | 时间 |
|------|------|------|
| 环境搭建 | 安装 Ollama，pull 模型，验证本地推理 | 1 天 |
| 文档准备 | 收集 3-5 份 BIOS spec PDF，提取文本 | 2 天 |
| Chunking | 试验不同的 chunk size (256/512/1024)，对比效果 | 2 天 |
| Embedding + 存储 | 生成向量，存入 Chroma/FAISS | 1 天 |
| 检索 | 实现相似度检索，加 Top-K 参数 | 1 天 |
| 问答 Pipeline | 检索结果 + prompt 模板 → LLM 回答 | 2 天 |
| 评估 | 准备 20 个问答测试集，人工评估准确率 | 1 天 |

### 验收标准
- [ ] 问"什么是 SMM？"能从 PDF 检索到 SMM 章节并生成准确回答
- [ ] 问"PCIe Configuration Space 有哪些寄存器？"能列出并引用出处
- [ ] 检索延迟 < 2 秒，回答生成 < 10 秒
- [ ] Top-3 检索结果中至少 1 个与问题真正相关

### 对应知识图谱
- `05_项目实战 / 5-1_企业知识库RAG大赛冠军项目` — 类似架构，企业级实现
- `05_项目实战 / 5-7_LLM_Wiki` — 知识库索引体系设计思路

---

## 项目 2：BIOS 日志智能分析器

> **目标**：构建一个能读 BIOS debug log、自动诊断故障原因的 Agent。
> **预计时间**：3-4 周

### 技术栈
- **LLM**: Ollama / DeepSeek API
- **API 框架**: FastAPI
- **向量库**: Chroma / FAISS（存储历史日志和解决方案）
- **Agent 框架**: LangChain Agent

### 实现步骤

| 步骤 | 内容 | 时间 |
|------|------|------|
| 日志解析 | 标准化 BIOS 日志格式（ERROR/WARNING/INFO），字段提取 | 2 天 |
| 知识库构建 | 历史故障日志 + 解决方案配对，Embedding 存储 | 2 天 |
| Agent 设计 | Tool: 检索相似日志 / 读取 spec 文档 / 查询已知解决方案 | 3 天 |
| API 服务 | FastAPI 封装，POST /analyze 返回诊断报告 | 2 天 |
| Streaming | SSE 实时输出分析过程（Agent 的思考步骤可视化） | 1 天 |
| 测试 | 准备 10 个不同的故障日志，验证诊断准确率 | 1 天 |

### BIOS 价值
- 定位内存 training 失败：读取 debug log → 匹配历史相似日志 → 输出可能原因和解决方案
- PCIe 枚举错误：追溯 BAR 分配链，定位失败的 device

### 验收标准
- [ ] 输入一段日志，Agent 能输出诊断报告（原因 + 建议 + 引用日志行）
- [ ] 能通过检索历史日志找到相似故障的解决方案
- [ ] API 响应时间 < 30 秒（含 Agent 的思考+工具调用）
- [ ] 支持至少 3 种不同类型的故障：内存、PCIe、SMM

---

## 项目 3：代码 Review Agent

> **目标**：构建一个能自动检查 BIOS 代码审查规则的 Agent。
> **预计时间**：2-3 周

### 技术栈
- **LLM**: Claude API / DeepSeek API（Coding 能力强的模型）
- **规则引擎**: 你的 `Code_Change_Rules_CN.md` 直接作为 System Prompt
- **Tool**: 文件读/写、Git diff 解析

### 核心思路
你已经用 Claude 做了一年的 Code Review。这个项目是把"手工打开 Claude，粘贴代码"变成"Agent 自动跑"。

| 步骤 | 内容 | 时间 |
|------|------|------|
| 规则模块化 | 把 `@Code_Change_Rules_CN.md` 拆成可独立执行的规则单元 | 2 天 |
| Git 集成 | 自动获取 git diff，识别变更的文件和行 | 1 天 |
| Review Pipeline | 逐规则检查 → 汇总报告 → 生成 markdown 格式的 review 结果 | 2 天 |
| 批量检测 | 支持扫描整个 codebase 而非仅 diff | 1 天 |
| 评分系统 | 每个规则通过/警告/失败，生成整体评分 | 1 天 |

### 验收标准
- [ ] Agent 能读取 git diff 并逐条对照 `Code_Change_Rules_CN.md` 检查
- [ ] Review 结果包含：违规规则编号 + 文件路径 + 行号 + 建议修改
- [ ] 误报率 < 20%（人工抽样 50 条 review 结论验证）
- [ ] 单次 review 耗时 < 2 分钟

### 对应知识图谱
- `04_AI研发工程师工作新范式 / 4-1_AI_Coding带来的范式变革` — 4 篇文章完整覆盖了 AI Code Review 的理论

---

## 项目 4：向量化 BIOS Spec 检索

> **目标**：把 PDF 格式的 BIOS Spec 全量向量化，支持自然语言检索。
> **预计时间**：2-3 周

### 技术栈
- **PDF 解析**: PyMuPDF / Unstructured / Marker
- **Embedding**: bge-large-zh-v1.5
- **向量数据库**: FAISS (性能) / Milvus (扩展到 10w+ 文档)
- **UI**: Streamlit（可选，做个简单 Web 界面）

### 实现步骤

| 步骤 | 内容 | 时间 |
|------|------|------|
| PDF 解析 | 提取文本 + 表格 + 代码块，保留章节结构 | 2 天 |
| 结构化 | 按章节 (Chapter/Section) 切分，保持层级关系 | 2 天 |
| 向量化 | 批量生成 embedding，选择合适的 batch size | 1 天 |
| 检索优化 | 混合检索（关键词 + 语义），Rerank 提升精度 | 2 天 |
| 性能测试 | 5 份 spec 共 2000+ 页，检索延迟 < 1s | 1 天 |
| Web 界面 | 简单搜索框 + 结果展示（可选） | 1 天 |

### 验收标准
- [ ] 5 份 BIOS spec PDF 成功解析并向量化（2000+ 页）
- [ ] 自然语言搜索"PCIe Root Port 的 BAR 分配流程"，能返回准确章节
- [ ] 检索延迟 < 1 秒，Top-5 准确率 > 80%
- [ ] 支持中英文混合搜索

### 对应知识图谱
- `05_项目实战 / 5-7_LLM_Wiki` — 完整覆盖了知识库构建的 4 个层次
- `02_AI应用技术 / 2-1_RAG` — RAG 全技术栈

---

## 项目通用注意事项

### 开发原则
1. **先跑通，再优化** — MVP 优先，不要一开始就追求完美架构
2. **用你自己的数据** — BIOS spec、debug log、code review 规则都是现成的
3. **记录踩坑** — 每个项目写一个 NOTES.md 记录遇到了什么问题、怎么解决的
4. **版本管理** — 每个项目独立 git repo 或独立目录，不要混在一起

### 工具统一选择
| 场景 | 推荐 | 原因 |
|------|------|------|
| 入门 RAG | LangChain | 文档多，社区大 |
| 高级 RAG | LlamaIndex | 检索策略更丰富 |
| 本地 LLM | Ollama | 零配置，开箱即用 |
| 向量库 (小) | Chroma | 一行 pip install，无需配置 |
| 向量库 (大) | FAISS | Meta 出品，性能好 |
| 向量库 (生产) | Milvus | 分布式，支持 10 亿级向量 |
| Agent 框架 | LangChain Agent | 生态完善 |

---

## 学习检查清单

- [ ] **项目 1 完成**：BIOS 智能问答系统能正确回答 spec 中的问题
- [ ] **项目 2 完成**：日志分析 Agent 能输出可用的诊断报告
- [ ] **项目 3 完成**：Code Review Agent 能自动检查代码规则
- [ ] **项目 4 完成**：BIOS Spec 检索系统能秒级返回相关章节
- [ ] 每个项目有独立的 README + NOTES.md（踩坑记录）
- [ ] 所有项目都用了你自己的真实 BIOS 数据和文档
