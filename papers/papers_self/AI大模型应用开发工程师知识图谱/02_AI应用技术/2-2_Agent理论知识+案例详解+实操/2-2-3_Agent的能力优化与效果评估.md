# 2.2.3 Agent的能力优化与效果评估

> 2.2 Agent理论知识+案例详解+实操 > 2. AI应用技术

---

## 核心概念

### 如何让 Agent 越用越好

**一句话**：好的 Agent 不是"一次开发完就固定"——它通过收集用户反馈（显式+隐式），持续优化检索、规划和生成能力，越用越聪明。

```
第一版 Agent:     "能用"(60分) → 上线
收集反馈(1周):   定位问题 → Bad Case 分析
第二版 Agent:     "好用"(75分) → 更新
持续迭代:        越用越好(90分+)
```

**类比**：Agent 像一个实习生——第一周靠基础知识，但真正的成长来自师傅的反馈和错误纠正。

### 显式反馈 vs 隐式反馈

| 反馈类型 | 是什么 | 信号强度 | 数据量 | 例子 |
|---------|--------|:-------:|:------:|------|
| **显式反馈** | 用户主动表达满意/不满意 | 强（明确） | 少（<5%用户会反馈） | 👍/👎 点赞、评分、纠错 |
| **隐式反馈** | 从用户行为中推断 | 弱（需推断） | 多（所有用户都有） | 复制/删除回答、重复提问、停留时长 |

**两种反馈必须结合使用**：显式反馈是"黄金训练数据"（质高量少），隐式反馈是"大数据信号"（质低量大）。

### 什么是 Agent 效果评估

**一句话**：Agent 评估不再是简单的"回答对不对"——需要从检索能力、推理能力、工具使用能力多个维度量化 Agent 的综合表现。

### 前置知识

- Agent 基础（[2.2.1 Function Calling与MCP](2-2-1_Function_Calling与MCP.md)）
- RAG 评估（[2.1.4 RAG调优](../2-1_RAG理论知识+案例详解+实操/2-1-4_RAG调优.md)）
- RAG 基础知识（[2.1.2 RAG技术与应用](../2-1_RAG理论知识+案例详解+实操/2-1-2_RAG技术与应用.md)）

---

## 原理讲解

### 利用用户反馈优化 Agent 的三条路径

```
用户反馈
  │
  ├─→ 路径1: 优化 RAG 知识库
  │    反馈:"回答没找到XX相关信息"
  │    → 补充缺失的知识点 → 优化文档切分 → 调整检索策略
  │
  ├─→ 路径2: 优化 Prompt / 工具定义
  │    反馈:"Agent 没有调用正确的工具"
  │    → 优化工具描述 → 调整 System Prompt → 添加 Few-shot 示例
  │
  └─→ 路径3: 微调模型
       反馈: 大量 Bad Case 指向模型推理能力不足
       → 收集高质量轨迹 → SFT 微调 → RLHF 强化
```

### 隐式反馈信号解读

| 用户行为 | 可能的信号 | 置信度 |
|---------|-----------|:-----:|
| 复制回答内容 | 回答有用 | 中 |
| 立刻重新提问（修改措辞） | 第一次回答不满足 | 高 |
| 快速关闭对话 | 回答无用/错误 | 中 |
| 长时间停留后无操作 | 在阅读/疑惑 | 低 |
| 点赞后又撤销 | 回答有部分问题 | 中 |
| 追问"你确定吗？" | 用户怀疑答案正确性 | 高（负面） |

**关键**：单一隐式信号不可靠，需要多维交叉验证。例如：复制+点赞=高置信度有用；复制+立刻重新提问=回答部分有用但不完整。

### Agent 评估的三个维度

#### 1. 大海捞针（Needle in a Haystack）

测试 RAG Agent 能否在大量无关信息中找到关键信息：

```
测试: 在 100 篇文档中插入 1 条关键信息
问题: "公司2024年的营收是多少？"
只有 1 篇文档包含答案,其他 99 篇无关

评估: Agent 能否精准检索到那 1 条答案而不被噪音淹没
```

评测指标：
- 检索召回率：是否在所有文档中找到目标
- 答案准确度：长上下文中是否仍正确引用了关键信息
- "迷失中间"效应：关键信息在文档中间位置时是否会遗漏

#### 2. 多跳推理评估（Multi-Hop）

测试 Agent 能否综合多条分散信息进行推理：

```
测试: 答案需要从 2-3 篇不同文档中分别提取信息并推理

问题: "谁是公司资历最深的员工？他负责的项目预算总额是多少？"
  Hop 1: 查 employees 表 → 最早 join_date = 2018 → 钱七
  Hop 2: 查 projects 表 → lead_id=5 → 预算 800,000
  Answer: 钱七，800,000 元
```

评测重点：
- 能否分解多跳问题
- 能否从第一跳结果推导第二跳搜索
- 中间步骤是否可追溯（调试友好）

#### 3. 业务指标评估

| 指标 | 定义 | 计算方式 |
|------|------|---------|
| **任务完成率** | Agent 成功完成任务的占比 | 人工标注/用户确认 |
| **平均对话轮次** | 完成任务需要多少轮交互 | 轮次越少越好 |
| **工具选择准确率** | 选对了工具吗 | 对比最优工具 vs 实际调用 |
| **幻觉率** | 回答中有多少编造内容 | LLM 自动评估/人工抽查 |
| **用户留存率** | 用过后还会再用的比例 | 7日/30日留存 |

### 从反馈到优化的实践链路

```
1. 收集 → 自动采集所有对话 (query + answer + tool_calls + 用户行为)
2. 标注 → LLM 自动初筛 + 人工抽检确认
3. 分析 → 按失败模式聚类 (检索失败/工具选错/推理错误/幻觉)
4. 优化 → 针对最高频失败模式制定修复方案
5. 验证 → A/B 测试对比修复前后效果
6. 上线 → 灰度→全量，继续循环
```

---

## 代码实战

### 环境准备

```bash
pip install openai numpy
```

### 实战 1：用户反馈收集与分析

```python
"""Agent 反馈收集系统"""
import json
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class ConversationRecord:
    """单次对话记录"""
    query: str
    answer: str
    tool_calls: list
    explicit_feedback: Optional[str]  # "up"/"down"/None
    implicit_signals: dict            # {"copied": True, "re_asked": False, ...}
    timestamp: str

@dataclass
class FeedbackSystem:
    """反馈系统"""
    records: List[ConversationRecord] = field(default_factory=list)

    def record(self, query, answer, tool_calls,
               explicit=None, copied=False, re_asked=False):
        self.records.append(ConversationRecord(
            query=query, answer=answer, tool_calls=tool_calls,
            explicit_feedback=explicit,
            implicit_signals={"copied": copied, "re_asked": re_asked},
            timestamp=datetime.now().isoformat(),
        ))

    def analyze(self):
        """分析反馈数据"""
        total = len(self.records)
        if total == 0:
            return "暂无反馈数据"

        up = sum(1 for r in self.records if r.explicit_feedback == "up")
        down = sum(1 for r in self.records if r.explicit_feedback == "down")
        copied = sum(1 for r in self.records if r.implicit_signals.get("copied"))
        re_asked = sum(1 for r in self.records if r.implicit_signals.get("re_asked"))
        no_tools = sum(1 for r in self.records if not r.tool_calls)

        return {
            "总对话数": total,
            "显式点赞率": f"{up/max(total,1)*100:.1f}%",
            "显式点踩率": f"{down/max(total,1)*100:.1f}%",
            "隐式-复制率": f"{copied/max(total,1)*100:.1f}%",
            "隐式-重新提问率": f"{re_asked/max(total,1)*100:.1f}%",
            "未使用工具占比": f"{no_tools/max(total,1)*100:.1f}%",
            "Bad Case 数(点踩或重问)": down + re_asked,
        }

    def get_bad_cases(self):
        """提取 Bad Case"""
        bad = []
        for r in self.records:
            if r.explicit_feedback == "down" or r.implicit_signals.get("re_asked"):
                bad.append({
                    "query": r.query,
                    "answer": r.answer[:100],
                    "tools": [t.get("name") for t in r.tool_calls] if r.tool_calls else [],
                    "feedback": r.explicit_feedback,
                    "re_asked": r.implicit_signals.get("re_asked"),
                })
        return bad

# 演示
fs = FeedbackSystem()

# 模拟对话数据
fs.record("查天气", "北京晴天", [{"name": "get_weather"}],
          explicit="up", copied=True)
fs.record("查股票", "贵州茅台1680元", [{"name": "get_stock"}],
          explicit="up", copied=True)
fs.record("复杂的分析任务", "抱歉我无法完成...", [],
          explicit="down", re_asked=True)
fs.record("查数据库", "查询结果...", [{"name": "query_db"}],
          copied=True)
fs.record("多跳推理问题", "根据A和B...回答不够完整", [{"name": "search"}],
          re_asked=True)

print("=== 反馈分析 ===")
analysis = fs.analyze()
for k, v in analysis.items():
    print(f"  {k}: {v}")

print("\n=== Bad Cases ===")
for case in fs.get_bad_cases():
    print(f"  问题: {case['query']}")
    print(f"  回答: {case['answer']}...")
    print(f"  工具: {case['tools']}")
    print(f"  反馈: {case['feedback']}, 重问: {case['re_asked']}")
    print()
```

### 实战 2：大海捞针测试

```python
"""Agent 大海捞针测试"""
import random

def create_needle_haystack(num_docs=100, needle_pos=None):
    """
    生成测试数据: N 篇无关文档 + 1 篇关键信息
    needle_pos: 关键信息插入位置 (0=开头, 0.5=中间, 1.0=结尾)
    """
    # 无关文档（噪音）
    haystack = [
        f"文档{i}: 这是第{i}号文档，包含一些无关的{{占位}}信息。"
        f"本文档讨论了主题{{A}}和主题{{B}}的关系。"
        for i in range(num_docs)
    ]

    # 关键信息（针）
    needle = "文档_关键: 公司2024年度总营收为 12.8 亿元，同比增长 23.5%。"

    # 在指定位置插入
    if needle_pos is None:
        needle_pos = random.random()
    insert_idx = int(needle_pos * num_docs)
    haystack.insert(insert_idx, needle)

    return haystack, insert_idx, needle

def needle_haystack_test(retrieve_func, num_trials=10):
    """
    大海捞针测试：评估检索系统在不同位置找到关键信息的能力
    retrieve_func: 检索函数，接收 (query, documents) 返回 [(doc, score), ...]
    """
    positions = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
    results = {}

    for pos in positions:
        success = 0
        rank_list = []

        for _ in range(num_trials):
            docs, true_idx, needle = create_needle_haystack(100, pos)
            query = "公司2024年的营收是多少？"

            retrieved = retrieve_func(query, docs)

            # 检查关键文档是否被检索到
            found = False
            for rank, (doc, score) in enumerate(retrieved):
                if "文档_关键" in doc:
                    rank_list.append(rank + 1)  # 1-indexed
                    found = True
                    break
            if found:
                success += 1

        results[f"位置{pos:.0%}"] = {
            "召回率": f"{success}/{num_trials}",
            "平均排名": f"{sum(rank_list)/max(len(rank_list),1):.1f}",
        }

    return results

# 用简单 BM25 做检索演示
def simple_retrieve(query, documents):
    """简单的关键词检索（演示用）"""
    from rank_bm25 import BM25Okapi
    tokenized = [d.split() for d in documents]
    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(query.split())
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    return [(documents[idx], score) for idx, score in ranked[:10]]

# 运行测试
print("=== 大海捞针测试 ===")
try:
    results = needle_haystack_test(simple_retrieve, num_trials=5)
    for pos, result in results.items():
        print(f"  关键信息在{pos}: 召回={result['召回率']}, 平均排名={result['平均排名']}")
except ImportError:
    print("(需要 pip install rank_bm25)")
    print("\n测试逻辑说明:")
    print("  1. 生成100篇文档，其中1篇含关键信息")
    print("  2. 关键信息分别放在 0%/10%/25%/50%/75%/90%/100% 位置")
    print("  3. 测试检索系统在各位置能否找到关键信息")
    print("  4. 关注'迷失中间'效应: 中间位置(50%)通常最差")
```

### 实战 3：Agent 综合评估框架

```python
"""Agent 效果评估框架"""
from dataclasses import dataclass

@dataclass
class EvalCase:
    """评估用例"""
    query: str
    expected_tools: list     # 预期调用的工具
    expected_answer_contains: list  # 答案应包含的关键词
    is_multi_hop: bool = False  # 是否多跳推理

@dataclass
class EvalResult:
    tool_accuracy: float       # 工具选择准确率
    answer_completeness: float # 答案完整性
    multi_hop_success: float   # 多跳推理成功率(仅多跳用例)

# 评估用例集
EVAL_SET = [
    EvalCase(
        query="今天北京天气怎么样？",
        expected_tools=["get_weather"],
        expected_answer_contains=["温度", "天气"],
    ),
    EvalCase(
        query="技术部工资最高的是谁？他的入职日期是什么时候？",
        expected_tools=["query_database"],
        expected_answer_contains=["工资", "入职"],
        is_multi_hop=True,  # 需要两次数据库查询
    ),
    EvalCase(
        query="解释一下什么是机器学习",
        expected_tools=[],  # 不需要工具
        expected_answer_contains=["算法", "数据", "模型"],
    ),
]

def evaluate_agent(agent_func, eval_set):
    """评估 Agent 效果"""
    results = {"tool_accuracy": [], "answer_completeness": [],
               "multi_hop_pass": 0, "multi_hop_total": 0}

    for case in eval_set:
        # 调用 Agent
        response = agent_func(case.query)
        tools_used = response.get("tools_called", [])
        answer = response.get("answer", "")

        # 1. 工具选择准确率
        expected = set(case.expected_tools)
        actual = set(tools_used)
        if expected == set():  # 不应该调用工具
            results["tool_accuracy"].append(1.0 if not actual else 0.0)
        else:
            overlap = len(expected & actual)
            results["tool_accuracy"].append(
                overlap / max(len(expected), 1)
            )

        # 2. 答案完整性
        hits = sum(1 for kw in case.expected_answer_contains
                   if kw in answer)
        results["answer_completeness"].append(
            hits / max(len(case.expected_answer_contains), 1)
        )

        # 3. 多跳推理
        if case.is_multi_hop:
            results["multi_hop_total"] += 1
            if hits == len(case.expected_answer_contains):
                results["multi_hop_pass"] += 1

    return {
        "工具选择准确率": f"{sum(results['tool_accuracy'])/max(len(results['tool_accuracy']),1)*100:.1f}%",
        "答案完整性": f"{sum(results['answer_completeness'])/max(len(results['answer_completeness']),1)*100:.1f}%",
        "多跳推理成功率": f"{results['multi_hop_pass']}/{results['multi_hop_total']}"
        if results['multi_hop_total'] > 0 else "无多跳用例",
    }

print("=== Agent 评估框架 ===")
print(f"评估用例数: {len(EVAL_SET)}")
print(f"多跳推理用例: {sum(1 for c in EVAL_SET if c.is_multi_hop)}")
print(f"需工具调用用例: {sum(1 for c in EVAL_SET if c.expected_tools)}")
print("\n评估维度:")
print("  1. 工具选择准确率 - Agent 是否正确选择了工具")
print("  2. 答案完整性 - 回答是否包含所有关键信息")
print("  3. 多跳推理成功率 - 多步推理任务是否完成")
```

---

### 预期输出

运行上述代码后，终端应看到类似以下结果（具体数值因环境与输入而异）：

```
（示例）关键日志/打印行出现，且无 Traceback
任务状态: success
耗时: <N> ms
```

若报错，优先检查：依赖是否安装、API Key/本地服务是否可用、路径与 Python 版本是否匹配。

## 进阶方向

### Agent 评估的挑战

| 挑战 | 说明 | 缓解方案 |
|------|------|---------|
| **评估标准主观** | "好回答"难以精确定义 | 多维度评估 + 人工校准 |
| **长尾场景覆盖** | 测试集难以覆盖所有真实场景 | 线上监控 + Bad Case 持续补充 |
| **评估成本高** | LLM 自动评估也需要 API 费用 | 分层评估: 规则→小模型→大模型 |
| **分数膨胀** | LLM 评估 LLM 容易"放水" | 多人/多模型交叉验证 |

### 反馈驱动的持续优化循环

```
线上 Agent
  → 收集所有对话(自动)
  → 每日 Bad Case 分析(LLM 自动分类 + 人工抽查)
  → 每周优化迭代(聚焦 Top-3 失败模式)
  → 灰度验证 → 全量上线
  → 回到第一步，循环
```

### 后续学习路径

- [2.2.4 Harness Engineering](2-2-4_Harness_Engineering.md) — 系统化的工具集管理
- [2.3.1 LLM微调原理](../2-3_模型训练与微调理论知识+案例详解+实操/2-3-1_LLM微调原理.md) — 用反馈数据做模型微调
- [2.1.4 RAG调优](../2-1_RAG理论知识+案例详解+实操/2-1-4_RAG调优.md) — RAG 系统评估和调优

---

## 常见问题

### 小白最常踩的 3 个坑

1. **只看显式反馈，忽略隐式反馈**
   - 错误：只有点赞/点踩数据，但量太少（<5%），结论不可靠
   - 正确：隐式反馈（复制、重问、停留）虽然不是 100% 准确，但数据量是显式的 20 倍，做趋势分析足够

2. **评估集和真实场景脱节**
   - 错误：评估用例全是"理想问题"（语法完整、意图明确），线上用户输入却是"v3怎么样""那它呢"
   - 正确：评估集直接从线上日志采样，保留真实用户的模糊、省略、口语化表达

3. **用单一指标衡量 Agent**
   - 错误：只看"答案准确率"，忽略了工具选择错误、推理步骤不可追溯等问题
   - 正确：至少用 3 个维度（检索/推理/工具使用），综合判断 Agent 表现

### 自检题

**Q1**：一个用户复制了 Agent 的回答，但 10 秒后又重新问了同一个问题（改了措辞）。这个隐式信号说明了什么？

> **答案**：复制说明回答有一定价值（用户想保存），但重新提问说明回答不完整或不够精确（用户觉得第一次回答没解决问题）。可能是回答太笼统，或缺少用户真正需要的细节。这种"部分有用但不完整"的 Bad Case 最容易被忽略。

**Q2**：大海捞针测试中，"迷失中间"效应是什么？为什么它很重要？

> **答案**："迷失中间"指长上下文模型中，在上下文窗口中间位置的信息更容易被模型忽略或遗漏，而开头和结尾的信息更容易被注意到。这很重要因为大多数人在填资料时会把重要信息放在中间（按时间或逻辑顺序），如果 RAG 系统检索到的关键文档恰好被放在了 Prompt 的中间位置，Agent 可能会漏掉它。

**Q3**：多跳推理评估和普通 RAG 评估有什么本质不同？

> **答案**：普通 RAG 评估只需判断"检索到了→回答了"（单步），多跳评估需要验证"第一步推理结果是否正确引导了第二步"。如果 Agent 跳过了第一步直接猜了答案，即使答案碰巧正确也不算通过。多跳评估的核心是**推理链路是否完整可追溯**，而不仅仅是最终答案是否正确。

---

## 延伸阅读

### 中文资料（推荐，无需科学上网）

- [Needle in a Haystack 测试工具](https://github.com/gkamradt/LLMTest_NeedleInAHaystack) — 大海捞针测试开源实现
- [Agent 评估方法综述 - 知乎](https://docs.python.org/3/) — Agent 各维度评估方法总结
- [RAGAS 评估框架](https://docs.ragas.io/) — RAG/RAG Agent 专业评估框架

### 英文资料（可能需科学上网）

- [LangSmith 评估平台](https://docs.smith.langchain.com/evaluation) — LangChain 官方的 LLM 应用评估工具
- [AgentBench](https://github.com/THUDM/AgentBench) — 清华开源的 Agent 综合评测基准
- [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html) — 伯克利 Function Calling 能力排行榜
