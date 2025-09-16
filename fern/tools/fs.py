# Filesystem utilities
from pathlib import Path

def snapshot_repo(repo: Path, max_chars: int = 40000) -> str:
    parts = []
    for p in repo.rglob("*"):
        if p.is_file() and p.stat().st_size < 200*1024 and "venv" not in p.parts and ".git" not in p.parts:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                parts.append(f"--- {p.relative_to(repo)} ---\n{text}\n")
            except Exception:
                pass
        if sum(len(x) for x in parts) > max_chars: break
    return "\n".join(parts)

def write_file(repo: Path, rel: str, content: str):
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def apply_code_task(repo: Path, task: dict):
    args = task.get("args", {})
    if "file" in args and "content" in args:
        write_file(repo, args["file"], args["content"])
