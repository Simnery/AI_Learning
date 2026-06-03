"""
从 .claude/config/config.local.json 同步配置到 CowAgent 的 config.json。
启动 CowAgent 前运行: python scripts/cowagent_sync_config.py
"""
import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_LOCAL = os.path.join(PROJECT_ROOT, ".claude", "config", "config.local.json")
COWAGENT_CONFIG = os.path.join(PROJECT_ROOT, "tools", "cowagent", "config.json")


def main():
    # 加载本地配置
    with open(CONFIG_LOCAL, "r", encoding="utf-8") as f:
        local = json.load(f)

    cow = local.get("cowagent", {})
    if not cow:
        print("[CowAgent] No cowagent section in config.local.json")
        return

    # 加载 CowAgent 配置模板
    with open(COWAGENT_CONFIG, "r", encoding="utf-8") as f:
        target = json.load(f)

    # 同步字段映射
    key_map = {
        "deepseek_api_key": "deepseek_api_key",
        "deepseek_api_base": "deepseek_api_base",
        "feishu_app_id": "feishu_app_id",
        "feishu_app_secret": "feishu_app_secret",
        "dingtalk_client_id": "dingtalk_client_id",
        "dingtalk_client_secret": "dingtalk_client_secret",
        "wecom_bot_id": "wecom_bot_id",
        "wecom_bot_secret": "wecom_bot_secret",
        "web_password": "web_password",
        "agent_workspace": "agent_workspace",
    }

    updated = 0
    for local_key, cow_key in key_map.items():
        value = cow.get(local_key, "")
        if value:
            # Resolve {项目根目录} placeholder to actual project root
            value = value.replace("{项目根目录}", PROJECT_ROOT.replace("\\", "/"))
            target[cow_key] = value
            updated += 1

    # 写入
    with open(COWAGENT_CONFIG, "w", encoding="utf-8") as f:
        json.dump(target, f, indent=2, ensure_ascii=False)

    print(f"[CowAgent] Synced {updated} config values → {COWAGENT_CONFIG}")


if __name__ == "__main__":
    main()
