#!/usr/bin/env python3
"""
Cognitive Planning Layer Demonstration Script
This script demonstrates the four core cognitive functions for Fern:

1. /plan_feature - Break goals into structured subtasks
2. /analyze_repo - Parse repository structure and dependencies  
3. /detect_changes - Compare commits and summarize changes
4. /prioritize_tasks - Rank issues by impact and risk

Usage:
    python demo_cognitive_functions.py [repo_path] [goal]
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from fern.cognitive import (
    create_cognitive_api, 
    plan_feature, 
    analyze_repo, 
    detect_changes, 
    prioritize_tasks
)

def demo_plan_feature():
    """Demonstrate the /plan_feature function"""
    print("=" * 60)
    print("DEMO: /plan_feature - Feature Planning")
    print("=" * 60)
    
    goals = [
        "Add user authentication with JWT tokens",
        "Implement REST API with FastAPI",
        "Create data visualization dashboard"
    ]
    
    for i, goal in enumerate(goals, 1):
        print(f"\nGoal {i}: {goal}")
        print("-" * 40)
        
        try:
            # Use current directory if no repo path provided
            repo_path = Path.cwd() if len(sys.argv) < 2 else Path(sys.argv[1])
            
            plan = plan_feature(goal, repo_path, max_chars=1000)
            print(f"Generated plan with {len(plan.subtasks)} subtasks:")
            
            for subtask in plan.subtasks:
                print(f"  - {subtask.id}: {subtask.description}")
                print(f"    Tool: {subtask.tool}, Effort: {subtask.estimated_effort}, Risk: {subtask.risk_level}")
            
            print(f"Total estimated effort: {plan.estimated_effort}")
            
        except Exception as e:
            print(f"Error: {e}")

def demo_analyze_repo():
    """Demonstrate the /analyze_repo function"""
    print("\n" + "=" * 60)
    print("DEMO: /analyze_repo - Repository Analysis")
    print("=" * 60)
    
    try:
        # Use provided repo path or current directory
        repo_path = Path.cwd() if len(sys.argv) < 2 else Path(sys.argv[1])
        
        if not repo_path.exists():
            print(f"Repository path does not exist: {repo_path}")
            return
        
        print(f"Analyzing repository: {repo_path}")
        analysis = analyze_repo(repo_path, "standard")
        
        if "error" in analysis:
            print(f"Analysis error: {analysis['error']}")
            return
        
        print(f"\nProject Type: {analysis.get('project_type', 'Unknown')}")
        print(f"Main Language: {analysis.get('main_language', 'Unknown')}")
        print(f"Framework: {analysis.get('framework', 'None detected')}")
        print(f"Complexity: {analysis.get('complexity_score', 'Unknown')}")
        print(f"Purpose: {analysis.get('purpose', 'Unknown')}")
        
        # Show dependencies
        deps = analysis.get('dependencies', {})
        if deps:
            print(f"\nDependencies found:")
            for dep_type, dep_list in deps.items():
                if isinstance(dep_list, list) and dep_list:
                    print(f"  - {dep_type}: {', '.join(dep_list[:5])}{'...' if len(dep_list) > 5 else ''}")
                elif isinstance(dep_list, dict):
                    print(f"  - {dep_type}: {sum(len(v) for v in dep_list.values())} packages")
        
        # Show key files
        key_files = analysis.get('key_files', {})
        if key_files:
            print(f"\nKey files found:")
            for category, files in key_files.items():
                if files:
                    print(f"  - {category}: {len(files)} files")
        
        # Show repository structure
        structure = analysis.get('structure', {})
        if structure:
            print(f"\nDirectory structure:")
            for dir_name, path in structure.items():
                print(f"  - {dir_name}: {path}")
        
    except Exception as e:
        print(f"Error: {e}")

def demo_detect_changes():
    """Demonstrate the /detect_changes function"""
    print("\n" + "=" * 60)
    print("DEMO: /detect_changes - Change Detection")
    print("=" * 60)
    
    try:
        # Use provided repo path or current directory
        repo_path = Path.cwd() if len(sys.argv) < 2 else Path(sys.argv[1])
        
        if not repo_path.exists():
            print(f"Repository path does not exist: {repo_path}")
            return
        
        # Check if it's a git repository
        git_path = repo_path / ".git"
        if not git_path.exists():
            print("Not a git repository - skipping change detection demo")
            return
        
        print(f"Analyzing changes in: {repo_path}")
        
        # Analyze recent changes
        changes = detect_changes(repo_path, "HEAD~1", "HEAD")
        
        if "error" in changes:
            print(f"Change detection error: {changes['error']}")
            return
        
        print(f"\nCommit: {changes['commit_analysis']['commit_hash']}")
        print(f"Author: {changes['commit_analysis']['author']}")
        print(f"Message: {changes['commit_analysis']['message']}")
        print(f"Impact Score: {changes['commit_analysis']['impact_score']}")
        
        diff_summary = changes.get('diff_summary', {})
        print(f"\nFiles changed: {len(diff_summary.get('files_changed', []))}")
        print(f"Lines added: {diff_summary.get('additions', 0)}")
        print(f"Lines deleted: {diff_summary.get('deletions', 0)}")
        
        # Show PR summary
        if 'pr_summary' in changes:
            print(f"\nPR-style summary:")
            print(f"{changes['pr_summary']}")
        
        # Show change categories
        commit_analysis = changes.get('commit_analysis', {})
        changes_list = commit_analysis.get('changes', [])
        if changes_list:
            print(f"\nChange categories:")
            for change in changes_list:
                print(f"  - {change['change_type']}: {len(change['files_changed'])} files")
        
    except Exception as e:
        print(f"Error: {e}")

def demo_prioritize_tasks():
    """Demonstrate the /prioritize_tasks function"""
    print("\n" + "=" * 60)
    print("DEMO: /prioritize_tasks - Task Prioritization")
    print("=" * 60)
    
    # Sample tasks for demonstration
    sample_tasks = [
        {
            "id": "bug-1",
            "title": "Fix critical authentication vulnerability",
            "description": "Users can bypass login due to JWT validation issue",
            "type": "bug",
            "severity": "critical",
            "effort": "large"
        },
        {
            "id": "feature-1", 
            "title": "Add user profile management",
            "description": "Allow users to edit their profile information",
            "type": "feature",
            "severity": "medium",
            "effort": "medium"
        },
        {
            "id": "perf-1",
            "title": "Optimize database queries",
            "description": "Slow page load times due to inefficient queries",
            "type": "performance",
            "severity": "high", 
            "effort": "large"
        },
        {
            "id": "docs-1",
            "title": "Update API documentation",
            "description": "Documentation is outdated for v2 endpoints",
            "type": "documentation",
            "severity": "low",
            "effort": "small"
        },
        {
            "id": "test-1",
            "title": "Add integration tests",
            "description": "Need more test coverage for critical paths",
            "type": "testing",
            "severity": "medium",
            "effort": "medium"
        }
    ]
    
    strategies = ["balanced", "impact_first", "risk_averse", "quick_wins"]
    
    for strategy in strategies:
        print(f"\nStrategy: {strategy.upper()}")
        print("-" * 30)
        
        try:
            # Use current directory if no repo path provided
            repo_path = Path.cwd() if len(sys.argv) < 2 else Path(sys.argv[1])
            
            result = prioritize_tasks(
                tasks_data=sample_tasks,
                strategy=strategy,
                repo_path=repo_path,
                constraints={"max_effort": 5}  # Avoid extremely large tasks
            )
            
            if "error" in result:
                print(f"Prioritization error: {result['error']}")
                continue
            
            print(f"Total tasks: {result['total_tasks']}")
            print(f"High priority: {result['high_priority']}")
            print(f"Medium priority: {result['medium_priority']}")
            print(f"Low priority: {result['low_priority']}")
            
            print(f"\nTop 3 recommended tasks:")
            for i, task in enumerate(result['prioritized_tasks'][:3], 1):
                print(f"  {i}. {task['title']} (Priority: {task['priority_score']})")
                print(f"     Impact: {task['impact_score']}, Risk: {task['risk_score']}, Category: {task['category']}")
            
            # Show recommendations
            recommendations = result.get('recommendations', [])
            if recommendations:
                print(f"\nRecommendations:")
                for rec in recommendations[:3]:
                    print(f"  - {rec}")
        
        except Exception as e:
            print(f"Error: {e}")

def demo_full_cognitive_analysis():
    """Demonstrate complete cognitive analysis workflow"""
    print("\n" + "=" * 60)
    print("DEMO: Full Cognitive Analysis Workflow")
    print("=" * 60)
    
    try:
        # Create cognitive API with repository path
        repo_path = Path.cwd() if len(sys.argv) < 2 else Path(sys.argv[1])
        
        if not repo_path.exists():
            print(f"Repository path does not exist: {repo_path}")
            return
        
        api = create_cognitive_api(repo_path)
        
        # Define a sample goal for the demo
        goal = "Add user role-based access control system"
        
        # Sample tasks to prioritize
        sample_tasks = [
            {
                "id": "rbac-1",
                "title": "Implement role-based permissions",
                "description": "Add role-based access control with admin, user, and guest roles",
                "type": "feature",
                "severity": "high",
                "effort": "large"
            },
            {
                "id": "rbac-2",
                "title": "Create role management UI",
                "description": "Admin interface for managing user roles and permissions",
                "type": "feature", 
                "severity": "medium",
                "effort": "medium"
            },
            {
                "id": "security-1",
                "title": "Add authorization middleware",
                "description": "Implement middleware to check permissions for each endpoint",
                "type": "security",
                "severity": "high",
                "effort": "medium"
            }
        ]
        
        print(f"Running complete cognitive analysis...")
        print(f"Repository: {repo_path}")
        print(f"Feature Goal: {goal}")
        print(f"Tasks: {len(sample_tasks)} items")
        
        # Perform full analysis
        result = api.full_cognitive_analysis(
            goal=goal,
            tasks_data=sample_tasks,
            strategy="impact_first"
        )
        
        if "error" in result:
            print(f"Analysis error: {result['error']}")
            return
        
        cognitive_analysis = result['cognitive_analysis']
        
        # Display summary
        print(f"\n" + "=" * 40)
        print("COGNITIVE ANALYSIS SUMMARY")
        print("=" * 40)
        
        print(f"\nRepository Analysis:")
        repo_analysis = cognitive_analysis.get('repository_analysis', {})
        if repo_analysis.get('status') == 'success':
            analysis = repo_analysis.get('analysis', {})
            print(f"  Project Type: {analysis.get('project_type', 'Unknown')}")
            print(f"  Complexity: {analysis.get('complexity_score', 'Unknown')}")
            print(f"  Insights: {', '.join(repo_analysis.get('insights', []))}")
        
        print(f"\nFeature Planning:")
        feature_plan = cognitive_analysis.get('feature_planning', {})
        if feature_plan.get('status') == 'success':
            plan = feature_plan.get('plan', {})
            print(f"  Subtasks: {plan.get('subtask_count', 0)}")
            print(f"  Total Effort: {plan.get('estimated_total_effort', 0)}")
            print(f"  Risk Level: {feature_plan.get('metadata', {}).get('risk_assessment', {}).get('level', 'Unknown')}")
        
        print(f"\nChange Analysis:")
        change_analysis = cognitive_analysis.get('change_analysis', {})
        if change_analysis.get('status') == 'success':
            summary = change_analysis.get('summary', {})
            print(f"  Files Modified: {summary.get('files_modified', 0)}")
            print(f"  Lines Changed: {summary.get('lines_added', 0) + summary.get('lines_removed', 0)}")
        
        print(f"\nTask Prioritization:")
        task_prioritization = cognitive_analysis.get('task_prioritization', {})
        if task_prioritization.get('status') == 'success':
            print(f"  High Priority: {task_prioritization.get('high_priority', 0)}")
            print(f"  Strategy Used: {task_prioritization.get('strategy', 'Unknown')}")
        
        # Display overall insights
        overall_insights = cognitive_analysis.get('overall_insights', [])
        if overall_insights:
            print(f"\nOverall Insights:")
            for insight in overall_insights:
                print(f"  - {insight}")
        
        # Display workflow recommendations
        workflow_recommendations = cognitive_analysis.get('workflow_recommendations', [])
        if workflow_recommendations:
            print(f"\nWorkflow Recommendations:")
            for rec in workflow_recommendations:
                print(f"  - {rec}")
        
        print(f"\n" + "=" * 40)
        print(f"Analysis completed at: {result['timestamp']}")
        print("=" * 40)
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main demonstration function"""
    print("Fern Cognitive Planning Layer - Demonstration")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Working Directory: {Path.cwd()}")
    
    if len(sys.argv) > 1:
        repo_path = Path(sys.argv[1])
        print(f"Target Repository: {repo_path}")
        if not repo_path.exists():
            print(f"WARNING: Repository path does not exist: {repo_path}")
    else:
        print("Using current directory as repository")
    
    if len(sys.argv) > 2:
        print(f"Feature Goal: {sys.argv[2]}")
    
    # Run all demonstrations
    demo_plan_feature()
    demo_analyze_repo()
    demo_detect_changes()
    demo_prioritize_tasks()
    demo_full_cognitive_analysis()
    
    print(f"\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("The cognitive planning layer functions have been demonstrated.")
    print("These functions can be integrated into the Fern agent workflow")
    print("to provide intelligent, context-aware development assistance.")

if __name__ == "__main__":
    main()