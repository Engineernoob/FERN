# Shell helpers
import subprocess, shlex
from pathlib import Path

def run_cmd(repo: Path, cmd: str) -> int:
    print(f"$ {cmd}")
    return subprocess.call(shlex.split(cmd), cwd=repo)

def run_tests(repo: Path, cmd: str = "pytest -q"):
    return run_cmd(repo, cmd)
