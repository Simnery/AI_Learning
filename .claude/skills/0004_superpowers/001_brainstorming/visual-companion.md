# 可视化伴侣指南

基于浏览器的可视化头脑风暴伴侣，用于展示原型、图表和选项。

## 何时使用

每个问题单独决定，而非每个会话决定。判断标准："用户看比读更能理解吗？"

**使用浏览器** 当内容是可可视化时：UI 原型、架构图、并排对比、设计润色和空间关系。

**使用终端** 当内容是文本或表格时：需求/范围、概念性 A/B/C 选择、权衡列表、技术决策和澄清问题。

关键区别："关于 UI 主题的问题并不自动等于可视化问题。"

## 工作原理

服务器监控一个目录中的 HTML 文件并展示最新的文件。用户将 HTML 写入 `screen_dir`，用户在浏览器中查看并点击选择选项。选择记录写入 `state_dir/events`。

**内容片段 vs 完整文档：** 以 `<!DOCTYPE` 或 `<html` 开头的 HTML 文件会被原样提供（注入辅助脚本）。否则，服务器会用框架模板包裹它们。默认编写内容片段。

## 启动会话

命令：`scripts/start-server.sh --project-dir /path/to/project`

返回 JSON，包含 server-started 类型、端口、URL、screen_dir 和 state_dir。

服务器将启动信息 JSON 写入 `$STATE_DIR/server-info`。传入项目根目录以便原型数据持久化在 `.superpowers/brainstorm/` 中。提醒用户将 `.superpowers/` 添加到 `.gitignore`（如果尚未添加）。

**各平台启动说明：**

- **Claude Code (macOS/Linux):** 默认模式可用；脚本自动后台运行。
- **Claude Code (Windows):** 自动检测前台模式——在 Bash 工具调用中使用 `run_in_background: true`。
- **Codex:** 自动检测 CODEX_CI 并切换到前台模式。
- **Gemini CLI:** 使用 `--foreground` 并在 shell 工具调用中设置 `is_background: true`。

对于远程/容器化设置：使用 `--host 0.0.0.0 --url-host localhost` 绑定。

## 循环流程

1. **检查服务器是否存活**，然后**将 HTML 写入** `screen_dir` 中的新文件：
   - 先验证 `$STATE_DIR/server-info` 存在；如果缺失或存在 `server-stopped`，重新启动。
   - 服务器在 30 分钟无活动后自动退出。
   - 使用有语义的文件名；永远不要重复使用文件名。
   - 使用 Write 工具——永远不要用 cat/heredoc（会将噪音输出到终端）。
   - 按修改时间排序，最新的文件会被提供。

2. **告诉用户预期内容并结束自己这一轮：**

3. **下一轮时：** 读取 `$STATE_DIR/events` 中的 JSON 交互行；与终端文本合并处理。

4. **迭代或推进** —— 为更改编写新文件；只有验证后才继续。

5. **返回终端时卸载** —— 推送一个显示居中"在终端中继续..."消息的等待页面。

## 编写内容片段

只编写页面内部的内容。最简结构：

```html
<h2>页面标题</h2>
<p class="subtitle">副标题文本</p>
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <span class="letter">A</span>
    <span class="content">选项描述</span>
  </div>
</div>
```

## 可用的 CSS 类

- **选项** —— `.options` 容器，内含 `.option` 子元素（每个有 `.letter` 和 `.content`）。多选：在容器上添加 `data-multiselect`。
- **卡片** —— `.cards` 容器，内含 `.card` 子元素，包含 `.card-image` 和 `.card-body`。
- **原型容器** —— `.mockup` 内含 `.mockup-header` 和 `.mockup-body`。
- **分屏视图** —— `.split` 内含两个 `.mockup` 子元素，用于并排展示。
- **优劣对比** —— `.pros-cons` 内含 `.pros` 和 `.cons` div，带有标题和列表。
- **原型元素** —— `.mock-nav`、`.mock-sidebar`、`.mock-content`、`.mock-button`、`.mock-input`、`.placeholder`。
- **排版** —— `h2`（页面标题）、`h3`（章节标题）、`.subtitle`、`.section`、`.label`。

## 设计技巧

- 根据问题调整保真度——布局问题用线框图，润色问题用高保真。
- 每页解释当前的问题。
- 每个屏幕最多 2-4 个选项。
- 保持原型简单。

## 文件命名

有语义的名称，永不重复使用，版本后缀（`layout-v2.html`）。服务器按修改时间提供最新文件。

## 清理

`scripts/stop-server.sh $SESSION_DIR`

使用 `--project-dir` 的会话持久化在 `.superpowers/brainstorm/` 中。仅 `/tmp` 会话在停止时删除。
