# fern/agents/coordinator.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from fern.agents.planner_agent import plan_for_goal
from fern.agents.builder_agent import execute_tasks
from fern.agents.reviewer_agent import review_and_suggest
from fern.tools.logger import log_info, log_success, log_error

def run_multi_agent(repo: Path, goal: str, max_rounds: int = 3) -> Dict[str, Any]:
    """
    Each round:
      1) Planner proposes tasks
      2) Builder executes
      3) Reviewer checks; may propose follow-ups
    Terminates early if Reviewer says all_ok.
    """
    summary = {"goal": goal, "rounds": []}
    for r in range(1, max_rounds + 1):
        log_info(f"Coordinator: round {r}/{max_rounds}")

        # 1) plan
        plan = plan_for_goal(repo, goal)
        round_rec: Dict[str, Any] = {"round": r, "plan": [t.__dict__ for t in plan.tasks]}

        # 2) build
        build = execute_tasks(repo, round_rec["plan"])
        round_rec["build"] = build

        # 3) review
        review = review_and_suggest(repo, goal)
        round_rec["review"] = review
        summary["rounds"].append(round_rec)

        if review["quality"]["all_ok"]:
            log_success("Coordinator: success — all checks passed.")
            break

        # if reviewer suggested follow-ups, append to goal for the next pass (simple heuristic)
        tasks = review.get("followups", {}).get("tasks", [])
        if tasks:
            # Convert follow-ups to a textual “goal extension”
            extra = "; ".join(t.get("desc", "") for t in tasks)
            goal = f"{goal} (follow-ups: {extra})"
        else:
            log_error("Coordinator: stuck — no follow-ups suggested. Stopping.")
            break

    return summary
