from pathlib import Path
import typer, json, os
from rich.console import Console

from fern.core.agent import run_goal   # 👈 use run_goal instead of operate
from fern.tasks.scaffold import scaffold_project
from fern.tasks.review import review_repo
from fern.tools.github import ensure_remote_repo, open_pr
from fern.tools.git import git_init, git_commit_all, git_push
from fern.core.state import load_history, compute_stats


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
            # 🔁 now uses retry + self-healing
            result = run_goal(repo, user_input, max_retries=3)
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
        # 🔁 now uses retry + self-healing
        result = run_goal(repo, g, max_retries=3)
        console.print(f"[magenta]Plan result:[/]\n{json.dumps(result, indent=2)}")
        os.system("ruff check . --fix || true")
        os.system("pytest -q || true")
        git_commit_all(repo, f"fern: {g}")

@app.command()
def status(path: str = "."):
    repo = Path(path)
    hist = load_history(repo)
    if not hist:
        console.print("[yellow]FERN:[/] No history found.")
        return
    console.print("[bold green]🌱 FERN Status [/]")
    for h in hist[-5:]:
        console.print(f"• {h['ts']}: {h['goal']} -> reward {h.get('reward', 0):.2f}")

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

@app.command()
def report(path: str = "."):
    repo = Path(path)
    hist = load_history(repo)
    stats = compute_stats(hist)
    
    if stats["runs"] == 0:
        console.print("[yellow]FERN:[/] No runs yet.")
        return
    console.print("[bold green]🌱 FERN Report [/]")
    console.print(f"Total runs: {stats['runs']}")
    console.print(f"Average reward: {stats['avg_reward']:.2f}")
    console.print(f"Tests pass rate: {stats['tests_pass_rate']*100:.1f}%")
    console.print(f"Lint pass rate: {stats['lint_pass_rate']*100:.1f}%")
    console.print(f"Typecheck pass rate: {stats['type_pass_rate']*100:.1f}%")

    last = stats["last"]
    console.print("\n[bold cyan]Last run:[/]")
    console.print(f"  Goal: {last['goal']}")
    console.print(f"  Reward: {last['reward']:.2f}")
    console.print(f"  Tests: {'✅' if last['tests_pass'] else '❌'}")
    console.print(f"  Lint: {'✅' if last['lint_ok'] else '❌'}")
    console.print(f"  Typecheck: {'✅' if last['type_ok'] else '❌'}")
    console.print(f"  Time: {last['ts']}")

def main():
    print("FERN 🌱 is ready to help.")

if __name__ == "__main__":
    main()
    app()
