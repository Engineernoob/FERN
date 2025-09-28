from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

app = FastAPI()

class RunPytestRequest(BaseModel):
    path: str = "/repos/repo"

@app.post("/run_pytest")
def run_pytest(req: RunPytestRequest):
    result = subprocess.run(
        ["pytest", req.path, "-q", "--tb=short"],
        capture_output=True, text=True
    )
    output = result.stdout + result.stderr
    passed = output.count("PASSED")
    failed = output.count("FAILED")
    errors = [line for line in output.splitlines() if "E   " in line]
    return {"passed": passed, "failed": failed, "errors": errors}

