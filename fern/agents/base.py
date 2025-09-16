# fern/agents/base.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Literal, Dict, Any, List
import time

Role = Literal["planner", "builder", "reviewer", "coordinator"]

@dataclass
class Msg:
    role: Role
    content: str
    meta: Dict[str, Any] | None = None
    ts: float = time.time()

    def to_dict(self):
        return asdict(self)

@dataclass
class Task:
    id: str
    desc: str
    tool: str # "code" | "fs"| "shell"| "github"
    args: Dict[str, Any]

@dataclass
class Plan:
    tasks: List[Task]
    
