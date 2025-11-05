# Advanced Feature Planning - Cognitive Layer
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from fern.tools.llm import complete
from fern.tools.fs import snapshot_repo
from fern.tools.logger import log_info, log_progress

class FeaturePlan:
    def __init__(self, goal: str, subtasks: List[Subtask], priority: str = "medium"):
        self.goal = goal
        self.subtasks = subtasks
        self.priority = priority
        self.estimated_effort = sum(task.estimated_effort for task in subtasks)
        self.dependencies = self._extract_dependencies()
        
    def _extract_dependencies(self) -> List[str]:
        """Extract file and system dependencies from subtasks"""
        deps = set()
        for task in self.subtasks:
            if hasattr(task, 'file') and task.file:
                deps.add(task.file)
            if hasattr(task, 'dependencies') and task.dependencies:
                deps.update(task.dependencies)
        return list(deps)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "priority": self.priority,
            "estimated_effort": self.estimated_effort,
            "dependencies": self.dependencies,
            "subtasks": [task.to_dict() for task in self.subtasks]
        }

class Subtask:
    def __init__(self, id: str, description: str, tool: str, args: Dict[str, Any], 
                 estimated_effort: int = 1, dependencies: Optional[List[str]] = None,
                 risk_level: str = "low"):
        self.id = id
        self.description = description
        self.tool = tool
        self.args = args
        self.estimated_effort = estimated_effort
        self.dependencies = dependencies or []
        self.risk_level = risk_level
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "tool": self.tool,
            "args": self.args,
            "estimated_effort": self.estimated_effort,
            "dependencies": self.dependencies,
            "risk_level": self.risk_level
        }

PLAN_FEATURE_SYS = """You are Fern's advanced feature planner. Given a feature goal, break it into structured, executable subtasks.

Focus on:
1. Breaking complex goals into atomic, testable units
2. Identifying file paths and dependencies
3. Estimating effort and risk for each subtask
4. Considering test requirements and validation steps
5. Prioritizing tasks by dependency and risk

Return JSON in this exact format:
{
  "goal": "Original goal description",
  "priority": "high|medium|low",
  "subtasks": [
    {
      "id": "T1",
      "description": "Clear, actionable description",
      "tool": "code|fs|shell|github|test",
      "args": {
        "file": "optional file path",
        "content": "optional content",
        "cmd": "optional command",
        "test": "optional test specification"
      },
      "estimated_effort": 1-5,
      "dependencies": ["optional file paths"],
      "risk_level": "high|medium|low"
    }
  ]
}

Guidelines:
- Tasks should be small enough to complete in 30-60 minutes
- Include testing tasks for each major feature
- Consider code review and documentation tasks
- Account for setup/teardown requirements
- Include validation and verification steps"""

def plan_feature(goal: str, repo_path: Optional[Path] = None, max_chars: int = 20000) -> FeaturePlan:
    """
    Break a feature goal into structured, executable subtasks.
    
    Args:
        goal: The feature goal to plan
        repo_path: Optional path to repository for context
        max_chars: Maximum characters for repository snapshot
        
    Returns:
        FeaturePlan object with structured subtasks, dependencies, and metadata
    """
    log_progress(f"Planning feature: {goal}")
    
    # Get repository context if available
    repo_context = ""
    if repo_path and repo_path.exists():
        try:
            repo_context = snapshot_repo(repo_path, max_chars=max_chars)
            if repo_context:
                repo_context = f"Repository context:\n{repo_context[:10000]}\n\n"
        except Exception as e:
            log_info(f"Could not snapshot repository: {e}")
    
    prompt = f"""{repo_context}Feature Goal: {goal}

Break this goal into structured, executable subtasks. Consider the repository structure and dependencies.
Return only valid JSON."""
    
    try:
        response = complete(prompt, sys=PLAN_FEATURE_SYS)
        
        # More robust JSON extraction
        response = response.strip()
        
        # Try to find JSON-like structure
        json_start = response.find('{')
        json_end = response.rfind('}')
        
        if json_start != -1 and json_end != -1:
            json_str = response[json_start:json_end+1]
            
            # Clean common LLM artifacts
            json_str = json_str.replace('\\n', ' ').replace('\\t', ' ')
            json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)  # Remove control chars
            
            try:
                plan_data = json.loads(json_str)
                
                # Validate and create subtasks
                subtasks = []
                for task_data in plan_data.get("subtasks", []):
                    subtask = Subtask(
                        id=task_data.get("id", f"T{len(subtasks)+1}"),
                        description=task_data.get("description", ""),
                        tool=task_data.get("tool", "code"),
                        args=task_data.get("args", {}),
                        estimated_effort=task_data.get("estimated_effort", 1),
                        dependencies=task_data.get("dependencies", []),
                        risk_level=task_data.get("risk_level", "low")
                    )
                    subtasks.append(subtask)
                
                feature_plan = FeaturePlan(
                    goal=plan_data.get("goal", goal),
                    subtasks=subtasks,
                    priority=plan_data.get("priority", "medium")
                )
                
                log_info(f"Created feature plan with {len(subtasks)} subtasks")
                return feature_plan
                
            except json.JSONDecodeError as je:
                log_info(f"JSON parsing failed: {je}, using fallback")
                
    except Exception as e:
        log_info(f"Advanced planning failed: {e}")
    
    # Fallback to basic planning
    log_info("Falling back to basic task creation")
    return _create_basic_plan(goal)

def _create_basic_plan(goal: str) -> FeaturePlan:
    """Create a basic plan when advanced planning fails"""
    basic_subtask = Subtask(
        id="T1",
        description=f"Implement: {goal}",
        tool="code",
        args={},
        estimated_effort=3,
        risk_level="medium"
    )
    
    return FeaturePlan(
        goal=goal,
        subtasks=[basic_subtask],
        priority="medium"
    )