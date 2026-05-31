# 5.5.1 主Agent核心能力——意图拆解、任务分发、权限管控

> 5.5.1 主Agent核心能力 > 5.5 Hermes多Agent > 5. 项目实战

## 核心概念

- **是什么**：主Agent（Orchestrator）是多Agent系统的"大脑"——接收用户指令后拆解为原子子任务，分发给最合适的子Agent执行，并控制各Agent的权限边界。
- **为什么重要**：没有主Agent的统一调度，多Agent系统会变成"各自为战"的混乱局面。

### 前置知识

- 建议先学 [2-2-2 Agent自主规划](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-2_Agent的自主规划与工具开发.md)、[5-4-1 心跳记忆](../5-4_搭建Hermes_Agent中的长期记忆和自进化能/5-4-1_心跳唤醒时，自主收集需要整理的记忆.md)。


## 原理讲解

### 1. 任务拆解——复杂任务 → 原子子任务

```
用户: "帮我分析销售数据，生成报告，发邮件给团队"
   ↓ 主Agent拆解
子任务1: 查询销售数据库 → data_agent
子任务2: 数据分析+可视化 → analyst_agent
子任务3: 生成Markdown报告 → writer_agent
子任务4: 发送邮件 → email_agent
```

拆解原则：每个子任务是**原子操作**（单一Agent可独立完成）+ 明确输入/输出。

### 2. 智能分发策略

| 任务类型 | 策略 | 示例 |
|---------|------|------|
| 轻任务（<10s） | 主Agent本地串行 | 简单查询、格式转换 |
| 重任务（>10s） | 抛给后台子Agent | 数据分析、LLM推理 |
| 独立任务 | 并行分发 | 同时查3个数据源 |
| 依赖任务 | 串行分发 | 分析依赖查询结果 |

### 3. 上下文分发——最小闭环

发给子Agent的不是全部上下文，而是完成任务**必要且充分**的信息（500-1500 token）：任务描述 + 相关数据 + 工具说明。

### 4. Hermes 主Agent 在系统中的位置

```
用户请求 + [5-4-4 唤醒的记忆摘要]
        ↓
┌───────────────────┐
│  MasterAgent      │  decompose → 校验子Agent能力 → 构建最小上下文
│  (Orchestrator)   │
└─────────┬─────────┘
          │ dispatch
    ┌─────┴─────┬─────────────┐
    ▼           ▼             ▼
 data_agent  analyst_agent  writer_agent  …（见 5-5-2 注册表）
```

主 Agent **不直接执行业务工具**，只做规划与调度；工具调用在子 Agent 内完成（见 5-5-2）。

### 5. 权限管控矩阵（示例）

| 数据域 | data_agent | writer_agent | 说明 |
|--------|:----------:|:------------:|------|
| 业务数据库只读 | ✅ | ❌ | 分析类任务 |
| 用户对话历史 | ✅ | ✅ | 写报告需上下文 |
| 系统配置/密钥 | ❌ | ❌ | 仅主进程可读 |

拆解 JSON 中增加 `required_scopes` 字段，分发前校验子 Agent 是否具备对应 scope。

### 6. 拆解结果 JSON Schema（Hermes 约定）

```json
{
  "subtasks": [
    {
      "id": 1,
      "agent": "data",
      "description": "查询近30天销售汇总",
      "input": "table=sales, range=30d",
      "output": "csv_path",
      "depends_on": [],
      "required_scopes": ["db.read"]
    }
  ]
}
```

## 代码实战

```python
# pip install — 本示例仅用 Python 3.10+ 标准库，无需额外安装

"""主Agent——任务拆解与智能分发（Hermes 简化版）"""
import asyncio
import json


class MockLLM:
    def complete(self, prompt: str) -> str:
        return json.dumps({
            "subtasks": [
                {"id": 1, "description": "查询销售库", "agent": "data",
                 "input": "sales_30d", "output": "rows", "depends_on": []},
                {"id": 2, "description": "生成周报", "agent": "writer",
                 "input": "rows", "output": "md", "depends_on": [1]},
            ]
        })


class MockSubAgent:
    async def execute(self, ctx: str) -> str:
        await asyncio.sleep(0.05)
        return f"done:{ctx[:30]}"


class MasterAgent:
    def __init__(self, llm, sub_agents: dict):
        self.llm = llm
        self.sub_agents = sub_agents  # {name: agent_instance}
    
    def decompose(self, user_task: str) -> list[dict]:
        prompt = f"""将任务拆解为原子子任务，输出 JSON:
{{"subtasks": [{{"id":1, "description":"...", "agent":"data|analyst|writer",
 "input":"...", "output":"...", "depends_on":[]}}]}}
任务: {user_task}"""
        return json.loads(self.llm.complete(prompt))["subtasks"]
    
    def build_minimal_context(self, subtask: dict) -> str:
        return f"任务: {subtask['description']}\n输入: {subtask.get('input','')}"
    
    async def execute(self, user_task: str) -> dict:
        subtasks = self.decompose(user_task)
        independent = [s for s in subtasks if not s.get("depends_on")]
        dependent = [s for s in subtasks if s.get("depends_on")]
        
        async def run(st):
            agent = self.sub_agents.get(st["agent"])
            return {"id": st["id"], "result": await agent.execute(self.build_minimal_context(st))}
        
        results = {}
        for r in await asyncio.gather(*[run(s) for s in independent]):
            results[r["id"]] = r
        for st in dependent:
            results[st["id"]] = await run(st)
        return results


async def _demo():
    master = MasterAgent(MockLLM(), {"data": MockSubAgent(), "writer": MockSubAgent()})
    out = await master.execute("分析销售并写周报")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(_demo())
```

### 预期输出

```
{
  "1": {"id": 1, "result": "done:任务: 查询销售库\n输入: sales_30d"},
  "2": {"id": 2, "result": "done:任务: 生成周报\n输入: rows"}
}
```

子任务 2 在 1 完成后执行，体现 `depends_on` 串行逻辑。

若报错，优先检查：依赖是否安装、API Key/本地服务是否可用、路径与 Python 版本是否匹配。

## 进阶方向

### 当前方案的局限性

- **拆解粒度固定**：当前拆解策略对所有任务同一粒度，简单任务过度拆解浪费调度开销
- **无动态重规划**：子任务执行失败后主Agent不会自动调整计划，缺少"Plan B"
- **权限模型简单**：当前只有基本的 Agent 能力匹配，缺少细粒度的数据访问权限控制
- **无负载感知**：不感知子Agent当前负载，可能把任务发给已经满载的Agent

### 下一步学什么

1. **[5-5-2 子Agent注册](5-5-2_子Agent分工、注册与执行机制.md)** — 子Agent如何注册和被主Agent发现
2. **[5-5-3 Agent间通信](5-5-3_Agent间通信_+_任务流闭环.md)** — DAG依赖和任务流闭环
3. **[2-2-2 Agent自主规划](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-2_Agent的自主规划与工具开发.md)** — 更通用的Agent规划框架

### 工业界最佳实践

- **任务优先级队列**：用户直接触发的任务高优先级，后台分析类任务低优先级
- **拆解结果缓存**：相似任务（如"分析本月销售数据"和"分析上月销售数据"）复用拆解模板，减少 LLM 调用
- **并发上限控制**：设置最大并行子任务数（如 5），防止瞬间创建 50 个子任务撑爆系统

---

## 常见问题

### 小白最常踩的 3 个坑

**坑 1：拆解太细，调度开销比执行时间还大**

一个 2 秒完成的查询被拆成 3 个子任务，调度+通信花了 5 秒，得不偿失。简单任务（< 5s）应该主Agent自己串行执行，别拆分。

**坑 2：忘了处理子Agent不存在或不可用的情况**

用户说"生成视频"，但系统里没有 video_agent。如果 decompose 阶段不做能力检查，任务拆出来了但没人能执行，用户干等着超时。

**坑 3：权限管控只靠 Agent 名称匹配**

把敏感数据（如工资表）发给 data_agent 没问题，但 data_agent 不应该有权访问用户密码。权限应该是列级/表级，不是 Agent 级。

### 自检题

**Q1**：任务拆解的原则是什么？<details><summary>答案</summary>每个子任务是原子操作（单一Agent可完成）、有明确输入/输出、有可验证完成标准。</details>

**Q2**：什么任务该并行，什么该串行？<details><summary>答案</summary>无依赖关系的任务并行执行（如同时查多个数据源）。有依赖关系的任务串行（如分析必须等查询完成）。</details>

**Q3**：Hermes 主 Agent 和单 Agent + 很多工具有什么区别？<details><summary>答案</summary>单 Agent 在一个上下文里轮流调工具，上下文易膨胀、职责不清。主 Agent 只做规划分发，子 Agent 各自维护工具集与权限，适合多领域、长链路、需隔离故障的企业场景。</details>

## 延伸阅读

- [Agent自主规划](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-2_Agent的自主规划与工具开发.md)
- [5-5-2 子Agent注册](5-5-2_子Agent分工、注册与执行机制.md) — 主 Agent 拆解后的执行单元
- [5-5-3 Agent间通信](5-5-3_Agent间通信_+_任务流闭环.md) — 任务流与 DAG 闭环
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — 多 Agent 编排的工程实践（可能需科学上网）
- [2-2-4 Harness Engineering](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-4_Harness_Engineering.md) — Agent 基础设施与编排的工程化方法

> 建议学习顺序：5-5-1 → 5-5-2 → 5-5-3 → 5-5-4，每节动手跑通示例后再进入下一节。

<!-- 节点 5-5-1 学习路径锚点 -->
