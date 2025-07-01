import os
import time
import json
import litellm
from ..utils.credentials import Credential
from ..results.result import Result
from .tool_execution import ToolExecutionHandler
from litellm import ModelResponse
from dataclasses import dataclass
from typing import List

MAX_ITERATIONS = 10

@dataclass
class Response:
    output_messages: List[ModelResponse]
    latencies: List[int]

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
        
        # Set up litellm
        litellm.set_verbose = False
        
    def run(self, test, tools=None, tool_execution_config=None, system_prompt=None) -> Response:
        """Run a test against this model with tool execution support."""
        messages = []
        response = Response(output_messages=[], latencies=[])
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add test messages
        messages.extend(test['messages'])
        
        # Prepare tools for API
        formatted_tools = None
        if tools:
            formatted_tools = [{
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            } for tool in tools]
        
        # Initialize tool handler
        tool_handler = None
        if tool_execution_config:
            tool_handler = ToolExecutionHandler(tool_execution_config, tools)
        
        # Tool execution loop
        iteration = 0
        max_iterations = tool_handler.max_iterations if tool_handler and tool_handler.max_iterations else MAX_ITERATIONS
        
        while iteration < max_iterations:
            # Make API call
            start_time = time.time()
            model_response = litellm.completion(
                model=self.name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                seed=self.seed,
                tools=formatted_tools,
                tool_choice="auto" if formatted_tools else None
            )
            
            # Track response
            response.latencies.append(int((time.time() - start_time) * 1000))
            print(f"Model Response: {model_response}")
            response.output_messages.append(model_response)
            
            # Check for tool calls
            if (tool_handler and 
                hasattr(model_response.choices[0].message, 'tool_calls') and 
                model_response.choices[0].message.tool_calls):
                
                # Add model message to conversation
                messages.append(model_response.choices[0].message.to_dict())
                
                # Execute tools and add results
                for tool_call in model_response.choices[0].message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_result = tool_handler.execute_tool(tool_name, tool_args)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })
                
                iteration += 1
                continue
            else:
                # No tool calls, we're done
                break
        
        return response