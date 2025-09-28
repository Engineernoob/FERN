from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

app = FastAPI()

class CloneRepoRequest(BaseModel):
    url: str

class CommitRequest(BaseModel):
    message: str

@app.post("/clone_repo")
def clone_repo(req: CloneRepoRequest):
    subprocess.run(["git", "clone", req.url, "/repos/repo"], check=True)
    return {"success": True, "path": "/repos/repo"}

@app.post("/commit_and_push")
def commit_and_push(req: CommitRequest):
    subprocess.run(["git", "add", "."], cwd="/repos/repo", check=True)
    subprocess.run(["git", "commit", "-m", req.message], cwd="/repos/repo", check=True)
    subprocess.run(["git", "push"], cwd="/repos/repo", check=True)
    return {"success": True}
