# 2.2.4 Harness Engineering

> 2.2 Agent理论知识+案例详解+实操 > 2. AI应用技术

##### 2.2.4.1 编排层、记忆层、执行层、反馈层
- 记忆层（Memory Layer）：赋予AI"持久化大脑"
- 执行层（Execution Layer）：从"能说"到"能做"的飞跃
- 编排层（Orchestration Layer）：让AI学会"规划与协作"
- 反馈层（Feedback Layer）：建立"自动化"的纠错闭环

##### 2.2.4.2 OpenClaw、Hermes、Claude Code的核心memory机制
- 记录全部聊天历史的SQLite数据库
- 记录每日事项的memory/YYYY-MM-DD.md文件机制
- 四层颗粒度

##### 2.2.4.3 代码执行时涉及的环境及工具
- 工具集的设计原则
- 执行环境的构建

##### 2.2.4.4 沙箱、文件系统、权限
- 文件系统隔离：Git Worktree的妙用
- 沙箱隔离的四层防护
- 权限系统的精细化设计

---
