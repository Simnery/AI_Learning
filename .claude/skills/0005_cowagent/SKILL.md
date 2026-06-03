---
name: 0005_cowagent
description: CowAgent 远程接入平台管理 — 启动/停止/更新/配置/检查。支持企微/飞书/钉钉/Telegram 等多渠道 IM 实时通信，Agent 直读 CLAUDE.md 获取项目上下文执行操作。
allowed-tools: Read Write Bash
---

# CowAgent 管理

## 概述

管理 CowAgent 远程接入平台的完整生命周期。CowAgent 通过 git submodule 管理，Agent 直接读取项目 CLAUDE.md 获取上下文，通过多渠道 IM 实时接收指令并执行。支持切换任意 LLM 模型和 IM 渠道。

**当前架构：** IM 消息 → Agent 读 CLAUDE.md → bash/read/write/edit 执行 → 直接回复（无中间 relay）

## 何时使用

| 用户说 | 执行操作 |
|--------|---------|
| "启动 cowagent" | 启动服务 (配置同步 + 启动 + 健康检查) |
| "停止 cowagent" | 停止服务 |
| "更新 cowagent" | 拉取上游更新 |
| "同步 cowagent 配置" | 配置同步 |
| "检查 cowagent" | 健康检查 |
| "重启 cowagent" | 停止 + 启动 |

## 操作

### 1. 启动服务

```bash
python scripts/cowagent_sync_config.py
cd tools/cowagent && python app.py &
sleep 4
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:9899
```

启动后 Agent 自动加载 `cowagent_workspace/MEMORY.md`，首次消息时读取 `../.claude/CLAUDE.md`。

### 2. 停止服务

```bash
taskkill //F //IM python.exe
```

### 3. 拉取上游更新

```bash
git submodule update --remote tools/cowagent
cd tools/cowagent && python -m pip install -r requirements.txt -q
```

更新后检查 `tools/cowagent/config-template.json` 是否有新配置项，如有则同步到 `config.local.json` 和 `config.example.json`。

### 4. 配置同步

从 `.claude/config/config.local.json` → `cowagent` 段写入 `tools/cowagent/config.json`：

```bash
python scripts/cowagent_sync_config.py
```

### 5. 健康检查

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:9899
```

| HTTP 状态 | 含义 |
|-----------|------|
| 303 | 正常运行 |
| 000 | 未启动 |
| 其他 | 异常 |

## 配置管理

CowAgent 配置链：

```
config.local.json (你的凭证) → cowagent_sync_config.py → config.json (CowAgent 读取)
config.example.json (模板，git 跟踪，占位符)
```

**渠道配置示例 (config.json)：**

| 渠道 | channel_type | 所需字段 |
|------|-------------|---------|
| Web Console | `web` | 无额外字段 |
| 企微群机器人 | `wecom_bot` | `wecom_bot_id`, `wecom_bot_secret` |
| 飞书 | `feishu` | `feishu_app_id`, `feishu_app_secret` |
| 钉钉 | `dingtalk` | `dingtalk_client_id`, `dingtalk_client_secret` |
| Telegram | `telegram` | `telegram_token` |
| 多渠并发 | `web,wecom_bot,telegram` | 对应字段并存 |

## 工作空间

| 文件 | 用途 |
|------|------|
| `cowagent_workspace/AGENT.md` | Agent 身份 |
| `cowagent_workspace/MEMORY.md` | 项目上下文参考 |
| `cowagent_workspace/RULE.md` | 工作空间规范 |
| `cowagent_workspace/skills/bridge-relay/SKILL.md` | 远程代理 skill |

以上为 git 跟踪的核心文件。其他运行时目录 (scheduler/, tmp/ 等) 由 `.gitignore` 排除。

## 远程通信流程

```
IM @机器人 "检查项目状态"
  → Agent 读 MEMORY.md (会话加载)
  → Agent 读 CLAUDE.md (首次消息)
  → Agent 使用 bash/read 工具执行
  → 直接回复 IM（实时，无中间 relay）
```

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 端口 9899 被占用 | 先 stop 再 start |
| API Key 无效 | 检查 `config.local.json` → deepseek_api_key |
| IM 渠道无响应 | 检查对应渠道的凭证是否正确（如 wecom_bot_id/secret、feishu_app_id/secret） |
| submodule 有改动 | `git submodule update --init` 恢复纯净版 |

## 牢记

- Agent 直读 CLAUDE.md，无需手动 relay
- 配置集中管理在 `config.local.json`
- 工作空间核心文件受 `.gitignore` 保护
- submodule 保持纯净，本地改动不提交
