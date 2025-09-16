# Core agent loop

from pathlib import Path
from fern.core.planner import make_plan
from fern.tools.fs import snapshot_repo, apply_code_task
from fern.tools.shell import run_tests
from fern.tools.git import ensure_branch, git_commit_all

def operate(repo: Path, goal: str) -> dict:
    snap = snapshot_repo(repo)
    plan = make_plan(snap, goal)

    ensure_branch(repo, "fern/work")
    for t in plan["tasks"]:
        tool = t.get("tool")
        if tool in ("code","fs"):
            apply_code_task(repo, t)
        elif tool == "shell":
            run_tests(repo, t.get("args",{}).get("cmd","pytest -q"))
    git_commit_all(repo, f"fern: {goal}")
    return plan
