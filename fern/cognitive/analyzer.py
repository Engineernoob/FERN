# Repository Analysis - Cognitive Layer
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from fern.tools.llm import complete
from fern.tools.fs import snapshot_repo
from fern.tools.logger import log_info, log_progress

class RepositoryAnalysis:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.analysis = {}
        self.project_type = None
        self.main_language = None
        self.dependencies = {}
        self.structure = {}
        self.readme_content = ""
        self.key_files = {}
        self.framework_detected = None
        self.build_system = None
        
    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive repository analysis"""
        log_progress(f"Analyzing repository: {self.repo_path}")
        
        try:
            # Basic structure analysis
            self._analyze_structure()
            
            # Detect project type and framework
            self._detect_project_type()
            
            # Extract dependencies
            self._extract_dependencies()
            
            # Analyze key files
            self._analyze_key_files()
            
            # Read README if present
            self._analyze_readme()
            
            # Use LLM for deeper understanding
            self._analyze_with_llm()
            
            # Compile final analysis
            self.analysis = {
                "project_type": self.project_type,
                "main_language": self.main_language,
                "framework": self.framework_detected,
                "build_system": self.build_system,
                "dependencies": self.dependencies,
                "structure": self.structure,
                "key_files": self.key_files,
                "readme_summary": self._summarize_readme(),
                "purpose": self._infer_purpose(),
                "complexity_score": self._calculate_complexity(),
                "analysis_timestamp": str(Path().cwd())
            }
            
            log_info(f"Repository analysis completed - Type: {self.project_type}, Framework: {self.framework_detected}")
            return self.analysis
            
        except Exception as e:
            log_info(f"Analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_structure(self):
        """Analyze repository directory structure"""
        structure = {}
        
        try:
            for item in self.repo_path.rglob("*"):
                if item.is_file() and not any(part.startswith('.') for part in item.parts):
                    rel_path = str(item.relative_to(self.repo_path))
                    extension = item.suffix.lower()
                    
                    if extension not in structure:
                        structure[extension] = []
                    structure[extension].append(rel_path)
                    
                    # Track important directories
                    if item.is_dir() and len(item.name) < 20:
                        if item.name.lower() in ['src', 'lib', 'app', 'tests', 'docs', 'scripts']:
                            self.structure[item.name.lower()] = str(item.relative_to(self.repo_path))
                            
        except Exception as e:
            log_info(f"Structure analysis error: {e}")
            self.structure = {"error": str(e)}
    
    def _detect_project_type(self):
        """Detect project type based on key files"""
        key_files = {
            'pyproject.toml': 'python',
            'requirements.txt': 'python',
            'setup.py': 'python',
            'package.json': 'node',
            'Cargo.toml': 'rust',
            'go.mod': 'go',
            'pom.xml': 'java',
            'build.gradle': 'java',
            '.csproj': 'csharp',
            'composer.json': 'php',
            'Gemfile': 'ruby'
        }
        
        for filename, lang in key_files.items():
            if (self.repo_path / filename).exists():
                self.main_language = lang
                break
        else:
            # Fallback to file extension analysis
            try:
                extensions = {}
                for file in self.repo_path.rglob("*.py"):
                    extensions['py'] = extensions.get('py', 0) + 1
                for file in self.repo_path.rglob("*.js"):
                    extensions['js'] = extensions.get('js', 0) + 1
                for file in self.repo_path.rglob("*.ts"):
                    extensions['ts'] = extensions.get('ts', 0) + 1
                    
                if extensions:
                    self.main_language = max(extensions, key=extensions.get)
                else:
                    self.main_language = "unknown"
            except Exception:
                self.main_language = "unknown"
    
    def _extract_dependencies(self):
        """Extract dependencies from various configuration files"""
        try:
            # Python dependencies
            if (self.repo_path / "requirements.txt").exists():
                req_content = (self.repo_path / "requirements.txt").read_text()
                self.dependencies['python'] = [line.strip() for line in req_content.split('\n') if line.strip() and not line.startswith('#')]
            
            if (self.repo_path / "pyproject.toml").exists():
                try:
                    import tomllib
                    with open(self.repo_path / "pyproject.toml", "rb") as f:
                        pyproject = tomllib.load(f)
                    
                    deps = pyproject.get('project', {}).get('dependencies', [])
                    dev_deps = pyproject.get('project', {}).get('optional-dependencies', {})
                    
                    if deps:
                        self.dependencies['python_main'] = deps
                    if dev_deps:
                        self.dependencies['python_dev'] = dev_deps
                except Exception as e:
                    log_info(f"Could not parse pyproject.toml: {e}")
            
            # Node.js dependencies
            if (self.repo_path / "package.json").exists():
                try:
                    package_json = json.loads((self.repo_path / "package.json").read_text())
                    self.dependencies['node'] = {
                        'dependencies': list(package_json.get('dependencies', {}).keys()),
                        'devDependencies': list(package_json.get('devDependencies', {}).keys())
                    }
                except Exception as e:
                    log_info(f"Could not parse package.json: {e}")
            
            # Rust dependencies
            if (self.repo_path / "Cargo.toml").exists():
                try:
                    cargo_toml = (self.repo_path / "Cargo.toml").read_text()
                    deps = re.findall(r'^([a-zA-Z0-9_-]+)\s*=', cargo_toml, re.MULTILINE)
                    self.dependencies['rust'] = deps
                except Exception as e:
                    log_info(f"Could not parse Cargo.toml: {e}")
                    
        except Exception as e:
            log_info(f"Dependency extraction error: {e}")
    
    def _analyze_key_files(self):
        """Analyze key configuration and source files"""
        key_patterns = {
            'config': ['*.conf', '*.config', '*.ini', '*.cfg', 'config/*'],
            'docker': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'],
            'ci': ['.github/workflows/*', '.gitlab-ci.yml', '.travis.yml'],
            'docs': ['README*', 'docs/*', '*.md'],
            'tests': ['test*', 'tests/*', '*_test*', '*Test*']
        }
        
        for category, patterns in key_patterns.items():
            self.key_files[category] = []
            
            for pattern in patterns:
                if '*' in pattern:
                    try:
                        for match in self.repo_path.rglob(pattern):
                            if match.is_file():
                                self.key_files[category].append(str(match.relative_to(self.repo_path)))
                    except Exception:
                        pass
                else:
                    file_path = self.repo_path / pattern
                    if file_path.exists():
                        self.key_files[category].append(pattern)
    
    def _analyze_readme(self):
        """Extract and analyze README content"""
        readme_files = list(self.repo_path.glob("README*"))
        if readme_files:
            try:
                readme_file = readme_files[0]
                self.readme_content = readme_file.read_text(encoding='utf-8', errors='ignore')
            except Exception as e:
                log_info(f"Could not read README: {e}")
    
    def _analyze_with_llm(self):
        """Use LLM for deeper project understanding"""
        try:
            prompt = f"""Analyze this repository snapshot and identify:

1. Framework/CMS used (if any)
2. Primary purpose/functionality  
3. Target deployment environment
4. Key architectural patterns
5. Complexity level (simple/moderate/complex)

Repository files:
{self._get_file_summary()}

Return only JSON with these keys."""
            
            response = complete(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                llm_analysis = json.loads(json_match.group())
                self.framework_detected = llm_analysis.get('framework')
                # Add other LLM insights to analysis
                if 'complexity' in llm_analysis:
                    self.analysis['complexity'] = llm_analysis['complexity']
                    
        except Exception as e:
            log_info(f"LLM analysis failed: {e}")
    
    def _get_file_summary(self) -> str:
        """Get summary of repository files for LLM analysis"""
        summary_parts = []
        
        # Top-level files
        try:
            for item in self.repo_path.iterdir():
                if item.is_file() and not item.name.startswith('.'):
                    summary_parts.append(f"File: {item.name}")
                elif item.is_dir() and not item.name.startswith('.'):
                    summary_parts.append(f"Dir: {item.name}/")
        except Exception:
            pass
            
        # Key framework files
        framework_files = ['package.json', 'pyproject.toml', 'Cargo.toml', 'go.mod', 'pom.xml']
        for fw_file in framework_files:
            fw_path = self.repo_path / fw_file
            if fw_path.exists():
                summary_parts.append(f"Framework config: {fw_file}")
        
        return "\n".join(summary_parts[:50])  # Limit to avoid token limits
    
    def _summarize_readme(self) -> str:
        """Create a summary of README content"""
        if not self.readme_content:
            return "No README found"
        
        try:
            # Extract title, description, and key sections
            lines = self.readme_content.split('\n')
            title = lines[0] if lines else ""
            description_lines = []
            
            for line in lines[1:]:
                if line.strip() and not line.startswith('#') and len(description_lines) < 5:
                    description_lines.append(line.strip())
                if len(description_lines) >= 5:
                    break
            
            return f"Title: {title}\nDescription: {' '.join(description_lines)}"
            
        except Exception:
            return "README analysis failed"
    
    def _infer_purpose(self) -> str:
        """Infer the project's primary purpose"""
        if not self.readme_content:
            return "Unknown purpose"
        
        # Simple heuristic based on README content
        readme_lower = self.readme_content.lower()
        
        purposes = {
            'web application': ['web', 'http', 'server', 'api'],
            'library/package': ['library', 'package', 'sdk', 'module'],
            'tool/utility': ['tool', 'utility', 'script', 'cli'],
            'data analysis': ['data', 'analytics', 'machine learning', 'ml'],
            'mobile app': ['mobile', 'ios', 'android'],
            'game': ['game', 'gaming', 'play']
        }
        
        for purpose, keywords in purposes.items():
            if any(keyword in readme_lower for keyword in keywords):
                return purpose
        
        return "General software project"
    
    def _calculate_complexity(self) -> str:
        """Calculate project complexity score"""
        score = 0
        
        # Count file types
        total_files = 0
        try:
            for _ in self.repo_path.rglob("*"):
                if Path(_).is_file():
                    total_files += 1
        except Exception:
            pass
        
        if total_files > 100:
            score += 3
        elif total_files > 20:
            score += 2
        elif total_files > 5:
            score += 1
        
        # Check for configuration complexity
        config_files = sum(len(files) for files in self.key_files.values() if files)
        if config_files > 10:
            score += 2
        elif config_files > 5:
            score += 1
        
        # Check dependency count
        total_deps = 0
        for dep_list in self.dependencies.values():
            if isinstance(dep_list, list):
                total_deps += len(dep_list)
            elif isinstance(dep_list, dict):
                for sub_list in dep_list.values():
                    if isinstance(sub_list, list):
                        total_deps += len(sub_list)
        
        if total_deps > 50:
            score += 3
        elif total_deps > 20:
            score += 2
        elif total_deps > 5:
            score += 1
        
        # Determine complexity level
        if score >= 6:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"

def analyze_repo(repo_path: Path, analysis_depth: str = "standard") -> Dict[str, Any]:
    """
    Analyze repository structure, dependencies, and purpose.
    
    Args:
        repo_path: Path to repository to analyze
        analysis_depth: "quick", "standard", or "deep" analysis
        
    Returns:
        Dictionary containing comprehensive repository analysis
    """
    analyzer = RepositoryAnalysis(repo_path)
    
    if analysis_depth == "quick":
        # Quick analysis - just structure and basic info
        analyzer._analyze_structure()
        analyzer._detect_project_type()
        analyzer._extract_dependencies()
        analyzer._analyze_readme()
        
        analyzer.analysis = {
            "project_type": analyzer.project_type,
            "main_language": analyzer.main_language,
            "dependencies": analyzer.dependencies,
            "readme_summary": analyzer._summarize_readme(),
            "purpose": analyzer._infer_purpose()
        }
    else:
        # Standard or deep analysis
        analyzer.analysis = analyzer.analyze()
    
    log_info(f"Repository analysis completed: {repo_path}")
    return analyzer.analysis