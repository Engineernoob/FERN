from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class DeployRequest(BaseModel):
    env: str = "staging"

@app.post("/deploy_app")
def deploy_app(req: DeployRequest):
    return {"success": True, "url": f"https://{req.env}.fern-app.local"}

@app.post("/rollback")
def rollback(req: DeployRequest):
    return {"success": True}


