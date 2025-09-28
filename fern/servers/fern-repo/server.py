from mcp.server import Server
import subprocess, os

server = Server("fern-repo")

@server.endpoint("clone_repo")
def clone_repo(url: str):
    subprocess.run(["git", "clone", url, "/repos/repo"], check=True)
    return {"success": True, "path": "/repos/repo"}

@server.endpoint("commit_and_push")
def commit_and_push(message: str):
    subprocess.run(["git", "add", "."], cwd="/repos/repo", check=True)
    subprocess.run(["git", "commit", "-m", message], cwd="/repos/repo", check=True)
    subprocess.run(["git", "push"], cwd="/repos/repo", check=True)
    return {"success": True}

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
