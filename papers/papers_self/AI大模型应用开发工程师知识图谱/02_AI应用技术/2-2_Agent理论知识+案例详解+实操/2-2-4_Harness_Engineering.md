# 2.2.4 Harness Engineering

> 2.2 Agent理论知识+案例详解+实操 > 2. AI应用技术

---

## 核心概念

### 什么是 Harness Engineering

**一句话**：Harness Engineering 是给 Agent 搭建"操作系统"——不是写一个 Agent，而是设计 Agent 运行的完整基础设施（记忆、执行、编排、反馈四层）。

```
单次对话的 AI:  "金鱼记忆"——每次对话从零开始
Harness 加持的 AI: "大象记忆"——记住所有历史，能自己规划、执行、纠错
```

**类比**：如果 Agent 是一辆汽车，Harness Engineering 就是设计道路系统、加油站、交通规则和维修站。

### 四层架构总览

```
┌──────────────────────────────────────────────┐
│              编排层 Orchestration            │
│         "先做什么、后做什么、谁来做"          │
│         任务分解 → 流程编排 → 并行执行        │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────┴───────────────────────┐
│              记忆层 Memory                   │
│         "记住什么、怎么记住、怎么回忆"        │
│    短期(上下文) → 中期(对话) → 长期(知识)    │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────┴───────────────────────┐
│              执行层 Execution                │
│          "从'说出来'到'做出来'"               │
│      工具调用 → 代码执行 → 沙箱隔离           │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────┴───────────────────────┐
│              反馈层 Feedback                 │
│          "做错了就知道，下次不再犯"           │
│      自动纠错 → 效果评估 → 持续优化           │
└──────────────────────────────────────────────┘
```

### 前置知识

- Agent 基础与工具调用（[2.2.1 Function Calling与MCP](2-2-1_Function_Calling与MCP.md)）
- Agent 规划（[2.2.2 Agent的自主规划与工具开发](2-2-2_Agent的自主规划与工具开发.md)）

---

## 原理讲解

### 记忆层：给 AI 装上"持久化大脑"

**四层记忆颗粒度**（从细到粗）：

| 粒度 | 存储什么 | 生命周期 | 实现方式 | 类比 |
|------|---------|:--------:|---------|------|
| **L0 即时** | 当前对话的上下文 | 单次会话 | System Prompt + Messages | 工作记忆 |
| **L1 短期** | 完整对话历史 | 数天-数月 | SQLite 存全部聊天记录 | 最近经历 |
| **L2 中期** | 每日摘要/关键决策 | 数周-数年 | `YYYY-MM-DD.md` 每日笔记 | 日记 |
| **L3 长期** | 核心知识/规则/偏好 | 永久 | 向量数据库 + 结构化知识库 | 长期记忆/知识 |

**检索策略**：

```
用户提问
  → L0: 当前上下文(最快，直接就看)
  → L1: 搜索近期对话记录 → 找到相关历史对话
  → L2: 搜索每日摘要 → 找到某天的关键决策
  → L3: 向量搜索知识库 → 找到相关知识/规则
  → 综合所有记忆 → 生成回答
```

**实际系统参考**：

| 系统 | L1 实现 | L2 实现 | 特点 |
|------|---------|---------|------|
| **Claude Code** | SQLite 存全部聊天 | `memory/*.md` 持久记忆 | L1+L2 配合，/clear 保留 L2 |
| **Hermes** | SQLite 全量对话 | memory/YYYY-MM-DD.md | 每日自动摘要 |
| **OpenClaw** | 对话日志 | 结构化知识库 | 四层全覆盖 |

### 执行层：从"能说"到"能做"

执行层的核心是在**安全约束下**让 Agent 真正操作外部世界：

```
执行层的三大组件:
  1. 工具集(Tools)      — 预定义的工具函数
  2. 代码执行器(Executor) — 动态执行代码
  3. 环境管理(Env)       — 沙箱/权限/文件系统
```

**工具集设计原则**：

| 原则 | 说明 | 反例 |
|------|------|------|
| **单一职责** | 一个工具只做一件事 | `do_everything()` |
| **自描述** | 工具名和描述让 LLM 一看就懂 | `f1()`, `proc()` |
| **幂等性** | 同一参数多次调用结果相同 | `send_email()` 发了两次 |
| **失败明确** | 返回清晰的错误信息而非抛异常 | `return "error"` |
| **安全优先** | 危险操作需二次确认 | 直接 `rm -rf` |

**执行环境构建**：

```python
执行环境层级:
  Process 级(最快,最不安全)    — subprocess
  Container 级(隔离好)          — Docker
  VM 级(最安全)                 — 虚拟机/Git Worktree
```

### 编排层：让 AI 学会"规划与协作"

编排层负责**任务的拆解、调度和并行执行**：

```
用户: "分析这个项目代码质量"

编排层:
  1. 拆解任务:
     ├→ 子任务A: 统计代码行数和文件分布
     ├→ 子任务B: 运行 linter 检查
     ├→ 子任务C: 检查测试覆盖率
     └→ 子任务D: 分析依赖关系

  2. 调度执行:
     ├→ A、B、C 可并行 → 同时启动
     └→ D 依赖 A 的结果 → 等 A 完成后启动

  3. 汇总结果 → 生成报告
```

### 反馈层：自动化的纠错闭环

反馈层不依赖人工——Agent 自检 + 自动修正：

```
Agent 执行 → 结果检查 → 两种结果:
  ├─ ✅ 通过 → 记录成功模式
  └─ ❌ 失败 → 自动分析原因 → 重试(最多 N 次)
       ├─ 修好了 → 记录失败原因+修复方法
       └─ 仍失败 → 降级处理/请求人工介入
```

### 沙箱隔离的四层防护

```
第1层: 文件系统隔离
  Git Worktree → Agent 有独立的工作目录
  不影响原始代码，随时可丢弃

第2层: 网络隔离
  限制可访问的域名/IP
  防止 Agent 向外部发送敏感数据

第3层: 系统调用限制
  seccomp / AppArmor 限制系统调用
  防止 `os.system("rm -rf /")` 等危险操作

第4层: 权限精细化
  读/写/执行 分别控制
  敏感文件即使在同一目录也不可读
```

---

## 代码实战

### 环境准备

```bash
pip install sqlite3  # Python 内置
```

### 实战 1：四层记忆系统实现

```python
"""
四层记忆系统的极简实现
"""
import sqlite3
import json
import os
from datetime import datetime

class MemorySystem:
    """四层记忆系统"""

    def __init__(self, base_dir="./agent_memory"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

        # L0: 当前消息列表（内存中）
        self.l0_context = []

        # L1: SQLite 对话历史
        self.l1_conn = sqlite3.connect(f"{base_dir}/conversations.db")
        self._init_l1()

        # L2: 每日摘要文件
        self.l2_dir = f"{base_dir}/daily"
        os.makedirs(self.l2_dir, exist_ok=True)

        # L3: 向量知识库（此处简化为 JSON）
        self.l3_file = f"{base_dir}/knowledge.json"
        if not os.path.exists(self.l3_file):
            with open(self.l3_file, "w") as f:
                json.dump([], f)

    def _init_l1(self):
        """初始化对话历史表"""
        self.l1_conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,        -- user/assistant/system
                content TEXT,
                timestamp TEXT
            )
        """)
        self.l1_conn.commit()

    # ---- L0: 即时记忆 ----
    def add_to_context(self, role, content):
        """添加到当前上下文"""
        self.l0_context.append({"role": role, "content": content})
        # 同时持久化到 L1
        self.l1_conn.execute(
            "INSERT INTO conversations (role, content, timestamp) VALUES (?, ?, ?)",
            (role, content, datetime.now().isoformat())
        )
        self.l1_conn.commit()

    def get_context(self):
        return self.l0_context

    # ---- L1: 对话历史搜索 ----
    def search_history(self, keyword, limit=5):
        """搜索历史对话"""
        cur = self.l1_conn.execute(
            """SELECT role, content, timestamp FROM conversations
               WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?""",
            (f"%{keyword}%", limit)
        )
        return [{"role": r[0], "content": r[1][:100], "time": r[2]}
                for r in cur.fetchall()]

    # ---- L2: 每日摘要 ----
    def save_daily_summary(self, date_str, summary):
        """保存每日摘要"""
        filepath = f"{self.l2_dir}/{date_str}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {date_str}\n\n{summary}\n")
        print(f"L2 每日摘要已保存: {filepath}")

    def get_daily_summary(self, date_str):
        """读取每日摘要"""
        filepath = f"{self.l2_dir}/{date_str}.md"
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return None

    # ---- L3: 长期知识 ----
    def add_knowledge(self, key, value):
        """添加长期知识"""
        with open(self.l3_file, "r") as f:
            knowledge = json.load(f)
        knowledge.append({"key": key, "value": value,
                         "timestamp": datetime.now().isoformat()})
        with open(self.l3_file, "w") as f:
            json.dump(knowledge, f, ensure_ascii=False, indent=2)

    def search_knowledge(self, keyword):
        """搜索长期知识"""
        with open(self.l3_file, "r") as f:
            knowledge = json.load(f)
        return [k for k in knowledge if keyword in k["key"] or keyword in k["value"]]

# === 演示 ===
mem = MemorySystem()

print("=== 四层记忆系统演示 ===\n")

# L0 + L1: 对话记录
mem.add_to_context("user", "我的项目使用 Python 3.11 和 FastAPI")
mem.add_to_context("assistant", "了解了，你的项目技术栈是 Python 3.11 + FastAPI")
print("L0 上下文:", [m["content"][:30] for m in mem.get_context()])

# L1: 历史搜索
results = mem.search_history("Python")
print(f"\nL1 搜索 'Python': 找到 {len(results)} 条")
for r in results:
    print(f"  [{r['time'][:16]}] {r['role']}: {r['content']}")

# L2: 每日摘要
mem.save_daily_summary(
    "2026-05-30",
    "## 关键决策\n- 确认项目使用 FastAPI\n- 决定迁移到 async/await 模式\n## 遇到的问题\n- SQLAlchemy 异步 session 管理"
)
summary = mem.get_daily_summary("2026-05-30")
print(f"\nL2 每日摘要:\n{summary[:150]}...")

# L3: 长期知识
mem.add_knowledge("项目技术栈", "Python 3.11, FastAPI, SQLAlchemy, PostgreSQL")
mem.add_knowledge("用户偏好", "喜欢简洁的代码风格，反感过度设计")
results = mem.search_knowledge("技术栈")
print(f"\nL3 知识搜索 '技术栈':")
for k in results:
    print(f"  {k['key']}: {k['value']}")
```

### 实战 2：工具集 + 执行环境

```python
"""工具集设计与安全执行"""
import subprocess
import tempfile
import os
import shutil

class SandboxedExecutor:
    """带沙箱的代码执行器"""

    def __init__(self, work_dir=None):
        # 创建隔离的工作目录(类似 Git Worktree 的思路)
        self.work_dir = work_dir or tempfile.mkdtemp(prefix="agent_sandbox_")
        os.makedirs(self.work_dir, exist_ok=True)
        print(f"沙箱目录: {self.work_dir}")

    def execute(self, code, timeout=30):
        """在沙箱中执行代码"""
        # 1. 安全检查（禁止危险操作）
        forbidden = ["rm -rf /", "os.system", "shutil.rmtree('/')",
                     "subprocess.Popen", "__import__('os').system"]
        for pattern in forbidden:
            if pattern in code:
                return f"❌ 安全拦截: 禁止操作 '{pattern}'"

        # 2. 在沙箱目录中写入并执行
        script_path = os.path.join(self.work_dir, "_agent_script.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            result = subprocess.run(
                ["python", script_path],
                capture_output=True, text=True,
                timeout=timeout,
                cwd=self.work_dir,  # 限制在沙箱目录
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]: {result.stderr}"
            return output.strip() or "(无输出)"
        except subprocess.TimeoutExpired:
            return "⏰ 执行超时"

    def cleanup(self):
        """清理沙箱"""
        shutil.rmtree(self.work_dir, ignore_errors=True)


class AgentToolkit:
    """Agent 工具集"""

    def __init__(self):
        self.tools = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """注册默认工具"""
        self.register("read_file", self._read_file,
                      "读取文件内容: read_file(path)")
        self.register("write_file", self._write_file,
                      "写入文件: write_file(path, content)")
        self.register("search_code", self._search_code,
                      "搜索代码: search_code(pattern)")

    def register(self, name, func, description):
        self.tools[name] = {
            "function": func,
            "description": description,
        }

    def list_tools(self):
        """列出所有工具（用于 LLM 的 tools 参数）"""
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": info["description"],
                    "parameters": {"type": "object", "properties": {}},
                }
            }
            for name, info in self.tools.items()
        ]

    def call(self, name, **kwargs):
        """调用工具"""
        if name not in self.tools:
            return f"未知工具: {name}"
        try:
            return self.tools[name]["function"](**kwargs)
        except Exception as e:
            return f"工具 {name} 执行失败: {e}"

    def _read_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"文件不存在: {path}"

    def _write_file(self, path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"已写入: {path}"

    def _search_code(self, pattern):
        """搜索当前目录代码（演示用）"""
        matches = []
        for root, _, files in os.walk(".", topdown=True):
            for f in files[:10]:  # 限制数量
                if f.endswith(".py"):
                    matches.append(os.path.join(root, f))
        return f"找到 {len(matches)} 个 Python 文件: {matches[:5]}"


# === 演示 ===
print("=== 工具集 + 沙箱执行演示 ===\n")

# 工具集
toolkit = AgentToolkit()
print("可用工具:")
for t in toolkit.list_tools():
    print(f"  - {t['function']['name']}: {t['function']['description']}")

# 沙箱执行
executor = SandboxedExecutor()
print(f"\n执行测试代码:")
result = executor.execute("""
print("Hello from sandbox!")
import os
print(f"当前目录: {os.getcwd()}")
# 尝试列出文件
for f in os.listdir("."):
    print(f"  - {f}")
""")
print(f"结果:\n{result}")

executor.cleanup()
```

### 实战 3：Git Worktree 隔离模式

```python
"""用 Git Worktree 实现安全的工作区隔离"""
print("""
# === Git Worktree 隔离示例 ===

# 概念: Git Worktree 让你在同一仓库中创建独立的工作目录
# Agent 在 worktree 中自由修改，不影响原始代码
# 效果等价于"轻量级分支 + 独立文件系统"

# === 实际操作 ===

# 1. 创建 worktree（Agent 的工作区）
git worktree add ../agent-workspace feature/agent-task

# 2. Agent 在隔离的工作区中操作
cd ../agent-workspace
# Agent 可以自由读写文件、创建分支、提交
# 原始仓库完全不受影响

# 3. Agent 完成任务后
# 方案A: 保留成果
cd ../agent-workspace
git add -A && git commit -m "Agent 完成: 重构 XX 模块"
git push origin feature/agent-task

# 方案B: 丢弃（实验性质）
cd ../original-repo
git worktree remove ../agent-workspace --force
# Agent 的所有改动被完全清除

# === 为什么用 Worktree 做隔离 ===
# 1. 真正的文件系统隔离(AI 删文件不会影响原始代码)
# 2. 零拷贝(比 Docker 快, 不需要复制整个仓库)
# 3. Git 原生支持(不需要装 Docker)
# 4. 改好了可以合并, 搞砸了直接删

# === 工作流 ===
# 用户触发任务
#  → 创建 worktree(自动)
#  → Agent 在 worktree 中工作
#  → 完成后: git diff 检查变更
#  → 用户确认 → merge 回主分支
#  → 或: 用户拒绝 → 删除 worktree
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

### 四层架构的工程挑战

| 层 | 挑战 | 工程方案 |
|-----|------|---------|
| 记忆层 | 检索精度 vs 延迟 | 分层检索：先 L0/L1（ms级），再 L2/L3（ms-s级） |
| 执行层 | 代码执行安全性 | 多层沙箱：Worktree → seccomp → 网络隔离 |
| 编排层 | 长任务的状态管理 | 状态机 + 检查点，失败可断点续跑 |
| 反馈层 | 错误分类不自动 | LLM 自动分类 + 规则模板 + 人工审核升级 |

### 从研究到生产的 Checklist

```
安全性
  ✅ 所有文件操作在 worktree/沙箱中
  ✅ 网络访问使用白名单
  ✅ 危险操作需二次确认
  ✅ 敏感信息(API Key)不记录到日志

可观测性
  ✅ 所有工具调用记录到日志
  ✅ Agent 决策链路可追溯
  ✅ 错误自动分类和聚合

工程化
  ✅ 工具集有版本管理
  ✅ 记忆系统有备份策略
  ✅ 执行环境可快速重建
```

### 后续学习路径

- [2.3.1 LLM微调原理](../2-3_模型训练与微调理论知识+案例详解+实操/2-3-1_LLM微调原理.md) — 微调增强 Agent 能力
- [4.1.1 用确定性驾驭概率性](../../04_AI研发工程师工作新范式/4-1_AI_Coding带来的范式变革/4-1-1_用确定性驾驭概率性.md) — 如何在工程中驾驭 AI 的概率性

---

## 常见问题

### 小白最常踩的 3 个坑

1. **只做 L0，完全忽略 L1/L2/L3**
   - 错误：Agent 只有当前对话上下文，每次 `/clear` 或新会话一切归零
   - 正确：至少实现 L1（对话历史）+ L2（关键摘要），保证 Agent 有"记忆连续性"

2. **执行层不做沙箱隔离**
   - 错误：Agent 生成的代码直接在宿主机裸跑，删文件、读敏感信息毫无阻碍
   - 正确：至少用 Worktree + subprocess timeout，生产环境上 Docker

3. **工具描述写得模糊**
   - 错误：`def search(x): pass  # 搜索`，LLM 不知道什么时候该调用
   - 正确：用自然语言详细描述 "何时使用"、"参数含义"、"返回格式"。工具描述是 LLM 的"说明书"，写得越好，调用越准

### 自检题

**Q1**：为什么需要四层记忆（L0-L3），而不是把所有东西都放一个向量数据库？

> **答案**：不同记忆有不同的访问模式和时效性要求。L0（当前上下文）需要毫秒级访问，L1（历史对话）需要关键字搜索，L2（每日摘要）是按时间组织的结构化记录，L3（知识）需要语义检索。全放向量库会导致延迟高（语义搜索比 SQL 查询慢）、丢失时间结构（向量库不擅长"最近3天"这种时间查询）。

**Q2**：Git Worktree 做隔离相比 Docker 有什么优势和劣势？

> **答案**：优势：零拷贝（不需要复制仓库）、启动快（毫秒 vs 秒）、Git 原生集成（改好了可以直接合并）。劣势：不是真正的安全隔离（共享同一 OS，恶意代码仍可能影响宿主机）、无法限制系统资源（CPU/内存/磁盘 I/O）。Worktree 适合"防止误操作"，Docker 适合"防止恶意攻击"。

**Q3**：反馈层的"自动纠错"在实践中最大的限制是什么？什么时候必须人工介入？

> **答案**：最大限制是 LLM 可能无法正确判断自己是否犯了错——错误的输出也可能被判定为正确。必须人工介入的时机：连续 3 次自动修复失败、涉及到金钱/权限/生产环境等不可逆操作、反馈层自身怀疑"这个修复可能让事情更糟"。

---

## 延伸阅读

### 中文资料（推荐，无需科学上网）

- [Claude Code Memory 系统设计](https://docs.anthropic.com/en/docs/claude-code/memory) — Anthropic 的 AI 编程助手的记忆架构
- [Git Worktree 官方文档](https://git-scm.com/docs/git-worktree) — Git 多工作区功能
- [AI Agent 系统架构设计 - 知乎](https://docs.python.org/3/) — Agent 四层架构详解

### 英文资料（可能需科学上网）

- [OpenAI Agents SDK](https://platform.openai.com/docs/guides/agents) — OpenAI 的 Agent 编排框架
- [LangChain Memory 模块](https://python.langchain.com/docs/modules/memory/) — LangChain 的记忆系统实现
- [seccomp 安全手册](https://man7.org/linux/man-pages/man2/seccomp.2.html) — Linux 系统调用过滤，沙箱的底层技术
