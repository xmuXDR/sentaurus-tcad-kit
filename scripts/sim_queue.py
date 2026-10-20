#!/usr/bin/env python3
"""Lightweight simulation queue tracker for Sentaurus TCAD work.

Records gsub submissions and their outcomes in a JSON state file.
This is an auxiliary log only -- it does NOT replace SWB .sta/.job
status or gsub itself.

Usage:
    python3 sim_queue.py add <node> <project> "description"
    python3 sim_queue.py done <node> "result"
    python3 sim_queue.py fail <node> "reason"
    python3 sim_queue.py status
    python3 sim_queue.py list

State file defaults to claude_tmp/sentaurus/sim_queue.json relative to
the current working directory; override with SIM_QUEUE_FILE env var.
"""

import json
import os
import sys
from datetime import datetime, timezone

STATUSES = ("pending", "done", "failed")


def state_path():
    override = os.environ.get("SIM_QUEUE_FILE")
    if override:
        return override
    return os.path.join("claude_tmp", "sentaurus", "sim_queue.json")


def load(path):
    if not os.path.exists(path):
        return {"entries": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = {"entries": []}
    if not isinstance(data, dict) or "entries" not in data:
        data = {"entries": []}
    return data


def save(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def find_entry(data, node):
    for e in data["entries"]:
        if str(e.get("node")) == str(node):
            return e
    return None


def cmd_add(args):
    if len(args) < 2:
        sys.exit("usage: sim_queue.py add <node> <project> [description]")
    node, project = args[0], args[1]
    desc = args[2] if len(args) > 2 else ""
    path = state_path()
    data = load(path)
    entry = find_entry(data, node)
    if entry is None:
        entry = {"node": str(node), "history": []}
        data["entries"].append(entry)
    entry.update({
        "node": str(node),
        "project": project,
        "description": desc,
        "status": "pending",
        "submitted_at": now(),
        "finished_at": None,
        "note": None,
    })
    entry["history"].append({"event": "add", "time": now(), "detail": desc})
    save(path, data)
    print(f"added node {node} ({project}) -> {path}")


def cmd_finish(args, status):
    if len(args) < 1:
        sys.exit(f"usage: sim_queue.py {status} <node> [note]")
    node = args[0]
    note = args[1] if len(args) > 1 else ""
    path = state_path()
    data = load(path)
    entry = find_entry(data, node)
    if entry is None:
        sys.exit(f"node {node} not found in queue; use add first")
    entry["status"] = status
    entry["finished_at"] = now()
    entry["note"] = note
    entry["history"].append({"event": status, "time": now(), "detail": note})
    save(path, data)
    print(f"node {node} marked {status}")


def cmd_status(_args):
    path = state_path()
    data = load(path)
    entries = data["entries"]
    if not entries:
        print(f"(empty queue: {path})")
        return
    counts = {s: 0 for s in STATUSES}
    for e in entries:
        counts[e.get("status", "pending")] = counts.get(e.get("status", "pending"), 0) + 1
    print(f"queue: {path}")
    print("  pending={pending} done={done} failed={failed}".format(**counts))
    pending = [e for e in entries if e.get("status") == "pending"]
    if pending:
        print("pending nodes:")
        for e in pending:
            print(f"  n{e['node']}  {e.get('project', '')}  {e.get('description', '')}  submitted {e.get('submitted_at', '')}")


def cmd_list(_args):
    path = state_path()
    data = load(path)
    entries = data["entries"]
    if not entries:
        print(f"(empty queue: {path})")
        return
    print(f"queue: {path}")
    for e in entries:
        line = f"[{e.get('status', '?'):7}] n{e.get('node')}  {e.get('project', '')}  {e.get('description', '')}"
        if e.get("finished_at"):
            line += f"  finished {e['finished_at']}"
        if e.get("note"):
            line += f"  note: {e['note']}"
        print(line)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    action = sys.argv[1]
    args = sys.argv[2:]
    if action == "add":
        cmd_add(args)
    elif action == "done":
        cmd_finish(args, "done")
    elif action == "fail":
        cmd_finish(args, "failed")
    elif action == "status":
        cmd_status(args)
    elif action == "list":
        cmd_list(args)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
