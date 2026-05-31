# 5.5.3 Agent间通信 + 任务流闭环

> 5.5.3 Agent间通信+任务流闭环 > 5.5 Hermes多Agent > 5. 项目实战

## 核心概念

- **是什么**：Agent间通信是多Agent系统的"神经系统"——定义子任务间的依赖关系、数据传递方式、异常处理。任务流闭环确保每个任务输入有来源、输出有去处、异常有兜底。
- **为什么重要**：单Agent执行好≠整体成功。通信不畅会导致数据丢失、时序错乱、异常雪崩。

### 前置知识

- 建议先学 [2-2-2 Agent自主规划](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-2_Agent的自主规划与工具开发.md)、[5-4-1 心跳记忆](../5-4_搭建Hermes_Agent中的长期记忆和自进化能/5-4-1_心跳唤醒时，自主收集需要整理的记忆.md)。


## 原理讲解

### 1. 任务依赖图（DAG）

```
[任务1: 查询数据] ──┐
                    ├→ [任务3: 分析] → [任务4: 报告] → [任务5: 发邮件]
[任务2: 查询配置] ──┘
```

### 2. 异常处理矩阵

| 异常 | 策略 | 
|------|------|
| Agent 超时 | 重试1次 → 标记失败 |
| Agent 崩溃 | 降级方案 |
| 依赖失败 | 下游全部跳过 |
| 部分失败 | 成功的继续用 |


### 3. Agent 间通信与任务流

```
Master 下发 TaskMessage {task_id, payload, reply_to}
     ↓
子 Agent 执行 → ResultMessage {status, output, artifacts}
     ↓
DAG 调度器：depends_on 未满足则阻塞；失败 → retry / 通知 Master 重规划
```

**消息总线**：内存 Queue（单机）或 Redis Stream（分布式）；务必持久化 `task_id` 状态供 5-5-4 回收。

### 4. 闭环检查点

| 状态 | 含义 |
|------|------|
| pending | 已拆解未执行 |
| running | 子 Agent 执行中 |
| success / failed | 可进入汇总 |

## 代码实战

```python
# pip install — 本示例仅用 Python 3.10+ 标准库

"""Agent间通信 + DAG执行"""
import asyncio

class TaskFlow:
    def __init__(self, registry):
        self.registry = registry
    
    async def execute_dag(self, subtasks: list[dict]) -> dict:
        sorted_tasks = self._topological_sort(subtasks)
        results = {}
        
        for group in self._group_parallel(sorted_tasks):
            async def run_with_retry(task):
                agent = self.registry._agents.get(task["agent"])
                if not agent:
                    return {"id": task["id"], "error": "Agent不存在"}
                for attempt in range(2):
                    try:
                        result = await asyncio.wait_for(
                            agent.execute(task), timeout=30)
                        return {"id": task["id"], "result": result}
                    except asyncio.TimeoutError:
                        if attempt == 1:
                            return {"id": task["id"], "error": "超时"}
                    except Exception as e:
                        return {"id": task["id"], "error": str(e)}
            
            group_results = await asyncio.gather(*[run_with_retry(t) for t in group])
            for r in group_results:
                results[r["id"]] = r
        
        return self._aggregate(results)
    
    def _topological_sort(self, tasks):
        sorted_ids, remaining = [], list(tasks)
        while remaining:
            ready = [t for t in remaining
                    if all(d in sorted_ids for d in t.get("depends_on", []))]
            if not ready: break
            sorted_ids.extend(t["id"] for t in ready)
            remaining = [t for t in remaining if t not in ready]
        return [t for tid in sorted_ids for t in tasks if t["id"] == tid]
    
    def _group_parallel(self, sorted_tasks):
        groups, current, seen = [], [], set()
        for task in sorted_tasks:
            if set(task.get("depends_on", [])).issubset(seen):
                current.append(task)
            else:
                if current: groups.append(current)
                current = [task]
            seen.add(task["id"])
        if current: groups.append(current)
        return groups
    
    def _aggregate(self, results):
        succeeded = sum(1 for r in results.values() if "result" in r)
        failed = sum(1 for r in results.values() if "error" in r)
        return {"status": "completed" if not failed else "partial",
                "succeeded": succeeded, "failed": failed}
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

- **DAG 静态**：任务依赖图在拆分时确定，执行中不能动态调整。某个任务产出意外结果时，下游任务无法自适应
- **超时全局固定**：所有任务 30 秒超时，但简单查询和复杂分析的时间需求差异巨大
- **无优先级抢占**：所有任务平权，紧急任务（用户等待）和后台任务（定期清理）同优先级排队
- **通信协议简单**：Agent 间只传 JSON，不支持流式传输、二进制数据或大文件引用

### 下一步学什么

1. **[5-5-4 全局闭环](5-5-4_全局闭环系统——结果回收、状态同步、自进.md)** — 通信完成后如何复盘和自进化
2. **[2-2-3 Agent评估](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-3_Agent的能力优化与效果评估.md)** — 任务流执行效果的系统评估
3. **[A2A 协议](https://github.com/google/A2A)** — Google 的 Agent-to-Agent 标准通信协议

### 工业界最佳实践

- **消息持久化**：Agent 间通信消息写入消息队列（Redis/Kafka），防止进程重启丢消息
- **链路追踪**：每次任务流执行分配唯一 trace_id，记录每个 Agent 的输入/输出/耗时，用于事后排查
- **熔断降级**：某个 Agent 连续失败 3 次自动熔断，后续任务走降级路径

---

## 常见问题

### 小白最常踩的 3 个坑

**坑 1：循环依赖导致 DAG 永远跑不完**

任务A依赖任务B的结果，任务B又依赖任务A的结果——拓扑排序检测到循环依赖但只 break 不报错。应该在校验阶段就检测循环依赖并拒绝执行。

**坑 2：所有子任务完成后不验证整体一致性**

每个子任务各干各的，data_agent 查了 2025 年数据，analyst_agent 分析了 2024 年数据——两个对不上。闭环阶段必须验证输出的时间范围、数据口径等一致性。

**坑 3：不设全局超时，一个慢任务拖垮全流程**

DAG 最长路径上的任务串行耗时决定了总时间。应该设全局超时（如 5 分钟），超时后已完成的返回部分结果，未完成的标记超时。

### 自检题

**Q1**：DAG执行的核心算法是什么？<details><summary>答案</summary>拓扑排序：找出所有依赖已满足的任务→执行→标记完成→重复，直到所有任务完成或遇到循环依赖。</details>

**Q2**：四种异常分别怎么处理？<details><summary>答案</summary>超时重试1次后标记失败；崩溃记录+降级；依赖失败下游跳过；部分失败成功结果继续用。</details>

**Q3**：Agent 间通信和普通 HTTP 调用的最大区别是什么？<details><summary>答案</summary>Agent 通信不是单纯的数据传输，而是"带意图的协作"——消息中含有任务上下文、依赖关系、置信度等语义信息。目标不是"把数据传过去"，而是"共同完成一个任务"。</details>

---

## 延伸阅读

- [DAG 工作流引擎对比 (Airflow vs Prefect vs Temporal)](https://www.prefect.io/blog/prefect-vs-airflow) — 成熟的 DAG 执行引擎，理解其设计对 Agent 任务流有启发
- [Celery 分布式任务队列](https://docs.celeryq.dev/) — Python 最成熟的分布式任务框架，任务路由和异常处理的设计可参考
- [Agent 通信协议设计模式](https://github.com/AI-Interviews/LLM-Interview-Questions) — 社区整理的 Agent 通信与面试题
- [5-5-2 子Agent注册](5-5-2_子Agent分工、注册与执行机制.md) — 通信双方的能力注册表
- [5-5-4 全局闭环](5-5-4_全局闭环系统——结果回收、状态同步、自进.md) — 任务流结束后的回收与自进化
