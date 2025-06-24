import os
import yaml
from typing import Dict, Any


def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load configuration from JSON or YAML file with support for YAML anchors and references.
    
    Args:
        config_file: Path to the configuration file (.json, .yaml, or .yml)
        
    Returns:
        Dictionary containing the configuration
        
    Raises:
        ValueError: If file type is not supported
        FileNotFoundError: If config file doesn't exist
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    ext = os.path.splitext(config_file)[1].lower()
    
    with open(config_file, 'r', encoding='utf-8') as f:
        if ext in ['.yaml', '.yml']:
            # Load YAML with support for anchors and references
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config file type: {ext}. Use .yaml, or .yml")


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure.
    
    Args:
        config: Dictionary containing the configuration
        
    Returns:
        True if valid, raises ValueError otherwise
    """
    required_fields = ["id", "models", "prompts", "tests"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate models
    if not isinstance(config["models"], list) or not config["models"]:
        raise ValueError("'models' must be a non-empty list")
    
    for model in config["models"]:
        if "id" not in model or "provider" not in model or "name" not in model:
            raise ValueError("Each model must have 'id', 'name' and 'provider' fields")
    
    # Validate prompts if present
    if "prompts" in config:
        if not isinstance(config["prompts"], list):
            raise ValueError("'prompts' must be a list")
        
        for prompt in config["prompts"]:
            if "id" not in prompt or "system" not in prompt:
                raise ValueError("Each prompt must have 'id' and 'system' fields")
    
    # Validate tests
    if not isinstance(config["tests"], list) or not config["tests"]:
        raise ValueError("'tests' must be a non-empty list")
    
    for test in config["tests"]:
        if "id" not in test or "messages" not in test:
            raise ValueError("Each test must have 'id' and 'messages' fields")
        if not isinstance(test["messages"], list):
            raise ValueError("Test 'messages' must be a list")
    
    # Validate tools if present
    if "tools" in config:
        if not isinstance(config["tools"], list):
            raise ValueError("'tools' must be a list")
        
        for tool in config["tools"]:
            if "id" not in tool or "description" not in tool or "name" not in tool:
                raise ValueError("Each tool must have 'id', 'name' and 'description' fields")
    
    return True