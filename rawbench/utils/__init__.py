"""
Utility functions and helpers.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

__all__ = ["load_env_file", "get_env_var"]

def load_env_file(env_path: str = None) -> None:
    """
    Load environment variables from a .env file.
    
    Args:
        env_path: Path to the .env file. If None, searches for .env in current directory.
    """
    if env_path is None:
        # Look for .env file in current working directory
        env_path = Path.cwd() / ".env"
    else:
        env_path = Path(env_path)
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        print(f"⚠️  No .env file found at {env_path}")

def get_env_var(key: str, default: str = None) -> str:
    """
    Get an environment variable with optional default value.
    
    Args:
        key: Environment variable name
        default: Default value if environment variable is not set
        
    Returns:
        Environment variable value or default
    """
    return os.environ.get(key, default) 