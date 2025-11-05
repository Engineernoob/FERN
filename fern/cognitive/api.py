# Cognitive API Integration Layer for Fern
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from fern.cognitive.planner import plan_feature, FeaturePlan
from fern.cognitive.analyzer import analyze_repo
from fern.cognitive.detector import detect_changes, analyze_pull_request
from fern.cognitive.prioritizer import prioritize_tasks, TaskItem

class CognitiveAPI:
    """
    Unified API for all cognitive planning layer functions.
    Provides both functional interface and potential REST API foundation.
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path
        self.session_data = {}
        
    def plan_feature_endpoint(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        API endpoint for /plan_feature functionality
        
        Args:
            goal: Feature goal to plan
            context: Optional context data (repo analysis, constraints, etc.)
            
        Returns:
            Structured feature plan with subtasks and metadata
        """
        try:
            # Use repository context if available
            repo_context = self.repo_path if self.repo_path else None
            
            # Create feature plan
            feature_plan = plan_feature(goal, repo_context, max_chars=20000)
            
            # Add context-based enhancements
            if context:
                feature_plan = self._enhance_plan_with_context(feature_plan, context)
            
            return {
                "status": "success",
                "function": "/plan_feature",
                "timestamp": datetime.now().isoformat(),
                "goal": goal,
                "plan": feature_plan.to_dict(),
                "metadata": {
                    "subtask_count": len(feature_plan.subtasks),
                    "estimated_total_effort": feature_plan.estimated_effort,
                    "dependencies_count": len(feature_plan.dependencies),
                    "risk_assessment": self._assess_plan_risk(feature_plan)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "function": "/plan_feature",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_repo_endpoint(self, analysis_depth: str = "standard") -> Dict[str, Any]:
        """
        API endpoint for /analyze_repo functionality
        
        Args:
            analysis_depth: "quick", "standard", or "deep"
            
        Returns:
            Comprehensive repository analysis
        """
        try:
            if not self.repo_path or not self.repo_path.exists():
                return {
                    "status": "error",
                    "function": "/analyze_repo",
                    "error": "Repository path not provided or does not exist",
                    "timestamp": datetime.now().isoformat()
                }
            
            analysis = analyze_repo(self.repo_path, analysis_depth)
            
            return {
                "status": "success",
                "function": "/analyze_repo",
                "timestamp": datetime.now().isoformat(),
                "repo_path": str(self.repo_path),
                "analysis_depth": analysis_depth,
                "analysis": analysis,
                "insights": self._generate_repo_insights(analysis)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "function": "/analyze_repo",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def detect_changes_endpoint(self, base_ref: str = "HEAD~1", head_ref: str = "HEAD") -> Dict[str, Any]:
        """
        API endpoint for /detect_changes functionality
        
        Args:
            base_ref: Starting reference for comparison
            head_ref: Ending reference for comparison
            
        Returns:
            Change analysis and PR-like summary
        """
        try:
            if not self.repo_path or not self.repo_path.exists():
                return {
                    "status": "error",
                    "function": "/detect_changes",
                    "error": "Repository path not provided or does not exist",
                    "timestamp": datetime.now().isoformat()
                }
            
            changes = detect_changes(self.repo_path, base_ref, head_ref)
            
            return {
                "status": "success",
                "function": "/detect_changes",
                "timestamp": datetime.now().isoformat(),
                "repo_path": str(self.repo_path),
                "comparison": {"base": base_ref, "head": head_ref},
                "analysis": changes,
                "summary": self._generate_change_summary(changes)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "function": "/detect_changes",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def prioritize_tasks_endpoint(self, tasks_data: Any, 
                                 strategy: str = "balanced",
                                 constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        API endpoint for /prioritize_tasks functionality
        
        Args:
            tasks_data: Tasks to prioritize (JSON, text, or dict)
            strategy: Prioritization strategy
            constraints: Optional constraints
            
        Returns:
            Prioritized tasks with recommendations
        """
        try:
            prioritization = prioritize_tasks(
                tasks_data=tasks_data,
                strategy=strategy,
                repo_path=self.repo_path,
                constraints=constraints
            )
            
            return {
                "status": "success",
                "function": "/prioritize_tasks",
                "timestamp": datetime.now().isoformat(),
                "strategy": strategy,
                "results": prioritization,
                "recommendations": self._generate_prioritization_recommendations(prioritization)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "function": "/prioritize_tasks",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def full_cognitive_analysis(self, goal: Optional[str] = None,
                              tasks_data: Optional[Any] = None,
                              strategy: str = "balanced") -> Dict[str, Any]:
        """
        Perform complete cognitive analysis workflow
        
        Args:
            goal: Optional feature goal for planning
            tasks_data: Optional tasks for prioritization
            strategy: Prioritization strategy
            
        Returns:
            Complete cognitive analysis report
        """
        results = {}
        
        # Repository analysis (if repo available)
        if self.repo_path and self.repo_path.exists():
            repo_analysis = self.analyze_repo_endpoint("standard")
            results["repository_analysis"] = repo_analysis
        else:
            results["repository_analysis"] = {"status": "skipped", "reason": "No repository path"}
        
        # Feature planning (if goal provided)
        if goal:
            feature_plan = self.plan_feature_endpoint(goal, 
                                                    context={"repo_analysis": results.get("repository_analysis", {}).get("analysis")})
            results["feature_planning"] = feature_plan
        else:
            results["feature_planning"] = {"status": "skipped", "reason": "No goal provided"}
        
        # Change detection (if git repo available)
        if self.repo_path and self.repo_path.exists():
            try:
                from git import Repo
                if (self.repo_path / ".git").exists():
                    change_analysis = self.detect_changes_endpoint()
                    results["change_analysis"] = change_analysis
                else:
                    results["change_analysis"] = {"status": "skipped", "reason": "Not a git repository"}
            except Exception as e:
                results["change_analysis"] = {"status": "error", "error": str(e)}
        else:
            results["change_analysis"] = {"status": "skipped", "reason": "No repository path"}
        
        # Task prioritization (if tasks provided)
        if tasks_data:
            task_prioritization = self.prioritize_tasks_endpoint(tasks_data, strategy)
            results["task_prioritization"] = task_prioritization
        else:
            results["task_prioritization"] = {"status": "skipped", "reason": "No tasks provided"}
        
        # Generate overall insights
        results["overall_insights"] = self._generate_overall_insights(results)
        results["cognitive_summary"] = self._create_cognitive_summary(results)
        results["workflow_recommendations"] = self._generate_workflow_recommendations(results)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "cognitive_analysis": results,
            "api_version": "1.0"
        }
    
    def _enhance_plan_with_context(self, plan: FeaturePlan, context: Dict[str, Any]) -> FeaturePlan:
        """Enhance feature plan with additional context"""
        # This could include repository-specific optimizations
        # or constraint-based adjustments
        return plan
    
    def _assess_plan_risk(self, plan: FeaturePlan) -> Dict[str, str]:
        """Assess risk level of a feature plan"""
        total_risk = sum(task.estimated_effort for task in plan.subtasks if hasattr(task, 'risk_level') and task.risk_level == 'high')
        complexity = len(plan.subtasks)
        
        if total_risk > 10 or complexity > 15:
            return {"level": "high", "reason": "Complex plan with high-risk components"}
        elif total_risk > 5 or complexity > 8:
            return {"level": "medium", "reason": "Moderate complexity with some risk"}
        else:
            return {"level": "low", "reason": "Simple plan with manageable risk"}
    
    def _generate_repo_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from repository analysis"""
        insights = []
        
        if analysis.get('project_type'):
            insights.append(f"Detected {analysis['project_type']} project")
        
        if analysis.get('framework'):
            insights.append(f"Framework detected: {analysis['framework']}")
        
        if analysis.get('complexity_score'):
            insights.append(f"Project complexity: {analysis['complexity_score']}")
        
        deps = analysis.get('dependencies', {})
        if deps:
            total_deps = sum(len(d) if isinstance(d, list) else 1 for d in deps.values())
            insights.append(f"Total dependencies: {total_deps}")
        
        return insights
    
    def _generate_change_summary(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of changes"""
        if 'error' in changes:
            return changes
        
        commit_analysis = changes.get('commit_analysis', {})
        diff_summary = changes.get('diff_summary', {})
        
        return {
            "files_modified": len(diff_summary.get('files_changed', [])),
            "lines_added": diff_summary.get('additions', 0),
            "lines_removed": diff_summary.get('deletions', 0),
            "impact_level": commit_analysis.get('impact_score', 0),
            "change_categories": list(set(ch.get('change_type') for ch in commit_analysis.get('changes', [])))
        }
    
    def _generate_prioritization_recommendations(self, prioritization: Dict[str, Any]) -> List[str]:
        """Generate recommendations from prioritization results"""
        recommendations = prioritization.get('recommendations', [])
        
        high_priority_count = prioritization.get('high_priority', 0)
        medium_priority_count = prioritization.get('medium_priority', 0)
        low_priority_count = prioritization.get('low_priority', 0)
        
        if high_priority_count > 5:
            recommendations.append("Consider breaking down high-priority items to reduce complexity")
        
        if medium_priority_count > high_priority_count * 2:
            recommendations.append("High number of medium-priority items - consider re-evaluating priorities")
        
        return recommendations
    
    def _generate_overall_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate overall insights from complete analysis"""
        insights = []
        
        # Repository insights
        repo_analysis = results.get('repository_analysis', {})
        if repo_analysis.get('status') == 'success':
            analysis = repo_analysis.get('analysis', {})
            insights.extend(repo_analysis.get('insights', []))
        
        # Feature planning insights
        feature_plan = results.get('feature_planning', {})
        if feature_plan.get('status') == 'success':
            plan_data = feature_plan.get('plan', {})
            insights.append(f"Feature plan created with {plan_data.get('subtask_count', 0)} subtasks")
        
        # Change analysis insights
        change_analysis = results.get('change_analysis', {})
        if change_analysis.get('status') == 'success':
            summary = change_analysis.get('summary', {})
            if summary.get('files_modified', 0) > 0:
                insights.append(f"Detected {summary['files_modified']} modified files")
        
        # Task prioritization insights
        task_prioritization = results.get('task_prioritization', {})
        if task_prioritization.get('status') == 'success':
            high_priority = task_prioritization.get('high_priority', 0)
            if high_priority > 0:
                insights.append(f"{high_priority} high-priority tasks identified")
        
        return insights
    
    def _create_cognitive_summary(self, results: Dict[str, Any]) -> str:
        """Create a narrative summary of the cognitive analysis"""
        summary_parts = []
        
        summary_parts.append("Cognitive Analysis Summary")
        summary_parts.append("=" * 30)
        
        # Repository summary
        repo_analysis = results.get('repository_analysis', {})
        if repo_analysis.get('status') == 'success':
            analysis = repo_analysis.get('analysis', {})
            project_type = analysis.get('project_type', 'unknown')
            complexity = analysis.get('complexity_score', 'unknown')
            summary_parts.append(f"Repository: {project_type} project with {complexity} complexity")
        else:
            summary_parts.append("Repository: No analysis performed")
        
        # Feature planning summary
        feature_plan = results.get('feature_planning', {})
        if feature_plan.get('status') == 'success':
            plan_data = feature_plan.get('plan', {})
            subtask_count = plan_data.get('subtask_count', 0)
            effort = plan_data.get('estimated_total_effort', 0)
            summary_parts.append(f"Feature Plan: {subtask_count} subtasks, estimated effort: {effort}")
        
        # Change analysis summary
        change_analysis = results.get('change_analysis', {})
        if change_analysis.get('status') == 'success':
            summary = change_analysis.get('summary', {})
            files = summary.get('files_modified', 0)
            summary_parts.append(f"Changes: {files} files modified")
        
        # Task prioritization summary
        task_prioritization = results.get('task_prioritization', {})
        if task_prioritization.get('status') == 'success':
            high_pri = task_prioritization.get('high_priority', 0)
            total_tasks = task_prioritization.get('total_tasks', 0)
            summary_parts.append(f"Tasks: {total_tasks} total, {high_pri} high priority")
        
        return "\\n".join(summary_parts)
    
    def _generate_workflow_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate workflow recommendations based on analysis"""
        recommendations = []
        
        # Repository-based recommendations
        repo_analysis = results.get('repository_analysis', {})
        if repo_analysis.get('status') == 'success':
            analysis = repo_analysis.get('analysis', {})
            complexity = analysis.get('complexity_score', 'low')
            
            if complexity == 'high':
                recommendations.append("High complexity project - consider implementing automated testing and CI/CD")
            elif complexity == 'medium':
                recommendations.append("Medium complexity - ensure adequate documentation and code reviews")
        
        # Feature planning recommendations
        feature_plan = results.get('feature_planning', {})
        if feature_plan.get('status') == 'success':
            plan_data = feature_plan.get('plan', {})
            subtask_count = plan_data.get('subtask_count', 0)
            
            if subtask_count > 10:
                recommendations.append("Complex feature - break into smaller milestones for better progress tracking")
        
        # Task prioritization recommendations
        task_prioritization = results.get('task_prioritization', {})
        if task_prioritization.get('status') == 'success':
            strategy = task_prioritization.get('strategy', 'balanced')
            recommendations.append(f"Applied {strategy} prioritization strategy")
        
        return recommendations

# Convenience function for easy API access
def create_cognitive_api(repo_path: Optional[Path] = None) -> CognitiveAPI:
    """Create a CognitiveAPI instance with optional repository path"""
    return CognitiveAPI(repo_path)