# Learner wrapper

from fern.rl.experience import ExperienceStore
from fern.rl.bandit import ThompsonBandit
import time

class Learner:
    def __init__(self, db_path):
        self.store = ExperienceStore(db_path)
        self.bandit = ThompsonBandit()

    def select_action(self, context: dict) -> str:
        return self.bandit.select(context, ["retry_small_patch","retry_rewrite_file","run_formatter_then_patch"])

    def compute_reward(self, tests_pass: float, lint_ok: bool, type_ok: bool, human_fb: float, diff_ratio: float, retries_ratio: float) -> float:
        r = 0.6*tests_pass + 0.2*(1 if lint_ok else 0) + 0.1*(1 if type_ok else 0)
        r += 0.1*((human_fb+1)/2)
        r -= 0.05*diff_ratio
        r -= 0.05*retries_ratio
        return max(0.0, min(1.0, r))

    def record(self, repo: str, context: dict, action: str, result: dict, reward: float):
        ep = {"ts": time.time(), "repo": repo, "context": context, "action": action, "result": result, "reward": reward}
        self.store.add(ep)
        self.bandit.update(context, action, reward)
        return ep

    def recent(self, limit=50):
        return self.store.recent(limit)