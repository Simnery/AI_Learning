# 5.5.2 子Agent分工、注册与执行机制

> 5.5.2 子Agent分工注册与执行 > 5.5 Hermes多Agent > 5. 项目实战

## 核心概念

- **是什么**：子Agent是执行具体任务的"专家"。每个子Agent有明确的角色（数据分析师/写手/邮件助手）、技能清单（能做什么）、注册信息（如何被主Agent发现和调用）。
- **为什么重要**：注册机制让系统可扩展——新增一种能力只需注册一个新的子Agent，主Agent自动发现并调度。

### 前置知识

- 建议先学 [2-2-2 Agent自主规划](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-2_Agent的自主规划与工具开发.md)、[5-4-1 心跳记忆](../5-4_搭建Hermes_Agent中的长期记忆和自进化能/5-4-1_心跳唤醒时，自主收集需要整理的记忆.md)。


## 原理讲解

### 1. 子Agent注册信息

```
注册信息 = {
  name: "data_agent",
  description: "负责数据库查询和数据处理",
  capabilities: ["sql_query", "data_transform", "export_csv"],
  input_schema: {query: str, params: dict},
  output_schema: {data: list, metadata: dict}
}
```

### 2. 标准执行流程

```
收到任务 → 验证输入 → 执行核心逻辑 → 验证输出 → 返回结果
              ↓失败                  ↓失败
          返回错误              返回错误+重试
```


### 3. 子 Agent 注册表（Hermes）

```python
REGISTRY = {
  "data": {"tools": ["sql_query"], "scopes": ["db.read"], "timeout": 30},
  "writer": {"tools": ["save_md"], "scopes": ["fs.write"], "timeout": 60},
}
```

主 Agent 拆解时 `agent` 字段必须在 REGISTRY 中存在，否则 **降级** 为「主 Agent 本地执行」或拒绝任务。

### 4. 执行隔离

每个子 Agent 独立：工具白名单、最大 token、独立错误栈；崩溃不拖垮主进程（子进程/容器可选）。

## 代码实战

```python
# pip install — 本示例仅用 Python 3.10+ 标准库

"""子Agent注册与执行机制"""
import uuid
from abc import ABC, abstractmethod
from datetime import datetime

class AgentRegistry:
    def __init__(self):
        self._agents = {}
    
    def register(self, agent):
        self._agents[agent.name] = agent
    
    def list_agents(self) -> list[dict]:
        return [{"name": a.name, "description": a.description,
                 "capabilities": a.capabilities} for a in self._agents.values()]
    
    def find_by_capability(self, cap: str) -> list:
        return [a for a in self._agents.values() if cap in a.capabilities]

class BaseAgent(ABC):
    def __init__(self, name: str, description: str, capabilities: list[str]):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.required_inputs = []
    
    def validate_input(self, task: dict) -> bool:
        return all(k in task for k in self.required_inputs)
    
    @abstractmethod
    async def execute(self, task: dict) -> dict:
        pass
    
    def format_result(self, data, success: bool, error: str = "") -> dict:
        return {"agent": self.name, "task_id": str(uuid.uuid4()),
                "success": success, "data": data, "error": error,
                "timestamp": datetime.now().isoformat()}

# 具体子Agent
class DataAgent(BaseAgent):
    def __init__(self):
        super().__init__("data_agent", "数据库查询和数据处理",
                        ["sql_query", "data_transform"])
        self.required_inputs = ["query"]
    
    async def execute(self, task: dict) -> dict:
        if not self.validate_input(task):
            return self.format_result(None, False, "缺少必要参数 query")
        result = f"查询: {task['query'][:50]}..."
        return self.format_result(result, True)

# 使用
registry = AgentRegistry()
registry.register(DataAgent())
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

- **注册信息静态**：Agent 注册后能力和 schema 不变，但实际能力可能随时间退化或增强
- **无版本管理**：同一 Agent 升级后新旧版本的能力差异未体现在注册信息中
- **依赖硬编码**：Agent 的 required_inputs 写死在代码里，新增输入字段需要改代码重新部署
- **缺乏健康检查**：Agent 注册后没有定期探活，主Agent可能在调度时才发现 Agent 已死

### 下一步学什么

1. **[5-5-3 Agent间通信](5-5-3_Agent间通信_+_任务流闭环.md)** — 注册好的 Agent 如何协作通信
2. **[5-5-4 全局闭环](5-5-4_全局闭环系统——结果回收、状态同步、自进.md)** — Agent 执行结果的回收和自进化
3. **[2-2-4 Harness Engineering](../../02_AI应用技术/2-2_Agent理论知识+案例详解+实操/2-2-4_Harness_Engineering.md)** — Agent 基础设施设计的系统方法论

### 工业界最佳实践

- **能力发现协议**：Agent 启动时主动向 Registry 注册，关闭时主动注销，支持热插拔
- **能力版本标签**：注册信息中包含 `version` 字段，主Agent 可以根据版本选择合适的 Agent
- **负载上报**：子Agent 定期上报当前队列长度和平均执行时间，供主Agent 做负载均衡

---

## 常见问题

### 小白最常踩的 3 个坑

**坑 1：Agent 注册了但没实现抽象方法**

继承 BaseAgent 后忘了实现 `execute` 方法，Python 不会报错直到真正调用时才抛出 NotImplementedError。应该写单元测试验证每个 Agent 实例化后 `execute` 可正常调用。

**坑 2：Agent 的 capabilities 描述太模糊**

"数据分析"太宽泛。应该细化为 `["sql_query", "pandas_transform", "matplotlib_chart", "csv_export"]`。主Agent 靠 capabilities 做精确匹配，模糊的描述会导致错误调度。

**坑 3：验证逻辑太松或太紧**

太松：接受空参数执行，结果无意义。太紧：拒绝合理的默认值，导致可用性差。验证应该区分"必需参数"（缺了就报错）和"可选参数"（缺了用默认值）。

### 自检题

**Q1**：子Agent注册包含哪些关键信息？<details><summary>答案</summary>名称、描述、能力清单（capabilities）、输入/输出schema。主Agent通过这些信息完成"能力发现→任务匹配→调度执行"。</details>

**Q2**：执行流程中两次验证的目的分别是什么？<details><summary>答案</summary>执行前验证输入确保任务可执行（必要参数齐全），执行后验证输出确保结果符合预期格式。任一失败返回明确错误信息，方便主Agent处理。</details>

**Q3**：为什么 Agent 需要注册机制而不直接硬编码？<details><summary>答案</summary>注册机制支持热插拔——新增/移除 Agent 无需修改主Agent代码。系统可以在运行时动态发现可用能力，根据任务需求自动匹配最合适的 Agent。</details>

---

## 延伸阅读

- [Agent Protocol 标准 (A2A)](https://github.com/google/A2A) — Google 提出的 Agent-to-Agent 交互协议
- [LangGraph Agent 注册与调度](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/) — 多 Agent 注册和调度的框架实现。**可能需科学上网**
- [微服务注册中心设计模式](https://microservices.io/patterns/service-registry.html) — 借鉴微服务的注册发现模式，用于 Agent 管理
