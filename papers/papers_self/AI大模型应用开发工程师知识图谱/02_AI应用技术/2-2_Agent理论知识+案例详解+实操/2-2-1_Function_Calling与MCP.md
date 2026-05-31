# 2.2.1 Function Calling与MCP

> 2.2 Agent理论知识+案例详解+实操 > 2. AI应用技术

---

## 核心概念

### 什么是 Function Calling

**一句话**：Function Calling 让 LLM 可以"使用工具"——模型不是直接回答，而是输出一个"调用函数"的指令，由外部代码执行后，再把结果传回模型。

```
没有 Function Calling:
  用户: "北京今天天气怎么样"
  LLM: "抱歉，我的训练数据截止到..."（不知道实时信息）

有 Function Calling:
  用户: "北京今天天气怎么样"
  LLM: → 调用 get_weather("北京") 
  系统: → 执行函数，获取实时天气
  LLM: "北京今天晴，18-25℃" （基于真实数据回答）
```

**类比**：LLM 是大脑，Function Calling 是给它装上的"手"——大脑决定要做什么，手指去操作外部世界（查天气、查数据库、发邮件）。

### Function Calling 的工作流程

```
1. 用户提问 → LLM 分析是否需要调用函数
2. 需要 → LLM 输出 JSON: { "function": "get_weather", "arguments": {"city": "北京"} }
3. 系统 → 执行真实函数 → 拿到结果
4. 结果 + 原问题 → 再次给 LLM → 生成最终回答
```

### Function Calling vs MCP：什么区别

| 维度 | Function Calling | MCP (Model Context Protocol) |
|------|:----------------:|:----------------------------:|
| 是什么 | LLM 的内置能力（"会用手"） | 工具调用的**标准协议**（"手和工具的接口标准"） |
| 谁定义的 | 模型厂商（OpenAI/DeepSeek 各自实现） | Anthropic 开源协议，跨模型通用 |
| 连接方式 | 代码中硬编码函数定义 | Server-Client 架构，即插即用 |
| 生态 | 每个工具要自己写集成代码 | 社区有现成的 MCP Server 可复用 |
| 类比 | 手机内置功能 | USB-C 接口——统一标准，任何设备都能接 |

**关系**：MCP 是 Function Calling 的"标准化版本"。Function Calling 是能力，MCP 是让这个能力跨平台复用的协议。

### 什么是 MCP

MCP 有三层角色：

```
┌─────────────────────────────────────────┐
│  MCP Host (如 Claude Desktop, Cursor)   │
│  "用户用的应用程序"                      │
└──────────────┬──────────────────────────┘
               │ 连接多个
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐ ┌──────────────┐
│ MCP Client   │ │ MCP Client   │
│ (内置在Host) │ │              │   "协议层，负责通信"
└──────┬───────┘ └──────┬───────┘
       │                │
       ▼                ▼
┌──────────────┐ ┌──────────────┐
│ MCP Server   │ │ MCP Server   │
│ (天气服务)    │ │ (数据库服务)  │  "实际干活的"
└──────────────┘ └──────────────┘
```

### A2A（Agent-to-Agent）：Agent 之间的"对话协议"

A2A 让多个 Agent 互相通信和协作：

```
用户: "帮我做一份AI行业分析报告"

Coordinator Agent:
  ├→ 研究 Agent: "搜索 2024 AI 行业数据" → 返回数据
  ├→ 分析 Agent: "分析这些数据中的趋势" → 返回分析
  └→ 写作 Agent: "将分析写成报告" → 返回报告

MCP = 模型 ↔ 工具的通信协议
A2A = 模型 ↔ 模型的通信协议
```

### 前置知识

- 理解 API 调用基础（[1.2.1 AI大模型基本原理及API使用](../../01_AI大模型基础/1-2_实操基础/1-2-1_AI大模型基本原理及API使用.md)）
- Agent 基本概念（[2.2.2 Agent的自主规划与工具开发](2-2-2_Agent的自主规划与工具开发.md)）

---

## 原理讲解

### Function Calling 的底层原理

当 LLM 收到 Function Calling 请求时，实际发生了什么：

```
1. Prompt 中注入函数定义
   System: "你可以使用以下工具:
     - get_weather(city: str): 获取城市天气
     - search_database(query: str): 查询数据库"

2. LLM 输出特殊 token
   普通输出: "今天天气不错"
   FC 输出: <function_call>{"name":"get_weather","arguments":{"city":"北京"}}</function_call>

3. 系统拦截 function_call token
   不展示给用户，而是执行实际函数

4. 函数结果注入对话
   System: "get_weather 返回: 晴, 18-25℃"

5. LLM 继续生成
   "北京今天晴天，气温18到25度，适合出行。"
```

**关键**：LLM 本身不执行函数——它只是输出"我想调用这个函数"的 JSON，由你的代码去实际调用并传回结果。

### MCP 的核心机制

一个 MCP Server 暴露三个基本能力：

| 能力 | 说明 | 例子 |
|------|------|------|
| **Resources** | 暴露数据文件 | "读取 ./data/weather.csv" |
| **Tools** | 可调用的函数 | "查询数据库"、"抓取网页" |
| **Prompts** | 预定义的提示模板 | "旅游攻略生成模板" |

**MCP 的通信流程**：

```
MCP Client → MCP Server:
  {"jsonrpc": "2.0", "method": "tools/list"}

MCP Server → MCP Client:
  {"tools": [
    {"name": "get_weather", "description": "获取天气", "inputSchema": {...}},
    {"name": "fetch_web", "description": "抓取网页", "inputSchema": {...}}
  ]}

MCP Client → MCP Server:
  {"jsonrpc": "2.0", "method": "tools/call", "params": {
    "name": "fetch_web", "arguments": {"url": "https://example.com"}}}

MCP Server → MCP Client:
  {"content": [{"type": "text", "text": "网页内容..."}]}
```

### Agent2Agent（A2A）协议

A2A 解决的是：多个 Agent 之间如何互相"委托任务"和"汇报结果"。

```
A2A 四个核心概念:
  - Agent Card: Agent 的"名片"——我能做什么，怎么联系我
  - Task: 委托的任务对象，有唯一 ID 和状态
  - Message: Agent 间的通信格式
  - Artifact: 任务产出的成果（文档、代码、数据等）

A2A vs MCP 核心区别:
  MCP: "工具怎么用"（工具接口标准化）
  A2A: "Agent 怎么协作"（Agent 间通信标准化）
  互补关系: MCP 管工具层，A2A 管协作层
```

---

## 代码实战

### 环境准备

```bash
pip install openai mcp  # mcp 是 MCP SDK
```

### 实战 1：OpenAI Function Calling（天气查询）

```python
"""最简 Function Calling: 让 LLM 调用天气函数"""
import json
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.deepseek.com",  # DeepSeek 兼容 OpenAI FC 格式
)

# 1. 定义函数 Schema
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的实时天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如 北京、上海"
                }
            },
            "required": ["city"]
        }
    }
}]

# 2. 实际的天气函数（模拟）
def get_weather(city):
    weather_data = {
        "北京": "晴，18-25℃，北风3级",
        "上海": "多云，22-28℃，东南风2级",
        "深圳": "阵雨，25-30℃，南风4级",
    }
    return weather_data.get(city, f"未找到{city}的天气数据")

# 3. 调用 LLM，让它决定是否调用函数
messages = [{"role": "user", "content": "北京今天天气怎么样？适合出门吗？"}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
    tool_choice="auto",  # auto=模型自己决定要不要调; none=不调; required=必须调
)

# 4. 检查模型是否要调用函数
msg = response.choices[0].message

if msg.tool_calls:
    # 模型要调函数
    tool_call = msg.tool_calls[0]
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)

    print(f"LLM 决定调用: {func_name}({func_args})")

    # 执行函数
    result = get_weather(**func_args)
    print(f"函数返回: {result}")

    # 把函数结果发回给 LLM
    messages.append(msg)  # LLM 的 tool_call 消息
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result,
    })

    # LLM 基于函数结果生成最终回答
    final_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )
    print(f"\n最终回答: {final_response.choices[0].message.content}")
else:
    # 模型直接回答（不需要调函数）
    print(f"直接回答: {msg.content}")

# 预期输出:
# LLM 决定调用: get_weather({'city': '北京'})
# 函数返回: 晴，18-25℃，北风3级
# 最终回答: 北京今天晴天，气温18到25度，北风3级，非常适合出门。
```

### 实战 2：Function Calling 查询数据库

```python
"""用 Function Calling 让 LLM 查询 SQLite 数据库"""
import sqlite3
import json
from openai import OpenAI

# 准备数据库
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE employees (id INT, name TEXT, dept TEXT, salary INT)")
conn.execute("INSERT INTO employees VALUES (1,'张三','技术部',30000)")
conn.execute("INSERT INTO employees VALUES (2,'李四','市场部',25000)")
conn.execute("INSERT INTO employees VALUES (3,'王五','技术部',35000)")
conn.commit()

def query_database(sql):
    """执行 SQL 查询并返回结果"""
    try:
        cur = conn.execute(sql)
        columns = [d[0] for d in cur.description]
        rows = cur.fetchall()
        return json.dumps({"columns": columns, "rows": rows}, ensure_ascii=False)
    except Exception as e:
        return f"SQL 错误: {e}"

# 定义数据库查询工具
tools = [{
    "type": "function",
    "function": {
        "name": "query_database",
        "description": "执行 SQL 查询数据库。数据库有 employees 表(id, name, dept, salary)",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "SQL 查询语句"}
            },
            "required": ["sql"]
        }
    }
}]

client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.deepseek.com",
)

# 自然语言问数据库
messages = [{"role": "user", "content": "技术部员工的平均工资是多少？谁工资最高？"}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
)

msg = response.choices[0].message
if msg.tool_calls:
    tool_call = msg.tool_calls[0]
    sql = json.loads(tool_call.function.arguments)["sql"]
    print(f"LLM 生成的 SQL: {sql}")

    result = query_database(sql)
    print(f"查询结果: {result}")

    messages.append(msg)
    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

    final = client.chat.completions.create(model="deepseek-chat", messages=messages)
    print(f"\n回答: {final.choices[0].message.content}")

conn.close()
```

### 实战 3：搭建一个 MCP Server

```python
"""从零搭建 MCP Server: 旅游攻略服务"""
# 安装: pip install mcp

# ===== server.py (MCP Server 端) =====
server_code = '''
import json
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities
from mcp.server.stdio import stdio_server

# 创建 MCP Server
server = Server("travel-guide")

# 模拟的旅游数据
TRAVEL_DATA = {
    "北京": {"景点": ["故宫", "长城", "颐和园"], "美食": ["烤鸭", "炸酱面"], "最佳季节": "9-10月"},
    "上海": {"景点": ["外滩", "迪士尼", "豫园"], "美食": ["小笼包", "生煎"], "最佳季节": "3-5月, 9-11月"},
}

@server.list_tools()
async def list_tools():
    """告诉客户端我能提供什么工具"""
    return [
        {"name": "get_travel_info",
         "description": "获取城市旅游攻略",
         "inputSchema": {
             "type": "object",
             "properties": {
                 "city": {"type": "string", "description": "城市名称"}
             },
             "required": ["city"]
         }}
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """实际执行工具调用"""
    if name == "get_travel_info":
        city = arguments["city"]
        info = TRAVEL_DATA.get(city, {"error": f"暂无{city}的旅游数据"})
        return [{"type": "text", "text": json.dumps(info, ensure_ascii=False)}]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

print("=== MCP Server 示例 (server.py) ===")
print(server_code)
print("\n使用方式:")
print("  1. 将 server.py 配置到 Claude Desktop / Cursor 的 MCP 设置中")
print("  2. 向 AI 助手提问: '推荐北京的旅游攻略'")
print("  3. AI 自动通过 MCP 调用 get_travel_info('北京') 获取数据")
```

### 实战 4：MCP Client 调用示例

```python
"""MCP Client 调用 Server 的完整示例"""
print("""
# === MCP Client 使用示例 ===
# 在 Claude Desktop 的配置文件中添加 MCP Server:

# claude_desktop_config.json:
{
  "mcpServers": {
    "travel-guide": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/server"
    },
    "fetch-web": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-fetch"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-key"
      }
    }
  }
}

# 配置后，AI 助手自动获得以下能力:
# - 查询旅游攻略（本地 MCP Server）
# - 抓取网页内容（Fetch MCP Server）
# - 搜索互联网（Brave Search MCP Server）
# 用户不需要关心工具怎么调用，AI 自动决策
""")

# Python 代码直接调用 MCP Server
print("""
# === Python 中直接使用 MCP Client ===
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def call_travel_mcp():
    # 创建与 MCP Server 的连接参数
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()

            # 列出所有可用工具
            tools = await session.list_tools()
            print(f"可用工具: {[t.name for t in tools.tools]}")

            # 调用工具
            result = await session.call_tool(
                "get_travel_info",
                arguments={"city": "北京"}
            )
            print(f"北京旅游攻略: {result.content[0].text}")

# asyncio.run(call_travel_mcp())
""")
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

### Function Calling 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 模型不调用函数 | 函数描述不够清晰 | 加详细的 description 和参数说明 |
| 参数解析失败 | LLM 生成了错误的 JSON | 加 `strict: true`，用结构化输出 |
| 循环调用同一函数 | 函数返回结果不满足 LLM | 函数返回明确的"成功/失败"标志 |
| 安全风险 | SQL 注入、命令注入 | **永远不要**把 LLM 生成的参数直接拼到系统命令中 |

### MCP 生态概览

| MCP Server | 功能 | 命令 |
|------------|------|------|
| Fetch | 网页抓取 | `npx @anthropic-ai/mcp-server-fetch` |
| Brave Search | 网络搜索 | `npx @anthropic-ai/mcp-server-brave-search` |
| GitHub | GitHub 操作 | `npx @anthropic-ai/mcp-server-github` |
| PostgreSQL | 数据库查询 | `npx @anthropic-ai/mcp-server-postgres` |
| Filesystem | 文件操作 | `npx @anthropic-ai/mcp-server-filesystem` |
| Memory | 记忆存储 | `npx @anthropic-ai/mcp-server-memory` |

### 后续学习路径

- [2.2.2 Agent的自主规划与工具开发](2-2-2_Agent的自主规划与工具开发.md) — Agent 如何用 FC/MCP 完成复杂自主任务
- [2.2.3 Agent的能力优化与效果评估](2-2-3_Agent的能力优化与效果评估.md) — Agent 的评估和优化
- [2.2.4 Harness Engineering](2-2-4_Harness_Engineering.md) — 大规模工具集成

---

## 常见问题

### 小白最常踩的 3 个坑

1. **混淆 Function Calling 和 MCP**
   - 错误：以为装了 MCP Server 就能让任何模型有 Function Calling 能力
   - 正确：MCP 需要模型的 Function Calling 能力配合才能用。先确认模型是否支持 Function Calling（DeepSeek/Qwen/GPT-4 系列支持，部分小模型不支持）

2. **LLM 生成的 SQL 直接执行（安全风险）**
   - 错误：把 LLM 生成的 SQL 原样执行
   - 正确：永远只给模型**只读权限**（SELECT），严禁 DROP/DELETE/UPDATE。使用只读数据库账户 + 查询超时限制

3. **MCP Server 配置后不生效**
   - 错误：改了配置不重启 AI 应用
   - 正确：修改 MCP 配置后必须重启 Claude Desktop / Cursor 才能加载新的 MCP Server

### 自检题

**Q1**：Function Calling 中 `tool_choice: "auto"` 和 `tool_choice: "required"` 有什么区别？什么时候用 `required`？

> **答案**：`auto` 让模型自己判断要不要调函数（LLM 可以决定不调函数直接回答）。`required` 强制模型必须调函数。当每次回答都依赖实时数据（如天气/股票/数据库）时用 `required`，确保模型不会跳过函数调用直接输出过时信息。

**Q2**：MCP 和传统 API 调用的核心区别是什么？为什么需要 MCP 这个协议？

> **答案**：传统 API 调用需要为每个服务单独写集成代码（不同服务不同接口格式）。MCP 统一了"发现工具→调用工具→返回结果"的标准流程，任何 MCP Client 可以和任何 MCP Server 通信，即插即用。目标是做"AI 工具的 USB-C 接口"——一个标准连接一切。

**Q3**：A2A 协议解决了什么问题？为什么不能直接用 MCP 代替？

> **答案**：MCP 解决"模型怎么用工具"（人→模型→工具），A2A 解决"Agent 之间怎么协作"（Agent→Agent）。例如多个专业 Agent 协作完成一个复杂任务（研究 Agent 搜数据、分析 Agent 出洞察、写作 Agent 出报告），它们之间需要委托任务、汇报进度、传递成果——这是 MCP 不覆盖的。

---

## 延伸阅读

### 中文资料（推荐，无需科学上网）

- [MCP 官方文档中文版](https://modelcontextprotocol.io/docs/) — Anthropic MCP 协议完整文档
- [Qwen-Agent Function Calling 教程](https://github.com/QwenLM/Qwen-Agent) — Qwen 官方 Agent 框架，含 FC 示例
- [DeepSeek Function Calling 文档](https://platform.deepseek.com/api-docs/) — DeepSeek API 的 FC 使用指南
- [A2A 协议简介 - 知乎](https://docs.python.org/3/) — Agent-to-Agent 通信协议介绍

### 英文资料（可能需科学上网）

- [MCP Specification](https://spec.modelcontextprotocol.io/) — MCP 协议规范
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) — OpenAI 官方 FC 文档
- [MCP Server 市场](https://github.com/modelcontextprotocol/servers) — 社区 MCP Server 合集
