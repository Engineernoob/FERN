# Core agent loop
from pathlib import Path
import time, json
from fern.core.planner import make_plan
from fern.tools.fs import snapshot_repo, apply_code_task
from fern.tools.shell import run_tests
from fern.tools.git import ensure_branch, git_commit_all
from fern.rl.learner import Learner
from fern.tools.fix_strategies import apply_fix_strategy
from fern.tools.logger import log_info, log_success, log_error, log_progress
from fern.core.state import append_history


def operate(repo: Path, goal: str) -> dict:
    """
    One execution of a goal:
    - Snapshot + plan
    - Apply tasks
    - Run checks
    - Apply fix strategy if needed
    - Commit & record reward
    """
    start = time.time()
    repo.mkdir(exist_ok=True)
    (repo / ".fern").mkdir(exist_ok=True)

    log_progress(f"Starting goal: {goal}")

    # 1. Snapshot + Plan
    snap = snapshot_repo(repo)
    log_info("Creating plan...")
    plan = make_plan(snap, goal)

    ensure_branch(repo, "fern/work")
    results = []
    learner = Learner(db_path=repo / ".fern" / "experience.duckdb")

    # 2. Execute tasks
    for t in plan["tasks"]:
        tool = t.get("tool")
        desc = t.get("desc")
        log_progress(f"Running task: {desc} ({tool})")
        if tool in ("code", "fs"):
            apply_code_task(repo, t)
        elif tool == "shell":
            run_tests(repo, t.get("args", {}).get("cmd", "pytest -q"))
        results.append(t)

    # 3. Run checks
    log_info("Running checks...")
    tests_pass = run_tests(repo, "pytest -q") == 0
    lint_ok = run_tests(repo, "ruff check .") == 0
    type_ok = run_tests(repo, "mypy .") == 0

    if tests_pass and lint_ok and type_ok:
        log_success("All checks passed ✅")
    else:
        (log_error if not tests_pass else log_progress)("Issues detected, applying fix strategy...")

    # 4. Reward
    reward = learner.compute_reward(
        tests_pass=float(tests_pass),
        lint_ok=lint_ok,
        type_ok=type_ok,
        human_fb=0.0,
        diff_ratio=0.1,
        retries_ratio=0.0,
    )

    # 5. Fix if needed
    if not (tests_pass and lint_ok and type_ok):
        ctx = {"goal": goal, "err_type": "tests" if not tests_pass else "lint"}
        action = learner.select_action(ctx)
        log_info(f"Selected fix strategy: {action}")
        apply_fix_strategy(repo, action, ctx)

    # 6. Record & Commit
    learner.record(str(repo), {"goal": goal}, "plan", {"results": results}, reward)
    git_commit_all(repo, f"fern: {goal}")

    result = {
        "goal": goal,
        "tasks": results,
        "tests_pass": tests_pass,
        "lint_ok": lint_ok,
        "type_ok": type_ok,
        "reward": reward,
        "elapsed": round(time.time() - start, 2),
    }

    # 7. Save run history
    append_history(repo, result)

    log_success(f"Finished goal: {goal} (reward={reward:.2f})")
    return result


def run_goal(repo: Path, goal: str, max_retries: int = 3) -> dict:
    """
    Run a goal with retries + self-healing.
    """
    attempt = 0
    result = {}

    while attempt < max_retries:
        attempt += 1
        log_info(f"Attempt {attempt}/{max_retries} for goal: {goal}")
        result = operate(repo, goal)

        if result["tests_pass"] and result["lint_ok"] and result["type_ok"]:
            log_success(f"Goal succeeded on attempt {attempt} ✅")
            break
        else:
            log_error(f"Attempt {attempt} failed. Retrying... 🔁")

    return result
