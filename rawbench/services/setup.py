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
                "id": "openai/gpt-4o-mini",
                "name": "openai/gpt-4o-mini",
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
        
        config_path = project_dir / "evaluations" / "template.yaml"
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
########### PROVIDERS ###########
# Paste API keys for the providers you want to use

# OpenAI
OPENAI_API_KEY = ""
OPENAI_BASE_URL = ""
# Cohere
COHERE_API_KEY = ""
# OpenRouter
OR_SITE_URL = ""
OR_APP_NAME = "LiteLLM Example app"
OR_API_KEY = ""
# Azure API base URL
AZURE_API_BASE = ""
# Azure API version
AZURE_API_VERSION = ""
# Azure API key
AZURE_API_KEY = ""
# Replicate
REPLICATE_API_KEY = ""
REPLICATE_API_TOKEN = ""
# Anthropic
ANTHROPIC_API_KEY = ""
# Infisical
INFISICAL_TOKEN = ""
# Novita AI
NOVITA_API_KEY = ""
# INFINITY
INFINITY_API_KEY = ""
# Groq
GROQ_API_KEY = ""
# DeepSeek
DEEPSEEK_API_KEY = ""
# Hugging Face
HUGGINGFACE_API_KEY = ""
# Gemini
GEMINI_API_KEY = ""
# Ollama
OLLAMA_API_KEY = ""


#################################





########### RAWBENCH ###########

# Custom variables directory (optional)
PROMPT_EVAL_VARIABLES_DIR=variables

# Server configuration (optional)
RAWBENCH_SERVER_PORT=8000
RAWBENCH_SERVER_HOST=0.0.0.0
"""
        with open(project_dir / ".env", "w") as f:
            f.write(env_content)