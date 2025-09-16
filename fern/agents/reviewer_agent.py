# fern/agents/reviewer_agent.py
from __future__ import annotations
import json
from pathlib import Path
from fern.tools.shell import run_cmd
from fern.tools.logger import log_info, log_error
from fern.tools.llm import complete

REVIEW_SYS = """You are FERN's Reviewer.
Given test/lint/typecheck results, propose a small follow-up task list (JSON) to fix issues.
If everything passes, return {"tasks": []}.
JSON schema: {"tasks":[{"id":"R1","desc":"...","tool":"code|fs|shell","args":{}}]}"""

def run_quality_checks(repo: Path) -> dict:
    tests = run_cmd(repo, "pytest -q")
    lint  = run_cmd(repo, "ruff check .")
    typec = run_cmd(repo, "mypy .")
    ok = (tests == 0) and (lint == 0) and (typec == 0)
    return {"tests_ok": tests == 0, "lint_ok": lint == 0, "type_ok": typec == 0, "all_ok": ok}

def review_and_suggest(repo: Path, goal: str) -> dict:
    qc = run_quality_checks(repo)
    if qc["all_ok"]:
        log_info("Reviewer: all checks passed.")
        return {"quality": qc, "followups": {"tasks": []}}

    # build a compact textual report for the model
    report = json.dumps(qc)
    prompt = f"Goal: {goal}\nQuality report: {report}\nReturn JSON only."
    txt = complete(prompt, sys=REVIEW_SYS)
    try:
        follow = json.loads(txt)
    except Exception:
        follow = {"tasks": []}
    if not follow.get("tasks"):
        log_error("Reviewer: issues found but no follow-ups suggested by LLM.")
    return {"quality": qc, "followups": follow}
