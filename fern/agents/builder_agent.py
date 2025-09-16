# fern/agents/builder_agent.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
from fern.tools.fs import apply_code_task
from fern.tools.shell import run_cmd
from fern.tools.git import git_commit_all
from fern.tools.logger import log_progress, log_success

def execute_tasks(repo: Path, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = []
    for t in tasks:
        tool = t.get("tool")
        desc = t.get("desc", "")
        log_progress(f"Builder: {desc} ({tool})")
        if tool in ("code", "fs"):
            apply_code_task(repo, t)
            results.append({"id": t.get("id"), "ok": True})
        elif tool == "shell":
            cmd = t.get("args", {}).get("cmd", "pytest -q")
            rc = run_cmd(repo, cmd)
            results.append({"id": t.get("id"), "ok": rc == 0, "rc": rc})
        else:
            results.append({"id": t.get("id"), "ok": False, "reason": f"unknown tool {tool}"})
    git_commit_all(repo, "fern(builder): apply tasks")
    log_success("Builder: tasks applied & committed.")
    return {"results": results}
