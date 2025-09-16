from __future__ import annotations
import json
from pathlib import Path
from typing import List
from fern.tools.llm import complete
from fern.tools.fs import snapshot_repo
from fern.tools.logger import log_info
from fern.agents.base import Plan, Task

PLAN_SYS = """You are FERN's Planner.
Break the goal into small, ordered tasks with explicit filenames and tools.
Respond ONLY with JSON:
{"tasks":[{"id":"T1","desc":"...","tool":"code|fs|shell|github","args":{"file":"...","content":"...","cmd":"..."}}]}"""

def plan_for_goal(repo: Path, goal: str, max_chars: int = 20000) -> Plan:
    snap = snapshot_repo(repo, max_chars=max_chars)
    prompt = f"Repo snapshot:\n{snap}\n\nGoal:\n{goal}\n\nReturn JSON only."
    txt = complete(prompt, sys=PLAN_SYS)
    try:
        obj = json.loads(txt)
        tasks: List[Task] = [Task(**t) for t in obj.get("tasks", [])]
        if not tasks:
            tasks = [Task(id="T0", desc=goal, tool="code", args={})]
        log_info(f"Planner produced {len(tasks)} task(s).")
        return Plan(tasks=tasks)
    except Exception:
        return Plan(tasks=[Task(id="T0", desc=goal, tool="code", args={})])