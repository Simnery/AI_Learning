---
name: finishing-a-development-branch
description: 当计划中的所有 task 完成并验证通过后使用，用于收尾开发工作
---

# Finishing a Development Branch

**核心流程：** 验证测试 → 呈现选项 → 执行选择 → 清理。

## 步骤 1：验证测试

运行项目的完整测试套件。如果测试失败 → 停止。不能继续。

```
全部测试通过 → 继续
任何测试失败 → 报告失败，不能继续
```

## 步骤 2：呈现选项

精确呈现以下 4 个选项（不附加额外解释）：

1. **本地合并** — 合并到基分支，清理
2. **推送并创建 PR** — 推送分支，创建 PR 供审查
3. **保持现有状态** — 保留所有内容，不做变更
4. **丢弃工作** — 删除分支，丢弃所有变更

## 步骤 3：执行选择

**选项 1 — 本地合并：**
```bash
git checkout master
git pull origin master
git merge <branch>
# 再次验证测试
git push origin master
git branch -d <branch>
```

**选项 2 — 推送并创建 PR：**
```bash
git push origin <branch>
# 使用 0001_git-commit skill 的约定创建 PR
```

**选项 3 — 保持现有状态：**
- 报告当前状态
- 无需进一步操作

**选项 4 — 丢弃：**
- 要求用户输入 "discard" 确认
- 强制删除分支

## 与 0001_git-commit 的协同

- 选项 1（合并）→ 调用 `0001_git-commit` 进行 commit 和推送
- 选项 2（PR）→ 使用 0001_git-commit 的约定来格式化 commit message
- Gitee + GitHub 双平台推送由 0001_git-commit 处理

## 常见错误

- 跳过测试验证
- 在验证合并之前删除分支
- 忘记双平台推送（Gitee + GitHub）

## 红线

绝不：
- 在测试失败的情况下继续
- 未经输入确认就删除
- 跳过双平台推送

始终：
- 在呈现选项之前验证测试通过
- 对选项 4 要求输入 "discard" 确认
