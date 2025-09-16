# Fix strategies for RL
from fern.tools.llm import complete
from fern.tools.fs import snapshot_repo, write_file
import json

def apply_fix_strategy(repo, action: str, context: dict):
    snap = snapshot_repo(repo, max_chars=10000)
    sys = f"You are a code fixer. Strategy: {action}. Apply minimal safe changes."
    prompt = f"Goal: {context.get('goal')}\n\nErrors:\n{context.get('err_type')}\n\nSnapshot:\n{snap}\n\nReturn JSON: [{{'file':'path','content':'new file content'}}]"
    txt = complete(prompt, sys=sys)

    try:
        changes = json.loads(txt)
        for ch in changes:
            write_file(repo, ch["file"], ch["content"])
    except Exception as e:
        print(f"[fix-strategy] Failed to parse LLM output: {e}")

