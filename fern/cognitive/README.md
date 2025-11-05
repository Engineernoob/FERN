# Fern Cognitive Planning Layer

A sophisticated cognitive planning layer for the Fern development automation system that provides intelligent, context-aware development assistance through four core functions.

## Overview

The Cognitive Planning Layer enhances Fern's capabilities by providing advanced reasoning functions that analyze repositories, plan features, detect changes, and prioritize tasks. These functions work together to provide a comprehensive development workflow that thinks like an experienced engineer.

## Core Functions

### 1. `/plan_feature` - Intelligent Feature Planning
Breaks complex feature goals into structured, executable subtasks with dependencies, effort estimates, and risk assessments.

**Features:**
- Context-aware planning using repository structure
- Automatic dependency detection
- Effort estimation (1-5 scale)
- Risk assessment (low/medium/high)
- Test integration planning
- Prioritized task ordering

**Usage:**
```python
from fern.cognitive import plan_feature
from pathlib import Path

# Plan a feature for a specific repository
goal = "Add user authentication with JWT tokens"
plan = plan_feature(goal, Path("./my-project"), max_chars=20000)

print(f"Goal: {plan.goal}")
print(f"Subtasks: {len(plan.subtasks)}")
print(f"Total effort: {plan.estimated_effort}")
for task in plan.subtasks:
    print(f"  - {task.id}: {task.description} ({task.tool})")
```

### 2. `/analyze_repo` - Repository Intelligence
Comprehensive analysis of repository structure, dependencies, frameworks, and complexity to understand project context.

**Features:**
- Automatic language and framework detection
- Dependency extraction and analysis
- File structure analysis
- Complexity scoring (low/medium/high)
- README analysis and summarization
- Purpose inference
- Key file identification

**Usage:**
```python
from fern.cognitive import analyze_repo
from pathlib import Path

# Analyze a repository
analysis = analyze_repo(Path("./my-project"), "standard")

print(f"Project type: {analysis['project_type']}")
print(f"Framework: {analysis['framework']}")
print(f"Complexity: {analysis['complexity_score']}")
print(f"Purpose: {analysis['purpose']}")

# Show dependencies
for dep_type, deps in analysis['dependencies'].items():
    if deps:
        print(f"{dep_type}: {len(deps)} packages")
```

### 3. `/detect_changes` - Change Analysis
Intelligent analysis of code changes that provides PR-like reviews with impact assessment and semantic understanding.

**Features:**
- Git-based change detection
- Automatic change categorization (feature, bugfix, refactor, etc.)
- Impact scoring (1-50)
- PR-style summaries using LLM
- File type analysis
- Line change counting

**Usage:**
```python
from fern.cognitive import detect_changes
from pathlib import Path

# Detect changes between commits
changes = detect_changes(Path("./my-project"), "HEAD~1", "HEAD")

print(f"Files changed: {len(changes['diff_summary']['files_changed'])}")
print(f"Lines added: {changes['diff_summary']['additions']}")
print(f"Impact score: {changes['commit_analysis']['impact_score']}")
print(f"PR Summary: {changes['pr_summary']}")

# Analyze specific change types
for change in changes['commit_analysis']['changes']:
    print(f"{change['change_type']}: {len(change['files_changed'])} files")
```

### 4. `/prioritize_tasks` - Smart Task Ranking
Intelligent task prioritization based on impact, risk, and strategic considerations with multiple prioritization strategies.

**Features:**
- Impact and risk scoring
- Multiple prioritization strategies (balanced, impact_first, risk_averse, quick_wins)
- Task categorization (security, performance, bug fixes, etc.)
- Constraint-based filtering (deadlines, effort limits)
- Dependency-aware prioritization
- Strategic recommendations

**Usage:**
```python
from fern.cognitive import prioritize_tasks

# Sample tasks
tasks = [
    {
        "id": "bug-1",
        "title": "Fix authentication vulnerability",
        "description": "Security issue in login flow",
        "type": "bug",
        "severity": "critical",
        "effort": "large"
    },
    {
        "id": "feature-1",
        "title": "Add user profiles",
        "description": "Allow users to edit profiles",
        "type": "feature",
        "severity": "medium",
        "effort": "medium"
    }
]

# Prioritize with different strategies
result = prioritize_tasks(
    tasks_data=tasks,
    strategy="impact_first",
    repo_path=Path("./my-project"),
    constraints={"max_effort": 5}
)

print(f"High priority tasks: {result['high_priority']}")
print(f"Strategy: {result['strategy']}")

# Show top recommendations
for task in result['top_recommendations']:
    print(f"- {task['title']} (Priority: {task['priority_score']})")
```

## Unified API

The `CognitiveAPI` class provides a unified interface for all cognitive functions with workflow orchestration:

```python
from fern.cognitive import create_cognitive_api
from pathlib import Path

# Create API instance
api = create_cognitive_api(Path("./my-project"))

# Perform complete cognitive analysis
result = api.full_cognitive_analysis(
    goal="Add user role-based access control",
    tasks_data=tasks,
    strategy="balanced"
)

print(result['cognitive_summary'])
print("Insights:", result['overall_insights'])
print("Recommendations:", result['workflow_recommendations'])
```

## Integration with Fern Agents

The cognitive functions integrate seamlessly with Fern's existing agent system:

```python
# Enhanced planner agent
from fern.cognitive import CognitiveAPI
from fern.agents.planner_agent import plan_for_goal

def enhanced_planner(repo, goal):
    # Use cognitive planning
    api = create_cognitive_api(repo)
    plan_result = api.plan_feature_endpoint(goal)
    
    if plan_result['status'] == 'success':
        return plan_result['plan']
    else:
        # Fallback to original planning
        return plan_for_goal(repo, goal)
```

## File Structure

```
fern/cognitive/
├── __init__.py          # Module exports
├── planner.py           # /plan_feature implementation
├── analyzer.py          # /analyze_repo implementation  
├── detector.py          # /detect_changes implementation
├── prioritizer.py       # /prioritize_tasks implementation
└── api.py              # Unified API and workflow orchestration
```

## Demonstration

Run the comprehensive demonstration:

```bash
python3 demo_cognitive_functions.py [repo_path] [goal]
```

This demonstrates all four cognitive functions with sample data and complete workflow analysis.

## Key Benefits

1. **Intelligent Context Awareness**: Functions understand repository structure and project context
2. **Strategic Decision Making**: Multiple prioritization strategies for different scenarios
3. **Risk Assessment**: Built-in risk evaluation for planning and prioritization
4. **Scalable Architecture**: Functions can be used independently or as part of complete workflows
5. **Extensible Design**: Easy to add new cognitive capabilities
6. **Error Resilient**: Robust fallback mechanisms for reliability

## Future Enhancements

- LLM integration improvements
- Performance optimization for large repositories
- Additional prioritization strategies
- Integration with external issue trackers
- Machine learning models for better predictions
- Real-time collaborative planning features

The cognitive planning layer transforms Fern from a reactive automation tool into an intelligent development assistant that can provide strategic guidance and context-aware decision making.