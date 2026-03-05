
🌱 **FERN – Full-stack Engineering Reinforcement Navigator**

An autonomous, MCP-powered, reinforcement-learning coding agent that plans, builds, reviews, and improves software projects while you sleep.

✨ **Key Features**

Chat-Driven Development – interact with FERN in your terminal or via APIs.

Autonomous Planning – decomposes high-level goals into structured tasks.

Self-Healing – retries failed builds and applies alternate fix strategies.

Reinforcement Learning – logs every attempt and improves with memory (DuckDB + vector DB).

MCP Architecture – modular servers for repo management, testing, and deployment.

GitHub Integration – commits, branches, pushes, and opens PRs automatically.

Status & Reports – track performance, test pass rates, and reward curves.

🛠️ Tech Stack

Core: Python 3.12+

LLMs: Ollama (qwen2.5-coder:7b/14b, phi3, codellama)

Agents: Typer, Rich (CLI), Requests

MCP Servers:

fern-repo → git clone/commit/push/PR

fern-tests → pytest & e2e test harness

fern-deploy → CI/CD hooks & rollbacks

RL Memory: DuckDB + (future) Qdrant for long-term memory

Tooling: Ruff, Pytest, Mypy

🚀 Getting Started
1. Clone & Install (Dev Mode)
git clone https://github.com/yourusername/fern.git
cd fern-v2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. Run Dev Mode (local agents + Docker MCP)
docker compose -f docker-compose.dev.yml up -d
python agents/engineer.py


Ollama runs in Docker (http://localhost:11434)

MCP Servers (fern-repo, fern-tests, fern-deploy) run in Docker

Agent runs on your host → hot reload & fast iteration

3. Run Prod Mode (fully containerized)
docker compose -f docker-compose.prod.yml up --build


All services run in Docker (agents + MCP servers + Ollama)

Fern becomes portable & demo-ready

Great for open-source contributors or SaaS deployment

🌿 Roadmap

 MCP servers (fern-repo, fern-tests, fern-deploy)

 Dual run modes (Dev + Prod)

 Multi-agent mode (Planner, Builder, Reviewer, DevOps)

 Persistent memory of past fixes & goals (DuckDB → Qdrant)

 Auto-generated GitHub PRs with annotated test reports

 Web dashboard with live logs & reward graphs

 Support for multiple LLM providers (Ollama, OpenAI, Anthropic)

📊 Tracking Progress
python -m fern.cli status   # last 5 runs
python -m fern.cli report   # full RL report


FERN 🌱 Example log:

Planning...
Writing app/main.py
Running tests...
Fixed lint errors
✅ Finished goal (reward=0.87)

🤝 Contributing

FERN is experimental. Contributions, bug reports, and feedback are welcome.

📜 License

MIT License © 2025 Taahirah Denmark
