from mcp.server import Server
import subprocess

server = Server("fern-tests")

@server.endpoint("run_pytest")
def run_pytest(path: str = "/repos/repo"):
    result = subprocess.run(["pytest", path, "-q", "--tb=short"],
                            capture_output=True, text=True)
    output = result.stdout + result.stderr
    passed = output.count("PASSED")
    failed = output.count("FAILED")
    errors = [line for line in output.splitlines() if "E   " in line]
    return {"passed": passed, "failed": failed, "errors": errors}

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
