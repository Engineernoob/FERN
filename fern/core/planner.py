# Planner logic
import json
from fern.tools.llm import complete
from fern.core.prompts import PLAN_SYS

def make_plan(repo_snapshot: str, goal: str) -> dict:
    prompt = f"Repo snapshot:\n{repo_snapshot}\n\nGoal:\n{goal}\n\nProduce plan JSON."
    text = complete(prompt, sys=PLAN_SYS)
    try:
        plan = json.loads(text)
        assert isinstance(plan.get("tasks"), list)
        return plan
    except Exception:
        return {"tasks":[{"id":"T0","desc":goal,"tool":"code","args":{}}]}