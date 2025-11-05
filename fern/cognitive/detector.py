# Change Detection and Analysis - Cognitive Layer
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from fern.tools.git import Repo
from fern.tools.llm import complete
from fern.tools.logger import log_info, log_progress

class ChangeSet:
    def __init__(self, files_changed: List[str], additions: int, deletions: int, 
                 change_type: str, semantic_impact: str):
        self.files_changed = files_changed
        self.additions = additions
        self.deletions = deletions
        self.change_type = change_type
        self.semantic_impact = semantic_impact
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "files_changed": self.files_changed,
            "additions": self.additions,
            "deletions": self.deletions,
            "change_type": self.change_type,
            "semantic_impact": self.semantic_impact
        }

class CommitAnalysis:
    def __init__(self, commit_hash: str, author: str, message: str, 
                 timestamp: datetime, changes: List[ChangeSet]):
        self.commit_hash = commit_hash
        self.author = author
        self.message = message
        self.timestamp = timestamp
        self.changes = changes
        self.impact_score = self._calculate_impact_score()
        
    def _calculate_impact_score(self) -> int:
        """Calculate impact score based on change type and scope"""
        score = 0
        
        # Base score for change types
        change_scores = {
            'feature': 5,
            'bugfix': 3,
            'refactor': 2,
            'docs': 1,
            'style': 1,
            'config': 2,
            'test': 1,
            'chore': 1
        }
        
        for change in self.changes:
            score += change_scores.get(change.change_type, 1)
            # Add weight for number of files
            score += min(len(change.files_changed), 5)
            # Add weight for size of changes
            score += min(change.additions + change.deletions, 100) // 20
            
        return min(score, 50)  # Cap at 50
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "commit_hash": self.commit_hash,
            "author": self.author,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "impact_score": self.impact_score,
            "changes": [change.to_dict() for change in self.changes]
        }

class PullRequestAnalysis:
    def __init__(self, pr_number: int, title: str, author: str, 
                 branch: str, base_branch: str, commits: List[CommitAnalysis],
                 description: str = "", labels: List[str] = None):
        self.pr_number = pr_number
        self.title = title
        self.author = author
        self.branch = branch
        self.base_branch = base_branch
        self.commits = commits
        self.description = description
        self.labels = labels or []
        self.overall_impact = self._calculate_overall_impact()
        self.review_status = "pending"
        
    def _calculate_overall_impact(self) -> str:
        """Calculate overall impact across all commits"""
        total_impact = sum(commit.impact_score for commit in self.commits)
        high_impact_count = sum(1 for commit in self.commits if commit.impact_score > 15)
        
        if total_impact > 50 or high_impact_count >= 2:
            return "high"
        elif total_impact > 20 or high_impact_count >= 1:
            return "medium"
        else:
            return "low"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pr_number": self.pr_number,
            "title": self.title,
            "author": self.author,
            "branch": self.branch,
            "base_branch": self.base_branch,
            "description": self.description,
            "labels": self.labels,
            "overall_impact": self.overall_impact,
            "review_status": self.review_status,
            "commit_count": len(self.commits),
            "total_impact_score": sum(commit.impact_score for commit in self.commits),
            "commits": [commit.to_dict() for commit in self.commits]
        }

def detect_changes(repo_path: Path, base_ref: str = "HEAD~1", head_ref: str = "HEAD") -> Dict[str, Any]:
    """
    Analyze changes between commits and provide PR-like review summary.
    
    Args:
        repo_path: Path to git repository
        base_ref: Starting commit/branch for comparison
        head_ref: Ending commit/branch for comparison
        
    Returns:
        Dictionary containing change analysis and PR-like summary
    """
    log_progress(f"Detecting changes from {base_ref} to {head_ref}")
    
    try:
        repo = Repo(repo_path)
        
        # Get commit objects
        base_commit = repo.commit(base_ref)
        head_commit = repo.commit(head_ref)
        
        if not base_commit or not head_commit:
            return {"error": f"Could not find commits {base_ref} or {head_ref}"}
        
        # Get diff between commits
        diff = repo.git.diff(base_ref, head_ref)
        
        # Parse changed files
        changed_files = []
        additions = 0
        deletions = 0
        
        for line in diff.split('\n'):
            if line.startswith('diff --git'):
                # Extract file path
                match = re.search(r'b/(.+)', line)
                if match:
                    changed_files.append(match.group(1))
            elif line.startswith('+++'):
                continue
            elif line.startswith('@@'):
                continue
            elif line.startswith('+') and not line.startswith('+++'):
                additions += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
        
        # Analyze change types and semantic impact
        changesets = _analyze_change_semantics(changed_files, diff)
        
        # Create commit analysis
        commit_analysis = CommitAnalysis(
            commit_hash=head_commit.hexsha[:8],
            author=head_commit.author.name,
            message=head_commit.message.strip(),
            timestamp=datetime.fromtimestamp(head_commit.committed_date),
            changes=changesets
        )
        
        # Generate PR-like summary
        summary = _generate_pr_summary(commit_analysis, diff)
        
        return {
            "commit_analysis": commit_analysis.to_dict(),
            "diff_summary": {
                "files_changed": changed_files,
                "additions": additions,
                "deletions": deletions,
                "lines_changed": additions + deletions
            },
            "pr_summary": summary,
            "comparison_refs": {
                "base": base_ref,
                "head": head_ref
            }
        }
        
    except Exception as e:
        log_info(f"Change detection failed: {e}")
        return {"error": str(e)}

def _analyze_change_semantics(changed_files: List[str], diff: str) -> List[ChangeSet]:
    """Analyze the semantic meaning of changes"""
    changesets = []
    
    # Categorize files by type and purpose
    file_categories = {
        'source_code': [],
        'tests': [],
        'docs': [],
        'config': [],
        'build': [],
        'style': []
    }
    
    for file_path in changed_files:
        file_lower = file_path.lower()
        
        if any(ext in file_lower for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']):
            if 'test' in file_lower or 'spec' in file_lower:
                file_categories['tests'].append(file_path)
            elif 'docs' in file_lower or 'readme' in file_lower or file_lower.endswith('.md'):
                file_categories['docs'].append(file_path)
            else:
                file_categories['source_code'].append(file_path)
        elif any(ext in file_lower for ext in ['.json', '.yaml', '.yml', '.conf', '.ini', '.cfg']):
            file_categories['config'].append(file_path)
        elif any(ext in file_lower for ext in ['.dockerfile', 'docker-compose', 'makefile', '.gradle', 'pom.xml']):
            file_categories['build'].append(file_path)
        elif any(ext in file_lower for ext in ['.css', '.scss', '.less']):
            file_categories['style'].append(file_path)
        else:
            file_categories['source_code'].append(file_path)
    
    # Analyze each category
    for category, files in file_categories.items():
        if not files:
            continue
            
        # Count lines changed for this category
        category_diff = ""
        for file_path in files:
            pattern = f'\\+\\+\\+ b/{re.escape(file_path)}.*?(?=\\ndiff --git|$)'
            matches = re.findall(pattern, diff, re.DOTALL)
            if matches:
                category_diff += "\\n".join(matches)
        
        additions = len(re.findall(r'^\\+', category_diff, re.MULTILINE))
        deletions = len(re.findall(r'^-', category_diff, re.MULTILINE))
        
        # Determine change type and semantic impact
        change_type, semantic_impact = _classify_change_type(category, files)
        
        changesets.append(ChangeSet(
            files_changed=files,
            additions=additions,
            deletions=deletions,
            change_type=change_type,
            semantic_impact=semantic_impact
        ))
    
    return changesets

def _classify_change_type(category: str, files: List[str]) -> Tuple[str, str]:
    """Classify change type and semantic impact"""
    
    if category == 'source_code':
        # Check for new files vs modifications
        new_files = [f for f in files if not (Path(f).parent / f).exists() or f.endswith('.new')]
        if new_files:
            return 'feature', 'significant'
        else:
            return 'refactor', 'moderate'
    
    elif category == 'tests':
        return 'test', 'low'
    
    elif category == 'docs':
        return 'docs', 'low'
    
    elif category == 'config':
        return 'config', 'moderate'
    
    elif category == 'build':
        return 'chore', 'moderate'
    
    elif category == 'style':
        return 'style', 'minimal'
    
    else:
        return 'unknown', 'unknown'

def _generate_pr_summary(commit_analysis: CommitAnalysis, diff: str) -> str:
    """Generate a PR-like summary using LLM analysis"""
    
    try:
        # Prepare context for LLM
        change_context = {
            "commit_message": commit_analysis.message,
            "files_changed": sum(len(ch.files_changed) for ch in commit_analysis.changes),
            "total_lines": sum(ch.additions + ch.deletions for ch in commit_analysis.changes),
            "change_types": list(set(ch.change_type for ch in commit_analysis.changes))
        }
        
        prompt = f"""As an expert code reviewer, summarize this commit in PR style:

Commit Message: {commit_analysis.message}
Files Changed: {change_context['files_changed']}
Total Lines: {change_context['total_lines']}
Change Types: {', '.join(change_context['change_types'])}

Provide a concise summary that includes:
1. What was changed
2. Why it was changed (if evident)
3. Potential impact
4. Review notes

Keep it to 2-3 sentences, professional tone."""
        
        summary = complete(prompt, sys="You are a professional code reviewer writing PR descriptions.")
        
        # Clean up LLM response
        summary = summary.strip().replace('\\n', ' ').replace('\\t', ' ')
        summary = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', summary)  # Remove control chars
        
        if summary and len(summary) > 10:
            return summary
        
    except Exception as e:
        log_info(f"PR summary generation failed: {e}")
    
    # Enhanced fallback summary
    change_types = list(set(ch.change_type for ch in commit_analysis.changes))
    total_files = sum(len(ch.files_changed) for ch in commit_analysis.changes)
    total_lines = sum(ch.additions + ch.deletions for ch in commit_analysis.changes)
    
    return f"Modified {total_files} files ({', '.join(change_types)}), {total_lines} lines. {commit_analysis.message}"

def analyze_pull_request(repo_path: Path, pr_branch: str, base_branch: str = "main") -> Dict[str, Any]:
    """
    Analyze a pull request by comparing branches.
    
    Args:
        repo_path: Path to git repository
        pr_branch: Feature branch to analyze
        base_branch: Base branch for comparison
        
    Returns:
        Dictionary containing PR analysis
    """
    log_progress(f"Analyzing PR: {pr_branch} -> {base_branch}")
    
    try:
        repo = Repo(repo_path)
        
        # Get all commits in the PR branch that aren't in base branch
        commits = []
        for commit in repo.iter_commits(f'{base_branch}..{pr_branch}'):
            changes = detect_changes(repo_path, f'{base_branch}..HEAD', f'{base_branch}..{pr_branch}')
            if 'commit_analysis' in changes:
                commits.append(commit)
        
        # Create PR analysis
        pr_analysis = PullRequestAnalysis(
            pr_number=0,  # Would need GitHub API integration for actual PR number
            title=f"PR: {pr_branch}",
            author="Unknown",  # Would need GitHub API for actual author
            branch=pr_branch,
            base_branch=base_branch,
            commits=[],  # Would populate from actual GitHub API
            description=f"Analysis of branch {pr_branch} against {base_branch}"
        )
        
        return pr_analysis.to_dict()
        
    except Exception as e:
        log_info(f"PR analysis failed: {e}")
        return {"error": str(e)}