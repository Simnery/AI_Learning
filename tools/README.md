# 外部工具集

通过 git submodule 管理的上游参考仓库。

## Superpowers

- 来源: [obra/superpowers](https://github.com/obra/superpowers) (MIT, 93K+ stars)
- 用途: 上游 Skill 源码参考，用于 `0004_superpowers` 增量同步
- 当前 commit: `6fd4507` (2026-05-29)

### 同步本地 Skill

```bash
# 查看上游变更
cd tools/superpowers && git pull
git diff <旧commit>..HEAD -- skills/

# 按 rule_skill_integration.md 步骤 9 适配
```

## CowAgent

- 来源: [zhayujie/cowagent](https://github.com/zhayujie/cowagent) (MIT)
- 用途: 多渠道 IM → AI 远程接入平台
- 当前 commit: `79323358` (2026-06-03)

### 初始化

```bash
git submodule update --init --depth 1
cd tools/cowagent && python -m pip install -r requirements.txt
python scripts/cowagent_sync_config.py
```

### 更新

```bash
git submodule update --remote tools/cowagent
python scripts/cowagent_sync_config.py
```

### 配置

API Key 在 `.claude/config/config.local.json` → `cowagent` 段统一管理。
