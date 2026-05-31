---
name: 0001_git-commit
description: AI 学习项目 Git 提交规范。涉及 Gitee 仓库操作、commit message 格式、分支管理、推送流程。当用户要求提交代码、创建 commit、推送时调用。
allowed-tools: Bash Read Edit
---

**格式规则**：Skill 是模板，禁止硬编码项目特定值。用 `{平台}` `{远程URL}` 等占位符。

---

# Git 提交规范

## 远程仓库

- **平台**: {平台} (Gitee / GitHub / 其他)
- **远程**: `origin {远程URL}`
- **默认分支**: {默认分支}

## Commit Message 格式（学习项目简化版）

```
<类别>: <一句话描述>
```

类别：`docs` / `exp` / `feat` / `fix` / `chore` / `refactor`

例：
- `docs: add Transformer Attention 学习笔记`
- `exp: nanoGPT training - add cosine lr scheduler`
- `feat: add RAG system with Chroma + qwen2.5`

## 提交流程

**核心规则：禁止自主 commit。只有用户明确说「提交」「commit」「推送」时才执行。**

0. **触发检查**：用户消息中必须含「提交」「commit」「推送」「push」等关键词，否则不执行 commit
1. `git status` 确认变更文件，列出给用户确认
2. `git add <指定文件>`（不 add 以下内容）:
   - `data/` `checkpoints/` `outputs/` 下的文件
   - `00_local_task/` 下除 `local_data_guide.md` 外的文件
   - `.env` 等敏感文件
   - 大文件（>10MB）
3. `git commit` — 仅用户确认后执行
4. **不自动 push**（需用户再次确认）

## 推送流程

1. 检查远程配置：`git remote -v`
2. `git fetch` 获取远端状态
3. `git log HEAD..origin/master --oneline` 检查差异
   - 无新提交 → 直接 push
   - 有新提交 → 先 pull 再 push
4. `git push`

## 冲突处理

1. `git stash` 暂存
2. `git pull --rebase`
3. 解决冲突 → `git add` + `git rebase --continue`
4. `git stash pop`
5. `git push`

## 禁止事项

- **禁止自主 commit**：用户没明确说「提交」「commit」时，只改代码不提交
- 不 skip hooks（--no-verify）
- 不 force push 到 master
- 不提交 `.env`、credentials、API key
- 不提交 `data/` `checkpoints/` `outputs/` 下的文件
