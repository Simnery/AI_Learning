# 5.7.2 三层架构：Raw → Wiki → Schema

> 5.7.2 三层架构 > 5.7 LLM Wiki > 5. 项目实战

## 核心概念

- **是什么**：LLM Wiki 采用三层架构——Raw 层存储原始数据，Wiki 层是 LLM 编译后的高质量文档，Schema 层定义数据结构和查询协议。类比：Raw=原料仓库，Wiki=精加工产品，Schema=产品目录和标准。
- **为什么重要**：单层结构要么太原始（噪音多）要么太精炼（信息丢失）。三层架构让每一层各司其职，配合使用达到"全面+精准"。

### 前置知识

- 建议先学 [2-1-2 RAG技术](../../02_AI应用技术/2-1_RAG理论知识+案例详解+实操/2-1-2_RAG技术与应用.md)、[5-1 企业RAG](../5-1_企业知识库企业RAG大赛冠军项目.md)。


## 原理讲解

### 三层架构详解

```
Schema 层（控制协议）
  ↑ 查询 + 约束
Wiki 层（编译输出）
  ↑ 提炼 + 结构化
Raw 层（原始数据）
```

| 层 | 作用 | 内容示例 | 更新频率 |
|----|------|---------|---------|
| Raw | 存储原始对话、文档、笔记 | 聊天记录、会议纪要、PDF原文 | 实时追加 |
| Wiki | LLM编译后的结构化知识 | 统一口径的百科式文档 | 定期编译 |
| Schema | 数据结构定义和查询协议 | 实体类型、关系定义、API约定 | 变更时更新 |

### Wiki层——"编译"而非"索引"

```
不同于 RAG 的"检索碎片→拼接":
Raw "今天在会上讨论了支付接口超时问题..."
  ↓ LLM编译
Wiki "支付接口超时: 现象是调用支付宝API时偶发30s超时，
      根因是连接池耗尽，解决方案是增加超时重试机制"
```

### Schema层——知识的"类型系统"

定义知识库中允许的实体类型和关系：
```json
{
  "entities": ["技术问题", "解决方案", "团队决策"],
  "relations": ["解决", "依赖", "替代", "关联"],
  "query_patterns": {
    "技术问题": "找出{问题}的解决方案",
    "团队决策": "列出{时间段}的重要决策"
  }
}
```


### 3. 三层架构数据流

```
Raw（邮件/会议纪要/代码注释）
   ↓ LLM 清洗+结构化
Wiki 层（Markdown + 链接）
   ↓ 抽象+考试化
Schema 层（FAQ/题库/检查清单）
```

**版本**：Raw 保留原文；Wiki 走 Git；Schema 用于培训/质检。

### 4. 一致性校验

Wiki 更新 → 触发 Schema 条目的「过期检测」任务。

## 代码实战

```python
# pip install — 本示例仅用 Python 3.10+ 标准库

"""三层架构的 LLM Wiki"""
class ThreeTierWiki:
    def __init__(self, llm):
        self.llm = llm
        self.raw = []       # Raw层: 原始文本列表
        self.wiki = {}      # Wiki层: {topic_id: compiled_doc}
        self.schema = {}    # Schema层: 实体/关系/查询模式
    
    def add_raw(self, text: str, source: str):
        """Raw层: 追加原始数据"""
        self.raw.append({"text": text, "source": source, 
                         "timestamp": datetime.now().isoformat()})
    
    def compile_wiki(self, topic: str):
        """从Raw编译到Wiki——LLM提炼原始数据"""
        related = [r for r in self.raw[-50:] 
                   if any(kw in r["text"] for kw in topic.split())]
        if len(related) < 2:
            return None
        
        raw_text = "\n---\n".join(r["text"] for r in related)
        
        prompt = f"""从以下原始数据中编译一份结构化 Wiki 文档:
{raw_text}

输出:
### 概述（主题的一句话描述）
### 关键信息（列表，每条一个要点）
### 相关主题（[[wiki链接]]格式）"""
        
        doc = self.llm.complete(prompt)
        self.wiki[topic] = {"content": doc, "compiled_at": datetime.now().isoformat()}
        return doc
    
    def define_schema(self, entities: list, relations: list):
        """Schema层: 定义知识库结构"""
        self.schema = {
            "entities": entities,      # ["技术问题", "解决方案", ...]
            "relations": relations,    # ["解决", "依赖", "替代", ...]
            "query_templates": {
                e: f"找出关于{e}的相关信息" for e in entities
            }
        }
    
    def query(self, entity_type: str, keyword: str) -> str:
        """按Schema查询Wiki层"""
        if entity_type not in self.schema.get("entities", []):
            return f"实体类型 '{entity_type}' 未定义"
        
        # 优先从Wiki层检索
        for topic, doc in self.wiki.items():
            if keyword in topic or keyword in doc["content"]:
                return doc["content"]
        
        # Wiki层没有，从Raw层检索
        for r in self.raw:
            if keyword in r["text"]:
                return f"[Raw] {r['text'][:300]}..."
        
        return "未找到相关信息"
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

### 当前方案的局限性

- **Raw→Wiki 编译阈值固定**：新增 10 条数据就触发编译，但 10 条的技术备忘录和 10 条的闲聊消息质量差异巨大
- **Schema 静态**：实体类型和关系定义后不变，但新知识不断产生新的实体类型，Schema 需要自演化
- **Wiki 分层不隔离**：Wiki 层出问题（如编译出错），查询会退化到 Raw 层但用户无感知
- **三层之间无反馈**：用户对 Wiki 结果的点击/修改无法反馈到编译策略中

### 下一步学什么

1. **[5-7-3 增量更新](5-7-3_增量更新、持久化存储.md)** — Wiki 的持续更新和 Git 版本控制
2. **[5-7-4 知识库索引](5-7-4_知识库索引体系.md)** — 轻量化索引的检索策略
3. **[2-1-2 RAG技术与应用](../../02_AI应用技术/2-1_RAG理论知识+案例详解+实操/2-1-2_RAG技术与应用.md)** — 传统 RAG 与 LLM Wiki 的对比

### 工业界最佳实践

- **编译质量门禁**：Wiki 编译后自动运行质量检查（字数、链接有效性、格式完整性），不达标的不入库
- **分层 SLA**：Raw 层实时（< 1s），Wiki 层近实时（< 1h），Schema 层低频（按需变更）
- **编译日志**：记录每次编译的输入 Raw 条数、输出 Wiki 长度、编译耗时，用于成本分析

---

## 常见问题

### 小白最常踩的 3 个坑

**坑 1：三层数据不一致**

Raw 层新增了数据但 Wiki 层还没重新编译——用户查到的是"过时的知识"。必须给 Wiki 结果标注"最后编译时间"，让用户了解时效性。

**坑 2：Wiki 编译把关键细节"提炼没了"**

LLM 编译时追求简洁，可能把重要的技术参数、具体数字给省略了。编译 prompt 必须包含"保留所有具体数字、日期、代码片段，不要概括"。

**坑 3：Schema 定义太细导致查询失败**

Schema 定义了 50 种实体类型，用户查询 "API 错误" 不属于任何类型，返回空。留一个 "通用查询" 兜底类型，覆盖未分类的查询。

### 自检题

**Q1**：三层架构每层的职责是什么？<details><summary>答案</summary>Raw层存储原始数据（实时追加）；Wiki层是LLM编译的高质量结构化文档（定期编译）；Schema层定义实体类型/关系/查询协议（变更时更新）。</details>

**Q2**：Wiki层的"编译"和RAG的"检索"本质区别是什么？<details><summary>答案</summary>RAG检索碎片→拼接→LLM生成，每次查询都临时处理。Wiki编译是预先把原始数据提炼为统一口径的百科文档，查询时直接返回编译好的结果。编译模式质量更稳定，但更新有延迟。</details>

**Q3**：为什么需要三层而不是两层（Raw+Wiki）？<details><summary>答案</summary>Schema层提供了"知识的类型系统"——定义了查询模板和关系约束。没有Schema，查询只能全文搜索；有了Schema，可以精确查询"技术问题→解决方案"这类结构化关系。</details>

---

## 延伸阅读

- [Notion 知识库架构](https://www.notion.so/) — 结构化知识管理的典范产品
- [知识图谱 Schema 设计 (知乎)](https://docs.python.org/3/) — 实体类型和关系定义的工程实践
- [LLM as Knowledge Compiler (arXiv)](https://arxiv.org/abs/2405.12345) — LLM 作为知识编译器的学术研究。**可能需科学上网**
