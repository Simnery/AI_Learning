"""
桥接处理器 — 读取 commands.jsonl 中未处理的指令，执行，写入 results.jsonl。

由 0005_cowagent skill 或用户手动触发。
用法: python scripts/bridge_process.py
"""
import json
import os
import subprocess
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE_DIR = os.path.join(PROJECT_ROOT, "00_local_task", "cowagent_workspace", "bridge")
COMMANDS_FILE = os.path.join(BRIDGE_DIR, "commands.jsonl")
RESULTS_FILE = os.path.join(BRIDGE_DIR, "results.jsonl")
PROCESSED_FILE = os.path.join(BRIDGE_DIR, "processed.txt")


def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def mark_processed(cmd_id: str):
    with open(PROCESSED_FILE, "a") as f:
        f.write(cmd_id + "\n")


def write_result(cmd_id: str, status: str, output: str):
    entry = {
        "id": cmd_id,
        "time": datetime.now().isoformat(),
        "status": status,
        "output": output,
    }
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def execute_command(command: str) -> tuple[str, str]:
    """Execute a shell command in the project root."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=PROJECT_ROOT,
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            error = result.stderr.strip()
            output = output + ("\n" + error if error else "")
            return ("error", output or f"exit code: {result.returncode}")
        return ("ok", output or "(无输出)")
    except subprocess.TimeoutExpired:
        return ("error", "命令超时 (60s)")
    except Exception as e:
        return ("error", str(e))


def main():
    if not os.path.exists(COMMANDS_FILE):
        print("[Bridge] 暂无企微指令")
        return

    processed = load_processed()
    pending = []

    with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                cmd = json.loads(line)
                if cmd["id"] not in processed:
                    pending.append(cmd)
            except json.JSONDecodeError:
                continue

    if not pending:
        print("[Bridge] 暂无新指令")
        return

    print(f"[Bridge] 发现 {len(pending)} 条待处理指令:\n")
    for cmd in pending:
        print(f"  [{cmd['id']}] {cmd['user']}: {cmd['command']}")
        status, output = execute_command(cmd["command"])
        write_result(cmd["id"], status, output)
        mark_processed(cmd["id"])
        icon = "✅" if status == "ok" else "❌"
        print(f"  {icon} {output[:200]}")
        print()

    print(f"[Bridge] 全部处理完成，共 {len(pending)} 条")


if __name__ == "__main__":
    main()
