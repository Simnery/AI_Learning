# 外部 Skill 集成规则

> 将外部开源 Skill 仓库深度适配到本项目的标准化流程。
> 来源：`obra/superpowers` 14 个 Skill 集成实战经验沉淀。
> 创建日期：2026-06-03

## 10 步决策链

按顺序执行，每步完成后才能进入下一步。**命名变更和引用同步必须在同一批次完成。**

### 0. 版本锚定

- [ ] 记录上游仓库 URL
- [ ] 记录当前集成 commit SHA
- [ ] 判断集成方式：逐文件拉取 / git clone
- [ ] 写入 README.md 版本追踪表

**输出:** 可追溯的版本锚点

### 1. 来源评估

- [ ] 确认开源协议（MIT/Apache/其他）
- [ ] 评估 Skill 总数和规模
- [ ] 检查外部依赖（脚本、工具、平台特定代码）
- [ ] 评估上游维护活跃度

**输出:** ✅ 可集成 / ⚠️ 需评估 / ❌ 不建议集成

### 2. 格式分析

- [ ] 读取 2-3 个代表性 SKILL.md
- [ ] 提取格式特征：frontmatter 字段、正文结构、约束机制
- [ ] 识别特殊元素：HARD-GATE / checklist / process flow / anti-pattern

**输出:** 上游 Skill 格式特征清单

### 3. 差异矩阵

对比维度：
- 文件路径、命名规则、frontmatter 字段
- 约束机制（HARD-GATE vs 占位符）
- 链式调用约定
- 语言（英文 vs 中文）
- 平台依赖

**输出:** 差异矩阵（16 维标准模板）

### 4. 分批策略

| 批次 | 内容 | 原则 |
|------|------|------|
| 第 1 批 | 核心工作流链 (3-4 个) | 最小闭环，先跑通 |
| 第 2 批 | 质量层 (4-5 个) | 增量增强 |
| 第 3 批 | 适配层 (其余) | 深度适配，可裁剪 |

**输出:** 分批执行计划

### 5. 命名适配

父 Skill 命名: `NNNN_功能名`（4 位数字前缀，按 `0004_superpowers` 递增）
子 Skill 命名: `0NN_原kebab-case名`（按工作流顺序编号）

```bash
# 示例
mv superpowers/brainstorming → 0004_superpowers/001_brainstorming
mv superpowers/writing-plans → 0004_superpowers/002_writing-plans
```

**输出:** 重命名后的完整目录结构

### 6. 引用同步（与步骤 5 同一批次）

<HARD-GATE>
命名变更和引用同步必须在同一批次完成。分批执行会导致链路断裂。
</HARD-GATE>

**必须更新引用的位置：**

| # | 位置 | 模式 |
|---|------|------|
| 1 | 所有子 SKILL.md 链式引用 | `superpowers:xxx` → `0004_superpowers:0NN_xxx` |
| 2 | 所有子 SKILL.md 路径引用 | `.claude/skills/superpowers/` → `.claude/skills/0004_superpowers/0NN_xxx/` |
| 3 | CLAUDE.md §1.1 表格 + 工作流链 | 全文搜索替换 |
| 4 | README.md 父目录索引 | 全表更新 |
| 5 | 任务文档路径引用 | 如有引用需同步 |

**验证:**
```bash
grep -rn "旧路径" .claude/ --include="*.md"
# 预期: 只有逻辑路径（如 docs/superpowers/specs/）可保留
```

**输出:** 零断裂的引用链

### 7. 内容本地化

| 部分 | 处理 |
|------|------|
| 标题/H1 | **保留英文原意** (如 Test-Driven Development) |
| 术语 | **保留英文** (TDD, HARD-GATE, YAGNI, subagent, worktree) |
| 正文说明 | 翻译为中文 |
| 代码块/命令/文件路径 | **保留原文不变** |
| frontmatter `description` | 翻译为中文 |
| frontmatter `name` | 保留英文 |
| HARD-GATE 块内容 | 翻译为中文 |
| 表格内容 | 翻译为中文 |

**术语不翻译原则:** 英文术语在软件工程中更通用，翻译会造成理解偏差。正文中文化是为了降低阅读门槛，术语保留英文是为了精确性。

### 8. 桥接建立

- [ ] 确认与 `0002_task-create` 的桥接规则已写入 CLAUDE.md
- [ ] 路径映射规则：逻辑路径 (Skill 中保留) → 实际路径 (任务目录)
- [ ] 前置检查规则：调用前确认 active 任务
- [ ] 后置同步规则：完成后更新任务文档 6 处

### 9. 上游同步

- [ ] 每批集成完成后：`git diff <锚定SHA>..HEAD -- skills/`
- [ ] 识别变更类型：新增 Skill / 修改 Skill / 删除 Skill
- [ ] 变更适配流程：
  - 新增 → 走步骤 1-8 完整流程
  - 修改 → diff 对比 → 合并正文 + 保留本地化
  - 删除 → 评估是否影响工作流链
- [ ] 更新版本锚定 SHA

## 常见陷阱

| 陷阱 | 预防 |
|------|------|
| 命名变更后漏更新引用 | 步骤 5+6 强制同批次，用 grep 验证 |
| 中文化时术语被翻译 | 步骤 7 强制术语保留英文 |
| 分批时忘记验证链路 | 每批完成后执行引用搜索 |
| 忘记记录版本锚点 | 步骤 0 先于一切 |
| 输出文件路径未映射到任务目录 | 步骤 8 桥接规则约束 |

## 参考实例

本次 Superpower 集成完整记录：
- 任务文档：`00_local_task/tasks/2026-06-03_项目实战_Superpower技能集成/`
- 上游 commit：`6fd4507659784c351abbd2bc264c7162cfd386dc` (2026-05-29)
- 最终产出：`.claude/skills/0004_superpowers/` (14 子 Skill + 父 Skill)
