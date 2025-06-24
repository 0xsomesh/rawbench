import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, Dict, Callable, Optional, List

def get_variables_directories() -> List[str]:
    """
    Get the list of directories to search for variable modules.
    
    Returns a list of directories in the following order:
    1. Directory specified by PROMPT_EVAL_VARIABLES_DIR environment variable if set
    2. 'variables' directory in the current working directory
    3. 'variables' directory in the package installation directory
    """
    directories = []
    
    # Check environment variable first
    env_dir = os.environ.get("PROMPT_EVAL_VARIABLES_DIR")
    if env_dir:
        directories.append(env_dir)
    
    # Check current working directory
    cwd_variables = os.path.join(os.getcwd(), "variables")
    directories.append(cwd_variables)
    
    # Use the source directory (we're not dealing with installed package case yet)
    source_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    source_variables = os.path.join(source_dir, "variables")
    directories.append(source_variables)
    
    return directories

def find_variable_module(module_name: str) -> Optional[str]:
    """
    Find the first occurrence of a variable module in the search directories.
    
    Args:
        module_name: The name of the Python file (without .py extension)
        
    Returns:
        The full path to the module file if found, None otherwise
    """
    for directory in get_variables_directories():
        module_path = os.path.join(directory, f"{module_name}.py")
        if os.path.isfile(module_path):
            return module_path
    return None

def load_variable_function(module_name: str) -> Callable[[], Any]:
    """
    Dynamically loads a function from a Python file in the variables directories.
    
    Args:
        module_name: The name of the Python file (without .py extension)
        
    Returns:
        The loaded function that can be called to get the variable value
        
    Raises:
        ImportError: If the module or function cannot be found in any search directory
        AttributeError: If the module doesn't contain a function with the same name
    """
    module_path = find_variable_module(module_name)
    if not module_path:
        search_dirs = "\n  - ".join(get_variables_directories())
        raise ImportError(f"Variable module '{module_name}.py' not found in any of these directories:\n  - {search_dirs}")
    
    # Load the module
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec or not spec.loader:
        raise ImportError(f"Could not load module specification for {module_name}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Get the function with the same name as the module
    if not hasattr(module, module_name):
        raise AttributeError(f"Module {module_name} must contain a function named {module_name}")
    
    return getattr(module, module_name)

def load_variables(variable_configs: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """
    Loads all variable functions from the config and executes them to get their values.
    
    Args:
        variable_configs: Dictionary of variable configurations from the YAML file
        
    Returns:
        Dictionary mapping variable names to their computed values
    """
    variables = {}
    
    for var_id, var_config in variable_configs.items():
        if "function" in var_config:
            func = load_variable_function(var_config["function"])
            variables[var_id] = func()
        else:
            # Support for static values
            variables[var_id] = var_config.get("value", "")
            
    return variables
