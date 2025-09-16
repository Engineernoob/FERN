**/\\\\\\\\\\\\\\\_\_/\\\\\\\\\\\\\\\_\_**/\\\\\\\\\_**\_**/\\\\\_\_**_/\\\_  
 _\/\\\///////////**\/\\\///////////**\_/\\\///////\\\_**\/\\\\\\**_\/\\\_  
 _\/\\\_\*\***\_\_**\*\***\/\\\_\***\*\_\_\_\_\*\***\/\\\_\_**\_\/\\\_**\/\\\/\\\__\/\\\_  
 _\/\\\\\\\\\\\_\_**\_\/\\\\\\\\\\\_\_\_**\/\\\\\\\\\\\/\_**_\/\\\//\\\_\/\\\_  
 _\/\\\///////\_\_\_\_**\/\\\///////**\_\_**\/\\\//////\\\_**_\/\\\\//\\\\/\\\_  
 _\/\\\_\*\***\_\_**\*\***\/\\\_\***\*\_\_\_\_\*\***\/\\\_**\_\//\\\_**\/\\\_\//\\\/\\\_  
 \_\/\\\_\***\*\_\_\_\_\*\***\/\\\_\***\*\_\_\_\_\*\***\/\\\_\_**\_\//\\\_\_\/\\\__\//\\\\\\_  
 \_\/\\\_\*\***\_\_**\*\***\/\\\\\\\\\\\\\\\_\/\\\_**\_**\//\\\_\/\\\_**\//\\\\\_
\_\///\*\***\_\_\_\_**\*\***\///////////////**\///**\_\_\***\*\///**\///\_\_\_\*\*\/////\_\_

🌱 **FERN – Full-stack Engineering Reinforcement Navigator**  
_An autonomous, reinforcement-learning powered coding agent that plans, builds, reviews, and improves software projects while you sleep._

---

## ✨ Key Features

- **Chat-Driven Development** – talk to FERN in your terminal as it builds your project.
- **Autonomous Planning** – breaks high-level goals into structured tasks.
- **Self-Healing** – retries failed builds and applies different fix strategies.
- **Reinforcement Learning** – logs every attempt and improves over time.
- **GitHub Integration** – commits, branches, pushes, and opens PRs automatically.
- **Status & Reports** – track performance, test pass rates, and reward curves.

---

## 🛠️ Tech Stack

- Python 3.12+
- Ollama (`qwen2.5-coder:7b`)
- GitPython, Typer, Rich
- DuckDB (RL memory)
- Ruff, Pytest, Mypy

---

## 🚀 Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/fern.git
cd fern
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run Ollama
   ollama serve
   ollama pull qwen2.5-coder:7b

3. Start Chatting
   python -m fern.cli chat

Example session:

FERN 🌱 You can talk to me while I’m building your project.
You: scaffold a FastAPI backend with authentication
FERN: Planning...
FERN: Writing app/main.py
FERN: Running tests...
FERN: Fixed lint errors
FERN: ✅ Finished goal (reward=0.87)

📊 Tracking Progress

Last 5 runs:

python -m fern.cli status

Full report:

python -m fern.cli report

🌿 Roadmap

Multi-agent mode (Planner, Builder, Reviewer)

Persistent memory of past fixes & goals

Auto-generated GitHub PRs with test reports

Web dashboard with live logs & reward graphs

Support for multiple LLM providers

🤝 Contributing

FERN is experimental. Contributions, feedback, and ideas are welcome.

📜 License

MIT License © 2025 Taahirah Denmark

---
