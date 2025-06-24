import os
import time
import litellm
from ..utils.credentials import Credential
from ..results.result import Result
from .tool_execution import ToolExecutionHandler
from litellm import ModelResponse


class Response:
    def __init__(self, evaluation_id, model_id, test_id, model_name, test_name, input_messages, output_content, output_messages, tokens_used=None, cost=None, latency_ms=0, status='success', error_message=None, metadata=None):
        self.evaluation_id = evaluation_id
        self.model_id = model_id
        self.test_id = test_id
        self.model_name = model_name
        self.test_name = test_name
        self.input_messages = input_messages
        self.output_content = output_content
        self.output_messages = output_messages
        self.tokens_used = tokens_used
        self.cost = cost
        self.latency_ms = latency_ms
        self.status = status
        self.error_message = error_message or ""
        self.metadata = metadata or {}

class Model:
    def __init__(self, id, name, provider, temperature=0.0, max_tokens=1000, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0, seed=None, credential=None):
        self.id = id
        self.name = name
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.seed = seed
        self.credential = credential or Credential(os.getenv("OPENAI_API_KEY"))
        
        # Set up litellm
        litellm.set_verbose = False
        
    def run(self, test, tools=None, tool_execution_config=None, system_prompt=None) -> tuple[ModelResponse, int]:
        """Run a test against this model."""
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add test messages
        messages.extend(test['messages'])
        
        # Prepare function calling if tools are provided
        function_calling = None
        if tools:
            # Format tools for OpenAI API
            tools = [{
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            } for tool in tools]
            function_calling = "auto"
        
        # Start timer
        start_time = time.time()
        
        # Make the API call
        response = litellm.completion(
            model=self.name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            seed=self.seed,
            tools=tools,
            tool_choice=function_calling
        )
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Handle tool execution if needed
        if tool_execution_config and hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            tool_handler = ToolExecutionHandler(tool_execution_config)
            response = tool_handler.execute_tools(response, tools)
                    
        return response, latency_ms