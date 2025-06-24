import json
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolCall:
    """Represents a tool call with input and output."""
    name: str
    input: Dict[str, Any]
    output: str


class ToolExecutionHandler:
    """Handles different types of tool execution during evaluation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize tool execution handler with configuration.
        
        Args:
            config: Tool execution configuration
        """
        self.config = config
        self.execution_type = config.get('type', 'mock')
    
    def execute_tools(self, response, tools: List[Dict[str, Any]]):
        """
        Execute tools based on the response and return updated response.
        
        Args:
            response: Original API response
            tools: List of tool definitions
            
        Returns:
            Updated response with tool execution results
        """
        if self.execution_type == 'mock':
            return self._execute_mock_tools(response, tools)
        elif self.execution_type == 'actual':
            return self._execute_actual_tools(response, tools)
        else:
            raise ValueError(f"Unsupported execution type: {self.execution_type}")
    
    def _execute_mock_tools(self, response, tools: List[Dict[str, Any]]):
        """Execute tools using mock data."""
        mock_config = self.config.get('mock', {})
        mock_type = mock_config.get('type', 'auto')
        
        if mock_type == 'auto':
            return self._execute_auto_mock_tools(response, tools)
        elif mock_type == 'manual':
            return self._execute_manual_mock_tools(response, tools, mock_config)
        else:
            raise ValueError(f"Unsupported mock type: {mock_type}")
    
    def _execute_auto_mock_tools(self, response, tools: List[Dict[str, Any]]):
        """Execute tools using auto-generated mock data."""
        # For auto mock, we'll use the tool's mock data if available
        # This is a simplified implementation
        return response
    
    def _execute_manual_mock_tools(self, response, tools: List[Dict[str, Any]], mock_config: Dict[str, Any]):
        """Execute tools using manually specified mock data."""
        # For manual mock, we'll use the provided mock data
        # This is a simplified implementation
        return response
    
    def _execute_actual_tools(self, response, tools: List[Dict[str, Any]]):
        """Execute tools using actual API calls."""
        http_config = self.config.get('http', {})
        
        if not http_config:
            raise ValueError("HTTP configuration required for actual tool execution")
        
        # This is a simplified implementation
        # In a real implementation, you would make actual HTTP calls
        return response
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool based on the configuration."""
        if self.execution_type == 'mock':
            return self._execute_mock_tool(tool_name, tool_input)
        elif self.execution_type == 'actual':
            return self._execute_actual_tool(tool_name, tool_input)
        else:
            raise ValueError(f"Unsupported tool execution type: {self.execution_type}")
    
    def _execute_mock_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a mock tool based on the configuration."""
        mock_config = self.config.get('mock', {})
        mock_type = mock_config.get('type', 'auto')
        
        if mock_type == 'auto':
            return self._generate_auto_mock_response(tool_name, tool_input)
        elif mock_type == 'manual':
            return self._get_manual_mock_response(tool_name, tool_input, mock_config.get('tools', []))
        else:
            raise ValueError(f"Unsupported mock type: {mock_type}")
    
    def _execute_actual_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute an actual tool via HTTP."""
        http_config = self.config.get('http', {})
        
        if not http_config:
            raise ValueError("HTTP configuration is required for actual tool execution")
        
        url = http_config.get('url')
        method = http_config.get('method', 'POST')
        headers = http_config.get('headers', {})
        body = http_config.get('body', {})
        
        # Merge tool input with body
        request_body = {**body, **tool_input}
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=request_body)
            elif method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=request_body)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.text
            
        except requests.RequestException as e:
            raise Exception(f"HTTP request failed: {str(e)}")
    
    def _generate_auto_mock_response(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Generate an automatic mock response based on tool name and input."""
        # First, try to find the tool in the tools configuration
        for tool in self.tools:
            if tool.get('name') == tool_name:
                # Check if the tool has a mock configuration
                if 'mock' in tool:
                    mock_config = tool['mock']
                    # Check if the input matches the mock input
                    if mock_config.get('input') == tool_input:
                        return mock_config.get('output', 'No output specified')
                    # If input doesn't match exactly, still return the mock output
                    return mock_config.get('output', 'No output specified')
                
        # If no specific mock found, return a generic response
        return f"Mock response for {tool_name} with input: {json.dumps(tool_input)}"
    
    def _get_manual_mock_response(self, tool_name: str, tool_input: Dict[str, Any], 
                                 manual_tools: List[Dict[str, Any]]) -> str:
        """Get a manual mock response from the configuration."""
        for tool_config in manual_tools:
            if tool_config.get('name') == tool_name:
                # Check if input matches (simple exact match for now)
                if tool_config.get('input') == tool_input:
                    return tool_config.get('output', 'No output specified')
        
        # If no exact match found, return a generic response
        return f"Manual mock response for {tool_name} with input: {json.dumps(tool_input)}"
    
    def should_intercept_tool_calls(self) -> bool:
        """Check if this handler should intercept tool calls."""
        return self.execution_type in ['mock', 'actual']
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for the model."""
        if not self.tools:
            return []
        
        tool_definitions = []
        for tool in self.tools:
            tool_definitions.append({
                "type": "function",
                "function": {
                    "name": tool['name'],
                    "description": tool['description'],
                    "parameters": tool['parameters']
                }
            })
        
        return tool_definitions 