# Git integration
from pathlib import Path
from git import Repo

def git_init(repo_dir: Path):
    if (repo_dir / ".git").exists():
        return
    Repo.init(repo_dir).index.commit("chore: initial")

def ensure_branch(repo_dir: Path, name: str):
    repo = Repo(repo_dir)
    if repo.active_branch.name != name:
        if name in repo.branches:
            repo.git.checkout(name)
        else:
            repo.git.checkout("-b", name)

def git_commit_all(repo_dir: Path, msg: str):
    repo = Repo(repo_dir)
    repo.git.add(A=True)
    if repo.is_dirty():
        repo.index.commit(msg)

def git_push(repo_dir: Path, remote: str, branch: str):
    repo = Repo(repo_dir)
    repo.git.push("--set-upstream", remote, branch)