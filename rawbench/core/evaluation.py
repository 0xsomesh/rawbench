from typing import Any, Dict, List
from .model import Model
import os
import time
from ..utils.credentials import Credential
from ..results.result import Result, ResultCollector
from ..config.loader import load_config, validate_config
from .variables import load_variables


class Evaluation:
    def __init__(self, config):
        """Initialize an evaluation from a config file."""
        self.id = config['id']
        self.models = config['models']
        self.prompts = config['prompts']
        self.tests = config['tests']
        # Load variables if present in config
        self.variables = load_variables(config.get('variables', {}))
        
        # Initialize components from config
        if not self.models:
            raise ValueError("No models defined in configuration")
            
        if not self.tests:
            raise ValueError("No tests defined in configuration")
            
        self.tools = config.get("tools", [])
            
        self.result_collector = ResultCollector()
    
    def run(self):
        """Run all tests against all models."""
        
        print(f"Running evaluation: {self.id}")
        print(f"Models: {len(self.models)}, Tests: {len(self.tests)}")
        tools = self.tools if self.tools else []

        for model_config in self.models:
            print(f"  Testing model: {model_config['name']}")

            model_id = model_config['id']
            
            # Create model instance
            model = Model(
                model_config['id'],
                model_config['name'], 
                model_config['provider'], 
                model_config.get('temperature', 0.0),
                model_config.get('max_tokens', 1000),
                model_config.get('top_p', 1.0),
                model_config.get('frequency_penalty', 0.0),
                model_config.get('presence_penalty', 0.0),
                model_config.get('seed', None),
                Credential(os.getenv("OPENAI_API_KEY"))
            )
            for prompt in self.prompts:
                prompt_id = prompt['id']
                print(f"    Using prompt: {prompt_id}")
                system_prompt = prompt['system']
                # replace {{variable_name}} with the variables.function
                for var_id, var_value in self.variables.items():
                    system_prompt = system_prompt.replace(f"{{{{{var_id}}}}}", str(var_value))

                print(f"      System Prompt: {system_prompt}...")

                for test in self.tests:
                    test_id = test['id']
                    print(f"        Running test: {test['id']}, Model: {model_config['id']}, System Prompt: {system_prompt[:30]}...")
                    complete_messages = test['messages']

                    # Run the test
                    response, latency = model.run(
                        test, 
                        tools=tools,
                        tool_execution_config=test.get('tool_execution'),
                        system_prompt=system_prompt
                    )

                    result = Result(
                        id=f"{self.id}::{model_id}::{prompt_id}::{test_id}",
                        model_id=model.id,
                        prompt_id=prompt_id,
                        test_id=test_id,
                        input_messages=complete_messages,
                        output_content=response.choices[0].message.content,
                        output_message=response.choices[0].message.to_dict(),
                        completion_tokens=response.usage.completion_tokens,
                        prompt_tokens=response.usage.prompt_tokens,
                        total_tokens=response.usage.total_tokens,
                        latency_ms=latency,
                    )
                    self.result_collector.add_result(result)

        # Print summary
        summary = self.result_collector.get_summary()
        print(f"\nEvaluation Summary:")
        print(f"  Total Results: {summary['total_results']}")
        if summary['total_tokens'] > 0:
            print(f"  Total Tokens: {summary['total_tokens']}")
        if summary['avg_latency'] > 0:
            print(f"  Avg Latency: {summary['avg_latency']:.0f}ms")
        return self.result_collector
    
    def get_results(self):
        """Get all results for this evaluation."""
        return [r.to_dict() for r in self.result_collector.results]
    
    def get_results_summary(self):
        """Get a summary of results for this evaluation."""
        return self.result_collector.get_summary()
    
    def export_results(self, filepath):
        """Export results to JSON file."""
        self.result_collector.export_to_json(filepath)
    
    def close(self):
        """No database connection to close."""
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()