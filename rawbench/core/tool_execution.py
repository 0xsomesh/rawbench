import json
from typing import Dict, List, Any

class ToolExecutionHandler:
    def __init__(self, config: Dict[str, Any], tools: List[Dict[str, Any]] = None):
        self.config = config
        self.tools = tools or []
        self.mode = config.get('mode', 'mock')
        self.max_iterations = config.get('max_iterations', 5)
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return the result."""
        if self.mode == 'mock':
            return self._get_mock_response(tool_name)
        elif self.mode == 'actual':
            return self._execute_actual_tool(tool_name, tool_input)
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")
    
    def _get_mock_response(self, tool_name: str) -> str:
        """Get mock response with priority: test-specific > global tool mock > default."""
        
        # 1. Check test-specific mock output
        test_mocks = self.config.get('output', [])
        for mock in test_mocks:
            if mock.get('id') == tool_name:
                return mock.get('output', '{}')
        
        # 2. Check global tool mock
        for tool in self.tools:
            if tool.get('name') == tool_name and 'mock' in tool:
                return tool['mock'].get('output', '{}')
        
        # 3. Default mock response
        return json.dumps({"message": f"Mock response for {tool_name}"})
    
    def _execute_actual_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute actual tool (placeholder for future implementation)."""
        return json.dumps({"message": f"Actual tool execution for {tool_name}", "input": tool_input}) 