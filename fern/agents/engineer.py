import requests, subprocess
from pathlib import Path

OLLAMA_API = "http://ollama:11434/api/chat"   # Dev Mode: localhost
REPO_MCP = "http://localhost:8001"
TESTS_MCP = "http://localhost:8002"
DEPLOY_MCP = "http://localhost:8003"

WORKDIR = Path("/repos/repo")

def call_mcp(base_url, endpoint, payload):
    r = requests.post(f"{base_url}/{endpoint}", json=payload)
    r.raise_for_status()
    return r.json()

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

def engineer_loop(repo_url: str):
    print("🌀 Starting Fern Engineer Loop...")

    print("📥 Cloning repo...")
    call_mcp(REPO_MCP, "clone_repo", {"url": repo_url})

    print("🧪 Running tests...")
    test_res = call_mcp(TESTS_MCP, "run_pytest", {"path": str(WORKDIR)})
    print(test_res)

    if test_res["failed"] > 0:
        print("🐞 Failures found, generating fix...")
        patch = generate_patch_with_ollama("\n".join(test_res["errors"]))
        print("Proposed patch:\n", patch)

        with open(WORKDIR / "PATCH.diff", "w") as f:
            f.write(patch)

        subprocess.run(["git", "apply", "PATCH.diff"], cwd=WORKDIR, check=True)
        call_mcp(REPO_MCP, "commit_and_push", {"message": "Fern auto-fix"})
    else:
        print("✅ All tests passed!")

    print("🚀 Deploying to staging...")
    dep_res = call_mcp(DEPLOY_MCP, "deploy_app", {"env": "staging"})
    print(dep_res)

if __name__ == "__main__":
    engineer_loop("https://github.com/someuser/somerepo.git")
