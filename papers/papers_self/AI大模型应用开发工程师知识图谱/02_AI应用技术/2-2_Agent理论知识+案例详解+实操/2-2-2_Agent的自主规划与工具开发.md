# 2.2.2 Agent的自主规划与工具开发

> 2.2 Agent理论知识+案例详解+实操 > 2. AI应用技术

---

## 核心概念

### 什么是 Agent 的自主规划

**一句话**：Agent 自主规划是指 AI 不只是"你问一句我答一句"，而是能自己把复杂任务拆成步骤、按顺序执行、遇到问题自己调整。

```
简单的聊天:  用户 → LLM → 回答（线性，一步到位）
自主 Agent:  用户 → LLM 制定计划 → 分步执行 → 检查结果 → 调整 → 完成（循环，多步推理）
```

**类比**：普通 AI 是"电话答录机"（你问什么答什么），有规划的 Agent 是"项目经理"（收到需求 → 拆解任务 → 分派执行 → 检查质量 → 交付）。

### Agent 的三种设计范式

| 范式 | 怎么做 | 优点 | 缺点 | 典型应用 |
|------|--------|------|------|---------|
| **反应式**（Reactive） | 感知→直接行动，不思考 | 极快 | 无法处理复杂任务 | 简单聊天机器人 |
| **深思熟虑式**（Deliberative） | 感知→规划→行动，先想再做 | 能处理复杂任务 | 慢，可能"过度思考" | 旅行规划、代码生成 |
| **混合式**（Hybrid） | 紧急情况反应式，复杂情况深思式 | 既快又强 | 实现复杂 | 自动驾驶、智能客服 |

**选择建议**：大多数应用场景选**混合式**——简单问题快速反应，复杂任务展开规划。

### 为什么 Agent 需要"自己写代码"

当现有工具不够用时，最强大的 Agent 能**自己创造工具**：

```
用户: "帮我分析这个 CSV 中的数据趋势"

传统 Agent（只有固定工具）:
  → 尝试用已有限工具处理 → 工具不匹配 → 失败

自编程 Agent:
  → 思考: 需要读取 CSV → 计算统计 → 画图
  → 编写 Python 代码完成这些操作
  → 执行代码 → 展示结果
  → 成功！
```

### 前置知识

- Function Calling 基础（[2.2.1 Function Calling与MCP](2-2-1_Function_Calling与MCP.md)）
- LLM 基本原理与 API（[1.2.1 AI大模型基本原理及API使用](../../01_AI大模型基础/1-2_实操基础/1-2-1_AI大模型基本原理及API使用.md)）

---

## 原理讲解

### ReAct：思考+行动循环

ReAct（Reasoning + Acting）是 Agent 规划的基础范式，把"想"和"做"交替进行：

```
ReAct 循环:
  ┌──────────────────────────────────┐
  │ 1. Thought (思考):               │
  │    "我需要知道北京的天气"         │
  │    ↓                             │
  │ 2. Action (行动):                │
  │    调用 get_weather("北京")       │
  │    ↓                             │
  │ 3. Observation (观察):           │
  │    "晴，18-25℃"                 │
  │    ↓                             │
  │ 4. Thought (再思考):             │
  │    "还需要查上海天气做对比"       │
  │    ↓                             │
  │ 5. Action → Observation → 循环   │
  │    ↓                             │
  │ 6. Thought (最终思考):           │
  │    "信息够了，可以回答了"        │
  │    ↓                             │
  │ 7. Answer: "北京晴天..."         │
  └──────────────────────────────────┘
```

**Chain-of-Thought（CoT）vs ReAct**：

| 方法 | 做法 | 区别 |
|------|------|------|
| **CoT** | 逐步推理，但不调用工具（纯脑内推演） | "动脑不动手" |
| **ReAct** | 逐步推理 + 调用工具 + 观察结果 | "边动脑边动手" |

CoT 适合数学推理和逻辑分析（不需要外部数据），ReAct 适合需要查信息/操作外部系统的场景。

### 混合式架构的实现

```python
def hybrid_agent(query):
    """混合式 Agent: 简单问题快速回复, 复杂任务进入规划"""
    # 步骤1: 快速分类
    complexity = classify_complexity(query)  # simple / medium / complex

    if complexity == "simple":
        return direct_answer(query)  # 反应式: 直接回答
    elif complexity == "medium":
        return react_loop(query)   # ReAct: 思考-行动循环
    else:  # complex
        plan = make_plan(query)     # 深思熟虑式: 先规划
        return execute_plan(plan)   # 再执行
```

### Code Interpreter：给 Agent 一个"代码执行器"

Code Interpreter 是最强大的 Agent 工具之一——让 Agent 能写代码来解决没有预置工具的问题：

```
Agent 有了 Code Interpreter 后能做什么:
  - 读取用户上传的文件（CSV, Excel, PDF...）
  - 数据清洗、统计分析、可视化
  - 运行算法、验证假设
  - 甚至写代码去调用其他 API

工作原理:
  LLM 生成代码 → 沙盒执行 → 捕获输出/错误 → 传回 LLM → LLM 解读结果
```

### Text-to-SQL Copilot 原理

Text-to-SQL 是 Agent 自主规划的一个经典用例：

```
用户自然语言 → Agent 理解意图 → 规划查询步骤 → 生成 SQL → 执行 → 解读结果

"技术部工资最高的三个人是谁？分别多少工资？"
  ↓ Agent 规划
  1. 查 employees 表结构
  2. 筛选 dept='技术部'
  3. 按 salary 降序排列
  4. 取前3条
  ↓ 生成 SQL
  SELECT name, salary FROM employees
  WHERE dept = '技术部'
  ORDER BY salary DESC LIMIT 3
  ↓ 执行 + 解读
  "技术部工资最高的三个人是：王五(35000)、张三(30000)、..."
```

**关键安全原则**：Text-to-SQL Agent 必须使用**只读数据库账户**，绝不能给 DROP/UPDATE/DELETE 权限。

---

## 代码实战

### 环境准备

```bash
pip install openai sqlite3  # sqlite3 是 Python 内置模块
```

### 实战 1：完整的 ReAct Agent

```python
"""ReAct Agent: 完整的思考-行动-观察循环"""
import json
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.deepseek.com",
)

# ===== 定义可用工具 =====
def search_knowledge(query):
    """模拟知识库搜索"""
    knowledge = {
        "天气": "北京晴天18-25℃, 上海多云22-28℃",
        "产品": "DeepSeek V3: MoE架构, API价格1元/1M token",
        "股票": "贵州茅台: 1680元/股, 今日涨2.3%",
    }
    for k, v in knowledge.items():
        if k in query:
            return v
    return "未找到相关信息"

def calculate(expression):
    """安全的数学计算"""
    return eval(expression, {"__builtins__": {}}, {})

tools = {
    "search_knowledge": search_knowledge,
    "calculate": calculate,
}

# ===== ReAct Prompt =====
REACT_SYSTEM_PROMPT = """你是一个使用 ReAct 模式的 Agent。你可以使用以下工具:

- search_knowledge(query: str): 搜索知识库
- calculate(expression: str): 执行数学计算

请按以下格式回答问题:

Thought: [你对当前情况的思考]
Action: tool_name(arguments)
Observation: [工具的返回结果]
... (可重复多次 Thought-Action-Observation)
Thought: 我现在有足够信息来回答了
Final Answer: [最终回答]

注意:
- 每次只输出一个 Thought/Action 或 Thought/Final Answer
- Action 参数必须是一个有效的 JSON 或简单字符串
"""

def run_react_agent(user_query, max_steps=5):
    """运行 ReAct 循环"""
    messages = [
        {"role": "system", "content": REACT_SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    for step in range(max_steps):
        print(f"\n{'='*40}\nStep {step+1}\n{'='*40}")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.1,
        )
        text = response.choices[0].message.content
        print(f"Agent:\n{text}")

        messages.append({"role": "assistant", "content": text})

        # 检查是否是 Final Answer
        if "Final Answer:" in text:
            return text.split("Final Answer:")[1].strip()

        # 解析 Action
        if "Action:" in text:
            action_line = text.split("Action:")[1].strip().split("\n")[0]
            # 解析 tool_name(arguments)
            if "(" in action_line and ")" in action_line:
                tool_name = action_line[:action_line.index("(")].strip()
                arg = action_line[action_line.index("(")+1:action_line.rindex(")")].strip().strip("'\"")
            else:
                print(f"  ❌ 无法解析 Action: {action_line}")
                break

            if tool_name in tools:
                result = tools[tool_name](arg)
                print(f"  [工具执行] {tool_name}({arg}) → {result}")
                observation = f"Observation: {result}"
                messages.append({"role": "user", "content": observation})
            else:
                print(f"  ❌ 未知工具: {tool_name}")
                break

    return "达到最大步数限制"

# 测试
result = run_react_agent("北京和上海今天哪里更适合出游？请对比天气后给出建议。")
print(f"\n{'='*40}\n最终结果: {result}")
```

### 实战 2：Code Interpreter Agent

```python
"""Agent 自主编写并执行代码"""
import subprocess
import tempfile
import os

def execute_python_code(code):
    """在临时文件中安全执行 Python 代码"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]:\n{result.stderr}"
        return output.strip() or "(无输出)"
    except subprocess.TimeoutExpired:
        return "代码执行超时(30秒)"
    finally:
        os.unlink(tmp_path)  # 清理临时文件

# Code Interpreter Agent 的 Prompt
CODE_AGENT_PROMPT = """你是一个能写代码解决问题的 Agent。用户会给你一个任务，你需要:

1. 分析任务，确定需要写什么代码
2. 输出 Python 代码（放在 ```python ... ``` 中）
3. 代码执行结果会返回给你
4. 根据结果，如果需要调整代码，继续输出修正版本
5. 最终基于执行结果给出回答

注意:
- 使用 print() 输出结果
- 如需安装库，说明需要 pip install xxx
- 对于数据分析任务，先打印数据的概况信息
"""

# 演示 Code Interpreter 的交互流程
print("=== Code Interpreter Agent 演示 ===")

# 模拟用户上传的 CSV 数据
sample_csv = """name,age,department,salary
张三,28,技术部,30000
李四,32,市场部,25000
王五,35,技术部,35000
赵六,26,设计部,22000
钱七,40,技术部,40000
"""

# Agent 会为这个数据生成分析代码
print(f"用户数据:\n{sample_csv}")

# Agent 通常会生成类似这样的代码:
agent_generated_code = '''
import csv
from io import StringIO

data = """name,age,department,salary
张三,28,技术部,30000
李四,32,市场部,25000
王五,35,技术部,35000
赵六,26,设计部,22000
钱七,40,技术部,40000
"""

reader = csv.DictReader(StringIO(data))
rows = list(reader)

# 基本统计
print(f"总人数: {len(rows)}")
print()

# 按部门统计平均工资
from collections import defaultdict
dept_salary = defaultdict(list)
for r in rows:
    dept_salary[r["department"]].append(int(r["salary"]))

print("各部门平均工资:")
for dept, salaries in dept_salary.items():
    avg = sum(salaries) / len(salaries)
    print(f"  {dept}: {avg:.0f}元 (人数: {len(salaries)})")

# 最高和最低工资
max_salary = max(rows, key=lambda r: int(r["salary"]))
min_salary = min(rows, key=lambda r: int(r["salary"]))
print(f"\\n工资最高: {max_salary['name']}({max_salary['department']}) - {max_salary['salary']}元")
print(f"工资最低: {min_salary['name']}({min_salary['department']}) - {min_salary['salary']}元")
'''

print(f"\nAgent 生成的代码:")
print(agent_generated_code)

result = execute_python_code(agent_generated_code)
print(f"\n代码执行结果:\n{result}")
```

### 实战 3：Text-to-SQL Copilot

```python
"""Text-to-SQL Copilot: 自然语言查询数据库"""
import sqlite3
import json
from openai import OpenAI

# ===== 准备演示数据库 =====
conn = sqlite3.connect(":memory:")
conn.executescript("""
    CREATE TABLE employees (
        id INT, name TEXT, dept TEXT, salary INT, join_date TEXT
    );
    INSERT INTO employees VALUES (1,'张三','技术部',30000,'2020-03-15');
    INSERT INTO employees VALUES (2,'李四','市场部',25000,'2021-07-01');
    INSERT INTO employees VALUES (3,'王五','技术部',35000,'2019-01-10');
    INSERT INTO employees VALUES (4,'赵六','设计部',22000,'2022-11-20');
    INSERT INTO employees VALUES (5,'钱七','技术部',40000,'2018-06-01');

    CREATE TABLE projects (
        id INT, name TEXT, lead_id INT, budget INT
    );
    INSERT INTO projects VALUES (1,'AI客服',3,500000);
    INSERT INTO projects VALUES (2,'数据分析平台',5,800000);
    INSERT INTO projects VALUES (3,'移动端重构',2,300000);
""")
conn.commit()

# ===== SQL Copilot =====
client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.deepseek.com",
)

SQL_COPILOT_PROMPT = """你是一个 Text-to-SQL Copilot。数据库有以下表:

表1: employees (id, name, dept, salary, join_date)
表2: projects (id, name, lead_id, budget)
  - lead_id 对应 employees.id

用户会用自然语言问问题。你需要:
1. 理解用户意图
2. 生成正确的 SQL 语句（只生成 SELECT，禁止 INSERT/UPDATE/DELETE/DROP）
3. 输出 SQL 语句

重要安全规则:
- 只允许 SELECT 查询
- 不允许多条语句
- 如果不确定，先查表结构"""

def sql_copilot(question):
    """自然语言→SQL→结果→自然语言"""
    print(f"用户: {question}\n")

    # Step 1: 生成 SQL
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SQL_COPILOT_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0.1,
    )
    sql = response.choices[0].message.content.strip()
    # 提取 SQL（去除可能的解释文本）
    if "SELECT" in sql.upper():
        sql = sql[sql.upper().index("SELECT"):]
        if ";" in sql:
            sql = sql[:sql.index(";")+1]

    print(f"SQL: {sql}")

    # Step 2: 安全检查
    sql_upper = sql.upper().strip()
    if any(kw in sql_upper for kw in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER"]):
        print("❌ 安全拦截: 不允许修改操作")
        return "查询被安全策略拦截"

    # Step 3: 执行
    cur = conn.execute(sql)
    columns = [d[0] for d in cur.description]
    rows = cur.fetchall()

    print(f"结果: {len(rows)} 行")
    for row in rows:
        print(f"  {dict(zip(columns, row))}")

    # Step 4: 自然语言解读
    interpretation = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "将数据库查询结果用自然语言简洁地解释给用户"},
            {"role": "user", "content": f"问题: {question}\n查询结果: {json.dumps({'columns': columns, 'rows': rows}, ensure_ascii=False)}"},
        ],
    )
    print(f"\n回答: {interpretation.choices[0].message.content}")

# 测试
sql_copilot("技术部员工的平均工资和最高工资是多少？")
print("\n" + "="*50 + "\n")
sql_copilot("列出每个部门的工资总额，按总额从高到低排序")

conn.close()
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

### Agent 规划的挑战

| 挑战 | 说明 | 缓解方案 |
|------|------|---------|
| **幻觉行动** | Agent 想象出不存在的工具 | 严格的工具列表校验 |
| **循环规划** | 陷入无限"再搜一次" | 设置 max_steps，每步增加"必要性检查" |
| **目标遗忘** | 多步后忘记最初目标 | 每步重述原始目标 |
| **资源滥用** | 生成 50 行代码能解决的写 500 行 | 限制代码长度和复杂度 |

### Code Interpreter 安全最佳实践

```
安全层:
  1. 沙盒执行（Docker/虚拟机）
  2. 网络隔离（禁止访问外网）
  3. 资源限制（CPU/内存/磁盘/时间上限）
  4. 系统调用白名单
  5. 敏感信息过滤（API Key 正则检测）

最低要求（本地开发环境）:
  - subprocess timeout（30秒）
  - 禁止 os.system / subprocess shell=True
  - 临时文件自动清理
```

### 后续学习路径

- [2.2.3 Agent的能力优化与效果评估](2-2-3_Agent的能力优化与效果评估.md) — 评估 Agent 效果
- [2.2.4 Harness Engineering](2-2-4_Harness_Engineering.md) — 大规模工具编排
- [2.3.1 LLM微调原理](../2-3_模型训练与微调理论知识+案例详解+实操/2-3-1_LLM微调原理.md) — 微调让 Agent 更擅长规划和调用工具

---

## 常见问题

### 小白最常踩的 3 个坑

1. **ReAct 循环中忘记保留历史**
   - 错误：每次调用 LLM 只用最新的观察结果，丢失了前面的上下文
   - 正确：messages 数组逐条追加，LLM 能看到完整的 Thought-Action-Observation 历史

2. **代码执行没有任何安全限制**
   - 错误：`exec(user_code)` 或 `os.system(user_code)` 直接在宿主机执行
   - 正确：沙盒执行 + 超时 + 资源限制。最低限度用 subprocess + timeout + 临时文件

3. **Agent 规划过于复杂反而出错**
   - 错误：让 Agent 做 20 步的详细计划，中间任一步出错全盘崩溃
   - 正确：复杂任务用"高层计划 + 逐步细化"模式（先定大方向，每步执行前再细化）

### 自检题

**Q1**：混合式 Agent 如何判断一个问题该用"反应式"还是"深思熟虑式"？给出一个判断规则。

> **答案**：判断标准是"问题是否需要多步推理或外部信息"——如果是事实性问答（"1+1等于几""今天星期几"）用反应式直接回答；如果需要多步操作（"帮我分析这份数据并出报告"）或依赖外部工具（"查天气对比后推荐出行方案"）则用深思熟虑式。实践中可用一个轻量分类器或让 LLM 自己输出 `complexity: simple/complex`。

**Q2**：Code Interpreter 和 Function Calling 有什么区别？为什么不是所有功能都用 Code Interpreter？

> **答案**：Function Calling 调用预定义的、特定的函数（明确输入输出，更可控更安全）。Code Interpreter 执行任意代码（灵活但风险高）。对于高频、明确的操作（查天气、查数据库），Function Calling 更高效安全；对于一次性的、灵活的数据处理（分析用户上传的 Excel），Code Interpreter 更合适。

**Q3**：Text-to-SQL Copilot 最关键的安全措施是什么？

> **答案**：最关键的是使用**只读数据库账户**——即使 Agent 生成了 DELETE/DROP 语句也无法执行。其次是 SQL 关键词检测（拦截 INSERT/UPDATE/DELETE/DROP），双重保护。绝不能只依赖 LLM 的 Prompt 约束（"请只生成 SELECT"），因为 LLM 可能被注入攻击绕过。

---

## 延伸阅读

### 中文资料（推荐，无需科学上网）

- [ReAct 论文中文解读 - 知乎](https://docs.python.org/3/) — ReAct 原理和实现详解
- [Qwen-Agent 工具开发指南](https://github.com/QwenLM/Qwen-Agent/blob/main/docs/tool.md) — 如何给 Qwen-Agent 开发自定义工具
- [Text-to-SQL 技术综述 - CSDN](https://so.csdn.net/so/search?q=Text-to-SQL%20%E6%8A%80%E6%9C%AF) — 从 NL2SQL 到智能数据分析

### 英文资料（可能需科学上网）

- [ReAct Paper](https://arxiv.org/abs/2210.03629) — ReAct 原始论文
- [OpenAI Code Interpreter 文档](https://platform.openai.com/docs/assistants/tools/code-interpreter) — OpenAI 官方 Code Interpreter
- [LangGraph Agent 教程](https://langchain-ai.github.io/langgraph/tutorials/) — LangChain 的 Agent 编排框架
