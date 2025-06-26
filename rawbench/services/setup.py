from pathlib import Path
import yaml
from typing import Dict, Any

class SetupService:
    """Handles project setup and configuration"""
    
    def init_project(self, project_name: str) -> str:
        """Initialize a new benchmark project with required structure"""
        project_dir = Path(project_name)
        if project_dir.exists():
            raise ValueError(f"Directory {project_name} already exists")
        
        # Create directory structure
        self._create_directory_structure(project_dir)
        
        # Create template files
        self._create_template_config(project_dir)
        self._create_gitignore(project_dir)
        self.create_environment_file(project_dir)
        
        return str(project_dir)
    
    def _create_directory_structure(self, project_dir: Path):
        """Create the basic project directory structure"""
        project_dir.mkdir()
        (project_dir / "tests").mkdir()
        (project_dir / "results").mkdir()
    
    def _create_template_config(self, project_dir: Path):
        """Create a template test configuration"""
        template_config = {
            "id": "template_evaluation",
            "models": [{
                "id": "gpt-4o-mini",
                "name": "gpt-4o-mini",
                "provider": "openai",
            }],
            "prompts": [{
                "id": "default",
                "system": "You are a helpful assistant focused on clear and accurate responses."
            }],
            "tests": [
                {
                    "id": "example_test",
                    "description": "Example test case",
                    "messages": [
                        {"role": "user", "content": "What is 2+2?"}
                    ],
                }
            ]
        }
        
        config_path = project_dir / "tests" / "template.yaml"
        with open(config_path, "w") as f:
            yaml.dump(template_config, f, sort_keys=False)
    
    def _create_gitignore(self, project_dir: Path):
        """Create a .gitignore file with common patterns"""
        gitignore_content = """
results/
__pycache__/
*.pyc
.env
.DS_Store
        """.strip()
        
        with open(project_dir / ".gitignore", "w") as f:
            f.write(gitignore_content)

    def create_environment_file(self, project_dir: Path):
        """Create a .env file with default environment variables"""
        env_content = """# Environment variables for RawBench
OPENAI_API_KEY=your_openai_api_key_here
"""
        with open(project_dir / ".env", "w") as f:
            f.write(env_content)