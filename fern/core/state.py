# Repo state management
# Placeholder for project state tracking
# (e.g. fern could store repo metadata, backlog, progress here)
import json
from pathlib import Path
from datetime import datetime

def history_file(repo: Path):
    return repo / ".fern" / "history.json"

def append_history(repo: Path, entry: dict):
    hf = history_file(repo)
    hist = []
    if hf.exists():
        hist = json.loads(hf.read_text())
    entry["ts"] = datetime.now().isoformat()
    hist.append(entry)
    hf.write_text(json.dumps(hist, indent=2))

def load_history(repo: Path):
    hf = history_file(repo)
    if hf.exists():
        return json.loads(hf.read_text())
    return []

def compute_stats(history: list[dict]) -> dict:
    if not history:
        return {"runs": 0, "avg_reward": 0.0, "tests_pass_rate": 0.0,
                "lint_pass_rate": 0.0, "type_pass_rate": 0.0, "last": None}

    runs = len(history)
    avg_reward = sum(h.get("reward", 0) for h in history) / runs
    tests_pass_rate = sum(1 for h in history if h.get("tests_pass")) / runs
    lint_pass_rate = sum(1 for h in history if h.get("lint_ok")) / runs
    type_pass_rate = sum(1 for h in history if h.get("type_ok")) / runs
    last = history[-1]

    return {
        "runs": runs,
        "avg_reward": avg_reward,
        "tests_pass_rate": tests_pass_rate,
        "lint_pass_rate": lint_pass_rate,
        "type_pass_rate": type_pass_rate,
        "last": last,
    }
