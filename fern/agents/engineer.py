import requests, subprocess
from pathlib import Path

# In Dev Mode: localhost ports (docker-compose.dev.yml)
OLLAMA_API = "http://localhost:11434/api/chat"
REPO_MCP = "http://localhost:8001"
TESTS_MCP = "http://localhost:8002"
DEPLOY_MCP = "http://localhost:8003"

WORKDIR = Path("/repos/repo")

# ---- MCP Client Helpers ----
def call_mcp(base_url, endpoint, payload=None):
    """Send JSON payload to MCP endpoint"""
    url = f"{base_url}/{endpoint}"
    r = requests.post(url, json=payload or {})
    r.raise_for_status()
    return r.json()

# ---- Ollama Client ----
def generate_patch_with_ollama(errors: str, model: str = "qwen2.5-coder:14b"):
    prompt = f"""
    Repo has test failures:

    {errors}

    Suggest a minimal Python code patch to fix.
    Return ONLY the code changes in unified diff format.
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert Python engineer."},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    resp = requests.post(OLLAMA_API, json=payload)
    resp.raise_for_status()
    return resp.json()["message"]["content"]

# ---- Engineer Loop ----
def engineer_loop(repo_url: str):
    print("🌀 Starting Fern Engineer Loop...")

    # 1. Clone repo
    print("📥 Cloning repo...")
    call_mcp(REPO_MCP, "clone_repo", {"url": repo_url})

    # 2. Run tests
    print("🧪 Running tests...")
    test_res = call_mcp(TESTS_MCP, "run_pytest", {"path": str(WORKDIR)})
    print(test_res)

    # 3. Fix if needed
    if test_res["failed"] > 0:
        print("🐞 Failures found, generating fix with Ollama...")
        errors = "\n".join(test_res["errors"])
        patch = generate_patch_with_ollama(errors)
        print("Proposed patch:\n", patch)

        # Save + apply patch
        patch_file = WORKDIR / "PATCH.diff"
        with open(patch_file, "w") as f:
            f.write(patch)

        subprocess.run(["git", "apply", str(patch_file)], cwd=WORKDIR, check=True)

        # Commit + push
        call_mcp(REPO_MCP, "commit_and_push", {"message": "Fern auto-fix"})
    else:
        print("✅ All tests passed!")

    # 4. Deploy
    print("🚀 Deploying to staging...")
    dep_res = call_mcp(DEPLOY_MCP, "deploy_app", {"env": "staging"})
    print(dep_res)

if __name__ == "__main__":
    engineer_loop("https://github.com/someuser/somerepo.git")

