# Repo state management
# Placeholder for project state tracking
# (e.g. fern could store repo metadata, backlog, progress here)
import json

def save_state(repo, state: dict):
    (repo / ".fern" / "state.json").write_text(json.dumps(state, indent=2))

def load_state(repo):
    import json
    path = repo / ".fern" / "state.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}
