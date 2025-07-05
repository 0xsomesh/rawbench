#!/usr/bin/env python3
"""
CLI tool for managing prompt evaluations with JSON and YAML file support.
"""

import sys
import click
from pathlib import Path
from ..services.evaluation import EvaluationService
from ..services.setup import SetupService 
from ..services.server import WebServer
from ..utils import load_env_file

# Load environment variables from .env file
load_env_file()

# Initialize services
evaluation_service = EvaluationService()
setup_service = SetupService()
web_server = WebServer()

@click.group()
def main():
    """RawBench CLI tool for managing evaluations"""
    pass

@main.command()
@click.argument('config_path')
@click.option('-o', '--output', help='Output file path for results')
@click.option('--serve', is_flag=True, help='Start web server to view results')
@click.option('--port', default=8000, help='Port for web server (default: 8000)')
def run(config_path: str, output: str = None, serve: bool = False, port: int = 8000):
    """Run a benchmark evaluation"""
    if not output:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = f"{Path(config_path).stem}_{timestamp}"
        output_path = f"results/{output_file_name}"
    else:
        output_path = output
    
    try:
        evaluation_service.run_evaluation(
            config_path=config_path,
            output_path=output_path,
        )
        click.echo("✅ Evaluation completed successfully")
        
        if serve:            
            click.echo(f"🌐 Starting web server on http://localhost:{port}")
            click.echo(f"📊 Viewing results from: {output_path}.json")
            web_server.serve_specific_result(output_path, port)
            
    except Exception as e:
        click.echo(f"❌ Error running evaluation: {str(e)}", err=True)
        sys.exit(1)

@main.command()
@click.option('--dir', default='evaluations', help='Directory containing evaluation files')
def list(dir: str):
    """List available evaluation configurations"""
    try:
        evaluations = evaluation_service.list(dir)
        if not evaluations:
            click.echo("No evaluation configurations found.")
            return

        click.echo(f"\nFound {len(evaluations)} evaluation files:")
        click.echo("-" * 60)
        for eval_info in evaluations:
            click.echo(f"File: {eval_info['path']}")
            click.echo(f"Name: {eval_info['name']}")
            click.echo(f"Models: {eval_info['description']}")
            click.echo(f"Tests: {eval_info['num_tests']}")
            click.echo("-" * 60)
    except Exception as e:
        click.echo(f"❌ Error listing evaluations: {str(e)}", err=True)
        sys.exit(1)

@main.command()
@click.option('--port', default=8000, help='Port for web server (default: 8000)')
def serve(port: int = 8000):
    """Start web server to browse all evaluation results"""
    try:
        click.echo(f"🌐 Starting web server on http://localhost:{port}")
        click.echo("📊 Browse all evaluation results")
        web_server.serve_all_results(port)
    except Exception as e:
        click.echo(f"❌ Error starting web server: {str(e)}", err=True)
        sys.exit(1)

@click.argument('dir')
@main.command()
def init(dir: str):
    """Initialize project structure"""
    try:
        project_info = setup_service.init_project(dir)
        click.echo(f"{'✅ Created project structure at:':<40} {project_info}")
        click.echo("✅ Created: .env file")
        click.echo("✅ Created: example evaluation template")
    except Exception as e:
        click.echo(f"❌ Error initializing project: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()