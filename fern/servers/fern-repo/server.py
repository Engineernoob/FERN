from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.post("/clone_repo")
def clone_repo(url: str):
    subprocess.run(["git", "clone", url, "/repos/repo"], check=True)
    return {"success": True, "path": "/repos/repo"}

@app.post("/commit_and_push")
def commit_and_push(message: str):
    subprocess.run(["git", "add", "."], cwd="/repos/repo", check=True)
    subprocess.run(["git", "commit", "-m", message], cwd="/repos/repo", check=True)
    subprocess.run(["git", "push"], cwd="/repos/repo", check=True)
    return {"success": True}
