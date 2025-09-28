from mcp.server import Server

server = Server("fern-deploy")

@server.endpoint("deploy_app")
def deploy_app(env: str = "staging"):
    return {"success": True, "url": f"https://{env}.fern-app.local"}

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
