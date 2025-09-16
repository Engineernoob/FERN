# Review tasks

from fern.tools.shell import run_cmd

def review_repo(repo):
    run_cmd(repo, "ruff format . || true")
    run_cmd(repo, "ruff check --fix . || true")
    run_cmd(repo, "pytest -q || true")
