# GitHub integration
import os
from pathlib import Path
from github import Github
from git import Repo


def _gh():
    return Github(os.environ["GITHUB_TOKEN"])

def ensure_remote_repo(repo_dir: Path, private: bool = True) -> str:
    user = os.environ["GITHUB_USER"]
    name = repo_dir.name
    gh = _gh()
    u = gh.get_user()  # Authenticated user
    try:
        r = u.get_repo(name)
    except:
        r = u.create_repo(name, private=private, auto_init=False)  # type: ignore[attr-defined]
    repo = Repo.init(repo_dir)
    url = f"https://github.com/{user}/{name}.git"
    repo.create_remote("origin", url)
    return url

def open_pr(repo_dir: Path, title: str, body: str = "") -> str:
    repo = Repo(repo_dir)
    base = "main"
    head = repo.active_branch.name
    user = os.environ["GITHUB_USER"]
    gh = _gh()
    gr = gh.get_user(user).get_repo(repo_dir.name)
    pr = gr.create_pull(title=title, body=body, base=base, head=head if "/" in head else f"{user}:{head}")
    return pr.html_url

