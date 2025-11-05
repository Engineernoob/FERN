# Task Prioritization Engine - Cognitive Layer
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from fern.tools.llm import complete
from fern.tools.logger import log_info, log_progress
from fern.cognitive.analyzer import analyze_repo

class TaskItem:
    def __init__(self, id: str, title: str, description: str, task_type: str,
                 severity: str = "medium", effort: str = "medium", 
                 dependencies: List[str] = None, source: str = "manual",
                 created_date: Optional[datetime] = None):
        self.id = id
        self.title = title
        self.description = description
        self.task_type = task_type
        self.severity = severity
        self.effort = effort
        self.dependencies = dependencies or []
        self.source = source
        self.created_date = created_date or datetime.now()
        
        # Calculated properties
        self.impact_score = 0
        self.risk_score = 0
        self.priority_score = 0
        self.category = self._categorize_task()
        
    def _categorize_task(self) -> str:
        """Categorize task based on type and content"""
        title_lower = self.title.lower()
        desc_lower = self.description.lower()
        
        # Critical system components
        if any(keyword in title_lower + desc_lower for keyword in ['security', 'auth', 'login', 'password', 'api']):
            return 'security_critical'
        
        # Performance related
        elif any(keyword in title_lower + desc_lower for keyword in ['performance', 'speed', 'slow', 'optimize', 'cache']):
            return 'performance'
        
        # Bug fixes
        elif self.task_type == 'bug' or any(keyword in title_lower + desc_lower for keyword in ['bug', 'error', 'crash', 'broken']):
            return 'bug_fix'
        
        # Feature requests
        elif self.task_type == 'feature' or any(keyword in title_lower + desc_lower for keyword in ['add', 'implement', 'new', 'feature']):
            return 'feature_request'
        
        # Technical debt
        elif any(keyword in title_lower + desc_lower for keyword in ['refactor', 'cleanup', 'debt', 'legacy', 'technical']):
            return 'technical_debt'
        
        # Documentation
        elif any(keyword in title_lower + desc_lower for keyword in ['doc', 'readme', 'comment', 'documentation']):
            return 'documentation'
        
        # Testing
        elif any(keyword in title_lower + desc_lower for keyword in ['test', 'testing', 'coverage', 'unit test']):
            return 'testing'
        
        # Infrastructure/DevOps
        elif any(keyword in title_lower + desc_lower for keyword in ['deploy', 'docker', 'ci', 'infrastructure', 'devops']):
            return 'infrastructure'
        
        else:
            return 'general'
    
    def calculate_scores(self, repo_analysis: Optional[Dict[str, Any]] = None):
        """Calculate impact and risk scores"""
        self._calculate_impact_score(repo_analysis)
        self._calculate_risk_score()
        self._calculate_priority_score()
        
    def _calculate_impact_score(self, repo_analysis: Optional[Dict[str, Any]] = None):
        """Calculate impact score based on task type and context"""
        base_scores = {
            'security_critical': 10,
            'bug_fix': 8,
            'performance': 7,
            'feature_request': 6,
            'technical_debt': 5,
            'testing': 4,
            'documentation': 3,
            'infrastructure': 6,
            'general': 4
        }
        
        # Base score for category
        self.impact_score = base_scores.get(self.category, 4)
        
        # Severity multiplier
        severity_multipliers = {
            'critical': 2.0,
            'high': 1.5,
            'medium': 1.0,
            'low': 0.7
        }
        self.impact_score *= severity_multipliers.get(self.severity, 1.0)
        
        # Effort factor (inverse - easier tasks get slight boost)
        effort_factors = {
            'small': 1.2,
            'medium': 1.0,
            'large': 0.8,
            'xlarge': 0.6
        }
        self.impact_score *= effort_factors.get(self.effort, 1.0)
        
        # Repository context factor
        if repo_analysis:
            project_type = repo_analysis.get('project_type', 'general')
            if self.category == 'performance' and project_type in ['web', 'api']:
                self.impact_score *= 1.3  # Performance more critical for web/API projects
            elif self.category == 'security_critical':
                self.impact_score *= 1.2  # Security always important
        
        self.impact_score = min(self.impact_score, 15)  # Cap at 15
    
    def _calculate_risk_score(self):
        """Calculate risk score based on complexity and dependencies"""
        base_risk = 5  # Base risk level
        
        # Effort-based risk
        effort_risks = {
            'small': 2,
            'medium': 4,
            'large': 7,
            'xlarge': 9
        }
        base_risk += effort_risks.get(self.effort, 4)
        
        # Dependency-based risk
        dep_risk = min(len(self.dependencies) * 2, 6)
        base_risk += dep_risk
        
        # Type-based risk
        if self.task_type == 'bug':
            base_risk += 3  # Bug fixes can have unknown scope
        elif self.task_type == 'feature':
            base_risk += 2  # New features always carry integration risk
        
        # Task-specific risk adjustments
        if self.category == 'security_critical':
            base_risk += 4  # Security work is high risk
        elif self.category == 'performance':
            base_risk += 3  # Performance work can have unintended consequences
        
        self.risk_score = min(base_risk, 15)  # Cap at 15
    
    def _calculate_priority_score(self):
        """Calculate final priority score (higher = more important)"""
        # Weighted combination of impact and risk, with inverse risk penalty
        self.priority_score = (self.impact_score * 2) - (self.risk_score * 0.5)
        
        # Age factor (tasks get more urgent over time)
        age_days = (datetime.now() - self.created_date).days
        if age_days > 30:
            self.priority_score += 2
        elif age_days > 14:
            self.priority_score += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            "category": self.category,
            "severity": self.severity,
            "effort": self.effort,
            "dependencies": self.dependencies,
            "source": self.source,
            "created_date": self.created_date.isoformat(),
            "impact_score": round(self.impact_score, 1),
            "risk_score": round(self.risk_score, 1),
            "priority_score": round(self.priority_score, 1)
        }

class TaskPrioritizer:
    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path
        self.repo_analysis = None
        if repo_path and repo_path.exists():
            try:
                self.repo_analysis = analyze_repo(repo_path)
            except Exception as e:
                log_info(f"Could not analyze repository for prioritization: {e}")
    
    def parse_issues_from_text(self, text: str) -> List[TaskItem]:
        """Parse issues from text (GitHub issues, TODO comments, etc.)"""
        tasks = []
        
        # Parse GitHub issue format
        github_pattern = r'#(\d+)\s+([^\n]+)\n([^\n]+(?:\n(?!#+)[^\n]+)*)'
        github_matches = re.findall(github_pattern, text)
        
        for match in github_matches:
            issue_id, title, description = match
            tasks.append(TaskItem(
                id=f"github-{issue_id}",
                title=title.strip(),
                description=description.strip(),
                task_type=self._infer_task_type(description),
                source="github"
            ))
        
        # Parse TODO format
        todo_pattern = r'TODO[:\s]+([^\n]+)(?:\n([^\n]+(?:\n(?![A-Z]{2,}:)[^\n]+)*))?'
        todo_matches = re.findall(todo_pattern, text, re.IGNORECASE)
        
        for i, (title, description) in enumerate(todo_matches):
            tasks.append(TaskItem(
                id=f"todo-{len(tasks)+1}",
                title=title.strip(),
                description=(description or "").strip(),
                task_type=self._infer_task_type(title + " " + (description or "")),
                source="todo"
            ))
        
        # Parse test failure format
        test_pattern = r'(FAIL|ERROR|FAILED)\s+([^\n]+)\n([^\n]+(?:\n(?![A-Z]{2,}:)[^\n]+)*)'
        test_matches = re.findall(test_pattern, text)
        
        for match in test_matches:
            status, test_name, error = match
            tasks.append(TaskItem(
                id=f"test-{len(tasks)+1}",
                title=f"Fix test failure: {test_name}",
                description=error.strip(),
                task_type="bug",
                severity="high",
                source="test_failure"
            ))
        
        return tasks
    
    def parse_issues_from_json(self, json_data: Union[str, Dict]) -> List[TaskItem]:
        """Parse issues from JSON data"""
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except Exception as e:
                log_info(f"Failed to parse JSON: {e}")
                return []
        
        tasks = []
        
        # Handle GitHub issues format
        if 'issues' in json_data:
            for issue in json_data['issues']:
                tasks.append(TaskItem(
                    id=f"github-{issue.get('number', len(tasks)+1)}",
                    title=issue.get('title', 'Untitled'),
                    description=issue.get('body', ''),
                    task_type=self._infer_task_type(issue.get('title', '') + ' ' + issue.get('body', '')),
                    severity=self._extract_severity(issue),
                    source="github"
                ))
        
        # Handle generic task list format
        elif isinstance(json_data, list):
            for i, item in enumerate(json_data):
                if isinstance(item, dict):
                    tasks.append(TaskItem(
                        id=item.get('id', f"task-{i+1}"),
                        title=item.get('title', f'Task {i+1}'),
                        description=item.get('description', ''),
                        task_type=item.get('type', 'general'),
                        severity=item.get('severity', 'medium'),
                        effort=item.get('effort', 'medium'),
                        dependencies=item.get('dependencies', []),
                        source="json"
                    ))
        
        return tasks
    
    def prioritize_tasks(self, tasks: List[TaskItem], 
                        strategy: str = "balanced",
                        constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prioritize tasks based on impact, risk, and strategy.
        
        Args:
            tasks: List of TaskItem objects
            strategy: "balanced", "impact_first", "risk_averse", "quick_wins"
            constraints: Optional constraints like max_effort, deadline, etc.
        """
        log_progress(f"Prioritizing {len(tasks)} tasks using {strategy} strategy")
        
        # Calculate scores for all tasks
        for task in tasks:
            task.calculate_scores(self.repo_analysis)
        
        # Apply prioritization strategy
        if strategy == "impact_first":
            prioritized = sorted(tasks, key=lambda t: t.impact_score, reverse=True)
        elif strategy == "risk_averse":
            prioritized = sorted(tasks, key=lambda t: (t.impact_score, -t.risk_score), reverse=True)
        elif strategy == "quick_wins":
            prioritized = sorted(tasks, key=lambda t: (t.impact_score / max(1, self._effort_to_score(t.effort)), -t.risk_score), reverse=True)
        else:  # balanced
            prioritized = sorted(tasks, key=lambda t: t.priority_score, reverse=True)
        
        # Apply constraints
        if constraints:
            prioritized = self._apply_constraints(prioritized, constraints)
        
        # Create groups by priority level
        high_priority = [t for t in prioritized if t.priority_score >= 8]
        medium_priority = [t for t in prioritized if 4 <= t.priority_score < 8]
        low_priority = [t for t in prioritized if t.priority_score < 4]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(prioritized, strategy)
        
        return {
            "strategy": strategy,
            "total_tasks": len(tasks),
            "high_priority": len(high_priority),
            "medium_priority": len(medium_priority),
            "low_priority": len(low_priority),
            "prioritized_tasks": [task.to_dict() for task in prioritized],
            "top_recommendations": [task.to_dict() for task in prioritized[:5]],
            "recommendations": recommendations,
            "constraint_summary": self._summarize_constraints(prioritized, constraints)
        }
    
    def _infer_task_type(self, text: str) -> str:
        """Infer task type from text content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['bug', 'error', 'crash', 'broken']):
            return 'bug'
        elif any(word in text_lower for word in ['feature', 'add', 'implement', 'new']):
            return 'feature'
        elif any(word in text_lower for word in ['refactor', 'cleanup', 'improve']):
            return 'refactor'
        else:
            return 'general'
    
    def _extract_severity(self, issue: Dict) -> str:
        """Extract severity from issue data"""
        labels = issue.get('labels', [])
        if isinstance(labels, list):
            for label in labels:
                if isinstance(label, dict):
                    name = label.get('name', '').lower()
                    if name in ['critical', 'high', 'urgent']:
                        return 'high'
                    elif name in ['low', 'minor']:
                        return 'low'
        
        # Check title for severity indicators
        title = issue.get('title', '').lower()
        if any(word in title for word in ['critical', 'urgent', 'security']):
            return 'high'
        elif any(word in title for word in ['minor', 'small']):
            return 'low'
        
        return 'medium'
    
    def _effort_to_score(self, effort: str) -> int:
        """Convert effort string to numeric score"""
        effort_scores = {
            'small': 1,
            'medium': 3,
            'large': 5,
            'xlarge': 8
        }
        return effort_scores.get(effort, 3)
    
    def _apply_constraints(self, tasks: List[TaskItem], constraints: Dict[str, Any]) -> List[TaskItem]:
        """Apply constraints to task list"""
        filtered = tasks.copy()
        
        # Max effort constraint
        if 'max_effort' in constraints:
            max_effort = constraints['max_effort']
            filtered = [t for t in filtered if self._effort_to_score(t.effort) <= max_effort]
        
        # Deadline constraint
        if 'deadline' in constraints:
            deadline = datetime.fromisoformat(constraints['deadline'])
            # Prefer tasks that can be completed by deadline
            urgency_weight = self._calculate_urgency_weight(tasks, deadline)
            filtered.sort(key=lambda t: t.priority_score + urgency_weight.get(t.id, 0), reverse=True)
        
        # Max tasks constraint
        if 'max_tasks' in constraints:
            filtered = filtered[:constraints['max_tasks']]
        
        return filtered
    
    def _calculate_urgency_weight(self, tasks: List[TaskItem], deadline: datetime) -> Dict[str, int]:
        """Calculate urgency weights based on deadline"""
        weights = {}
        time_remaining = deadline - datetime.now()
        
        for task in tasks:
            # Tasks with longer time remaining get slight priority boost
            task_effort_days = self._effort_to_score(task.effort)
            if time_remaining.days > task_effort_days * 2:
                weights[task.id] = 1
        
        return weights
    
    def _generate_recommendations(self, tasks: List[TaskItem], strategy: str) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        if not tasks:
            return ["No tasks to prioritize"]
        
        # Strategy-specific recommendations
        if strategy == "impact_first":
            recommendations.append("Focus on high-impact tasks first to maximize value delivery")
        elif strategy == "risk_averse":
            recommendations.append("Prioritize lower-risk tasks to build momentum and confidence")
        elif strategy == "quick_wins":
            recommendations.append("Target small, high-impact tasks to demonstrate progress quickly")
        
        # Task mix recommendations
        categories = {}
        for task in tasks[:10]:  # Top 10 tasks
            categories[task.category] = categories.get(task.category, 0) + 1
        
        if categories.get('bug_fix', 0) > 3:
            recommendations.append("High number of bugs detected - consider dedicating a sprint to technical debt")
        
        if categories.get('security_critical', 0) > 0:
            recommendations.append("Security issues detected - prioritize these due to their critical nature")
        
        if categories.get('performance', 0) > 2:
            recommendations.append("Multiple performance issues - consider a dedicated performance optimization cycle")
        
        # Dependency recommendations
        critical_deps = []
        for task in tasks[:5]:
            critical_deps.extend(task.dependencies)
        
        if len(set(critical_deps)) < len(critical_deps):
            recommendations.append("Multiple tasks share dependencies - coordinate implementation to maximize efficiency")
        
        return recommendations
    
    def _summarize_constraints(self, tasks: List[TaskItem], constraints: Optional[Dict[str, Any]]) -> str:
        """Create a summary of constraints application"""
        if not constraints:
            return "No constraints applied"
        
        summary_parts = []
        if 'max_effort' in constraints:
            summary_parts.append(f"Effort limit: {constraints['max_effort']}")
        if 'max_tasks' in constraints:
            summary_parts.append(f"Task limit: {constraints['max_tasks']}")
        if 'deadline' in constraints:
            summary_parts.append(f"Deadline: {constraints['deadline']}")
        
        return "; ".join(summary_parts) if summary_parts else "No constraints applied"

def prioritize_tasks(tasks_data: Union[List[Dict], str, Dict], 
                    strategy: str = "balanced",
                    repo_path: Optional[Path] = None,
                    constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main function to prioritize tasks by impact and risk.
    
    Args:
        tasks_data: Tasks as dict list, JSON string, or text to parse
        strategy: "balanced", "impact_first", "risk_averse", "quick_wins"
        repo_path: Optional repository path for context
        constraints: Optional constraints like max_effort, deadline, max_tasks
        
    Returns:
        Dictionary containing prioritized tasks and recommendations
    """
    prioritizer = TaskPrioritizer(repo_path)
    
    # Parse tasks based on input type
    if isinstance(tasks_data, str):
        if tasks_data.strip().startswith('{') or tasks_data.strip().startswith('['):
            tasks = prioritizer.parse_issues_from_json(tasks_data)
        else:
            tasks = prioritizer.parse_issues_from_text(tasks_data)
    elif isinstance(tasks_data, dict):
        tasks = prioritizer.parse_issues_from_json(tasks_data)
    elif isinstance(tasks_data, list):
        tasks = prioritizer.parse_issues_from_json({"tasks": tasks_data})
    else:
        raise ValueError("Invalid tasks_data format")
    
    if not tasks:
        return {
            "strategy": strategy,
            "total_tasks": 0,
            "error": "No valid tasks found in input data"
        }
    
    return prioritizer.prioritize_tasks(tasks, strategy, constraints)