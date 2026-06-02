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
2. **检查凭证配置**：
   - 检查 `.claude/config/config.local.json` 是否存在
   - 若不存在 → 自动复制 `config.example.json` 为 `config.local.json`，提示用户填入对应平台的用户名和密码/Token 后重新推送
3. **识别 origin 平台，自动配好双向同步**（本地 `.git/config` 不随仓库同步，需自动修复）:

   **场景 A — origin 是 Gitee**（`gitee.com/Simnery/AI_Learning`）:
   添加 GitHub 为第二 push URL:
   ```bash
   git remote set-url --add --push origin https://github.com/Simnery/AI_Learning.git
   ```

   **场景 B — origin 是 GitHub**（`github.com/Simnery/AI_Learning`）:
   添加 Gitee 为第二 push URL:
   ```bash
   git remote set-url --add --push origin https://gitee.com/Simnery/AI_Learning.git
   ```

   检查方法：`git config --local --get-all remote.origin.pushurl` 查已有 push URL，只添加缺失的那一侧。

4. `git fetch` 获取远端状态
5. `git log HEAD..origin/master --oneline` 检查差异
   - 无新提交 → 直接 push
   - 有新提交 → 先 pull 再 push
6. `git push`（如 clone 时用 HTTPS，会使用 git credential manager 缓存的凭证；未缓存则提示输入）
7. **推送 403 故障排查**：
   - 检查 `config.local.json` 中 username 是否为**登录账号名**（非邮箱、非昵称）
     - Gitee: 用 `curl -s "https://gitee.com/api/v5/user" --user "username:token" | grep login` 验证
     - GitHub: 检查 `https://github.com/settings/tokens` 下 Token 的 Repository access 和 Contents 权限
   - Gitee Token 需勾选 `projects` / `仓库` 权限
   - GitHub 细粒度 Token (`github_pat_` 开头) 需: Repository access 选中目标仓库 + Permissions → Contents → Read and write

## Amend 合并提交（追加改动到上一次 commit）

**触发条件**：用户明确说「合并」「amend」「追加到上次提交」「合为一笔」时执行。

**流程**：
1. 确认未推送或用户知晓需 force push
2. `git add <文件>`
3. `git commit --amend`（复用原 commit message；如用户要求改 message 则调整）
4. `git push origin master --force-with-lease`
5. 若 `--force-with-lease` 被 GitHub 拒（stale info），对 GitHub remote 单独用 `--force`：
   ```bash
   git push github master --force
   ```

> **注意**：Gitee 通常接受 `--force-with-lease`，GitHub 在跨 remote 场景可能需 `--force`。amend 后务必确认两侧都推送成功。

## 网络优化（国内访问 GitHub 慢/超时）

**克隆策略**：
- **首选 Gitee**（国内快）：`git clone https://gitee.com/Simnery/AI_Learning.git`
- **备选 GitHub 浅克隆**（只拉最新，跳过历史）：
  ```bash
  git clone --depth 1 https://github.com/Simnery/AI_Learning.git
  ```
- **已有 Gitee 再补 GitHub**：
  ```bash
  git remote add github https://github.com/Simnery/AI_Learning.git
  git fetch github --depth 1
  ```

**验证克隆完整性**：克隆超过 30s 无进展即超时，改用 Gitee 或 `--depth 1`。

## 冲突处理

1. `git stash` 暂存
2. `git pull --rebase`
3. 解决冲突 → `git add` + `git rebase --continue`
4. `git stash pop`
5. `git push`

## 禁止事项

- **禁止自主 commit**：用户没明确说「提交」「commit」时，只改代码不提交
- 不 skip hooks（--no-verify）
- 不 force push 到 master（**例外**：amend 合并提交时可用 `--force-with-lease`）
- 不提交 `.env`、credentials、API key
- 不提交 `data/` `checkpoints/` `outputs/` 下的文件
