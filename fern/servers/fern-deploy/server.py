from fastapi import FastAPI

app = FastAPI()

@app.post("/deploy_app")
def deploy_app(env: str = "staging"):
    return {"success": True, "url": f"https://{env}.fern-app.local"}

@app.post("/rollback")
def rollback(env: str = "staging"):
    return {"success": True}

