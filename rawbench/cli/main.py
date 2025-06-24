#!/usr/bin/env python3
"""
CLI tool for managing prompt evaluations with JSON and YAML file support.
"""

import argparse
import sys
import os
from ..core.evaluation import Evaluation
from ..config.loader import load_config, validate_config


def list_evaluations(evaluations_dir="evaluations"):
    """List all evaluation JSON and YAML files in the evaluations directory."""
    if not os.path.exists(evaluations_dir):
        print(f"Evaluations directory '{evaluations_dir}' not found.")
        return
    
    config_files = [f for f in os.listdir(evaluations_dir) 
                   if f.endswith(('.json', '.yaml', '.yml'))]
    if not config_files:
        print("No evaluation configuration files found.")
        return
    
    print(f"Found {len(config_files)} evaluation files:")
    print("-" * 60)
    for filename in config_files:
        filepath = os.path.join(evaluations_dir, filename)
        try:
            config = load_config(filepath)
            print(f"File: {filename}")
            print(f"Name: {config.get('name', 'Unnamed')}")
            print(f"Models: {len(config.get('models', []))}")
            print(f"Tests: {len(config.get('tests', []))}")
            print(f"Tools: {len(config.get('tools', []))}")
            print(f"Variables: {len(config.get('variables', []))}")
            print(f"Prompts: {len(config.get('prompts', []))}")
            print("-" * 60)
        except Exception as e:
            print(f"File: {filename} (Error reading: {e})")
            print("-" * 60)



def create_template(output_file):
    """Create a template evaluation configuration file in YAML format."""
    template = {
        "id": "Default Evaluation",
        "description": "A template for evaluating chat model responses",
        "models": [
            {
                "id": "gpt-4",
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            {
                "id": "gpt-35-turbo",
                "provider": "openai", 
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        ],
        "prompts": [
            {
                "id": "default",
                "system": "You are a helpful assistant focused on clear and accurate responses."
            },
            {
                "id": "analytical",
                "system": "You are an analytical assistant focused on detailed evaluation."
            }
        ],
        "tests": [
            {
                "id": "basic-test",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, how are you?"
                    }
                ]
            }
        ]
    }
    
    try:
        ext = os.path.splitext(output_file)[1].lower()
        
        if ext in ['.yaml', '.yml']:
            import yaml
            with open(output_file, 'w') as f:
                yaml.dump(template, f, default_flow_style=False, indent=2, allow_unicode=True)
        else:
            import json
            with open(output_file, 'w') as f:
                json.dump(template, f, indent=2)
        
        print(f"✅ Template created: {output_file}")
    except Exception as e:
        print(f"❌ Error creating template: {e}")
        sys.exit(1)


def list_results():
    """List all result folders."""
    if not os.path.exists("results"):
        print("No results directory found.")
        return
    
    result_dirs = [d for d in os.listdir("results") if os.path.isdir(os.path.join("results", d))]
    if not result_dirs:
        print("No result folders found.")
        return
    
    print(f"Found {len(result_dirs)} result folders:")
    print("-" * 60)
    for result_dir in sorted(result_dirs, reverse=True):
        dir_path = os.path.join("results", result_dir)
        json_file = os.path.join(dir_path, "results.json")
        markdown_file = os.path.join(dir_path, "report.md")
        
        print(f"📁 {result_dir}")
        if os.path.exists(json_file):
            print(f"   📄 JSON: results.json")
        if os.path.exists(markdown_file):
            print(f"   📝 Report: report.md")
        print("-" * 60)


def init_project():
    """Initialize project structure with required directories and files."""
    # Create directories
    directories = ['evaluations', 'results', 'variables']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")
    
    # Create .env file if it doesn't exist
    env_file = '.env'
    if not os.path.exists(env_file):
        env_content = """# OpenAI API Key
OPENAI_API_KEY=your-api-key-here

# Other API Keys can be added here
# ANTHROPIC_API_KEY=your-anthropic-key-here
# AZURE_API_KEY=your-azure-key-here
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"Created file: {env_file}")
    else:
        print(f"File already exists: {env_file}")
    
    # Create template evaluation file
    eval_file = os.path.join('evaluations', 'template.yaml')
    if not os.path.exists(eval_file):
        create_template(eval_file)
        print(f"Created template evaluation: {eval_file}")
    else:
        print(f"Template evaluation already exists: {eval_file}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="RawBench Prompt Evaluation CLI tool"
    )
    
    # Add commands
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize project structure")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all evaluation files")
    list_parser.add_argument(
        "--dir",
        default="evaluations",
        help="Directory containing evaluation files (default: evaluations)"
    )
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run an evaluation")
    run_parser.add_argument(
        "file",
        help="Path to the evaluation YAML file"
    )
    run_parser.add_argument(
        "--output",
        help="Output file for results (default: <evaluation_id>.json)"
    )
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_project()
    elif args.command == "list":
        list_evaluations(args.dir)
    elif args.command == "run":
        # Load and validate the config
        config = load_config(args.file)
        if validate_config(config):
            # Pass the config file path to Evaluation
            evaluation = Evaluation(config)
            results = evaluation.run()

            print(f"✅ Evaluation '{evaluation.id}' completed with {len(results)} results.")
            
            print(f"Exporting results to {args.output if args.output else f'{evaluation.id}.json'}")
            evaluation.export_results(args.output if args.output else f"{evaluation.id}.json")
            # # Transform results to markdown
            # Transformer = get_transformer()
            # transformer = Transformer(evaluation_name, args.file)
            # transformer.save_results(results, args.output)
        else:
            print("❌ Invalid configuration file. Please check the structure and required fields.")
            sys.exit(1)


    else:
        parser.print_help()

if __name__ == "__main__":
    main()