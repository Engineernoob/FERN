from pathlib import Path
import typer, json, os
from rich.console import Console

from fern.core.agent import operate
from fern.tasks.scaffold import scaffold_project
from fern.tasks.implement import implement_spec
from fern.tasks.review import review_repo
from fern.tools.github import ensure_remote_repo, open_pr
from fern.tools.git import git_init, git_commit_all, git_push

console = Console()
app = typer.Typer(help="FERN: Full-stack Engineering Reinforcement Navigator")

@app.command()
def chat(path: str = "."):
    repo = Path(path)
    repo.mkdir(parents=True, exist_ok=True)
    console.print("[bold green]FERN:[/] 🌱 You can talk to me while I’m building your project.")

    history = []
    while True:
        try:
            user_input = console.input("[bold cyan]You:[/] ")
            if user_input.lower() in {"exit", "quit"}:
                console.print("[yellow]FERN:[/] Goodbye!")
                break

            history.append({"role": "user", "content": user_input})
            result = operate(repo, user_input)
            console.print(f"[magenta]FERN result:[/]\n{json.dumps(result, indent=2)}")
        except KeyboardInterrupt:
            console.print("\n[yellow]FERN:[/] Stopping session.")
            break

@app.command()
def scaffold(name: str, template: str = "py_lib", path: str = "."):
    project_dir = Path(path) / name
    project_dir.mkdir(parents=True, exist_ok=True)
    git_init(project_dir)
    scaffold_project(project_dir, template=template, name=name)
    git_commit_all(project_dir, "chore: scaffold project")
    console.print(f"[green]FERN:[/] Scaffolded {name} at {project_dir}")

@app.command()
def batch(plan: str = "fern.plan.json", path: str = "."):
    repo = Path(path)
    with open(plan) as f:
        goals = json.load(f)["goals"]

    for g in goals:
        console.print(f"[cyan]FERN:[/] Working on {g}")
        result = operate(repo, g)
        console.print(f"[magenta]Plan:[/]\n{result}")
        os.system("ruff check . --fix || true")
        os.system("pytest -q || true")
        git_commit_all(repo, f"fern: {g}")

@app.command()
def review(path: str = "."):
    review_repo(Path(path))

@app.command()
def sync(path: str = ".", private: bool = True):
    repo_url = ensure_remote_repo(Path(path), private=private)
    git_push(Path(path), "origin", "main")
    console.print(f"[green]FERN:[/] Pushed to {repo_url}")

@app.command()
def pr(title: str, body: str = "", path: str = "."):
    url = open_pr(Path(path), title, body)
    console.print(f"[green]FERN:[/] PR opened: {url}")

def main():
    print("FERN 🌱 is ready to help.")

if __name__ == "__main__":
    main()
    app()