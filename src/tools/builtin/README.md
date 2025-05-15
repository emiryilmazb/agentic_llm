# Built-in Tools

This directory contains the built-in tools that are available to all agentic characters in the system. These tools provide core functionality that characters can use to respond to user requests.

## Available Tools

The following built-in tools are included:

1. **search_wikipedia.py**: Searches Wikipedia for information on a topic
2. **get_current_time.py**: Gets the current date and time
3. **get_weather.py**: Gets weather information for a specified location
4. **open_website.py**: Opens a specified URL in the browser
5. **calculate_math.py**: Evaluates mathematical expressions

## Tool Structure

Each built-in tool follows this basic structure:

```python
from src.tools.base import MCPTool
from typing import Dict, Any

class MyToolName(MCPTool):
    def __init__(self):
        super().__init__(
            name="my_tool_name",
            description="Description of what your tool does"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required arguments
        validation_error = self.validate_args(args, ["required_param"])
        if validation_error:
            return validation_error
            
        # Extract parameters
        param = args.get("param", "default_value")
        
        # Implement tool functionality
        try:
            # Your implementation here
            result = {"result": "operation result"}
            return result
        except Exception as e:
            return self.handle_error(e)
```

## Adding New Tools

To add a new built-in tool:

1. Create a new Python file in this directory
2. Define a class that inherits from `MCPTool`
3. Implement the required methods (`__init__` and `execute`)
4. Register the tool in `src/core/mcp_server.py`

Example:

```python
# In src/tools/builtin/my_new_tool.py
from src.tools.base import MCPTool
from typing import Dict, Any

class MyNewTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="my_new_tool",
            description="Description of what your tool does"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation here
        return {"result": "operation result"}

# In src/core/mcp_server.py
from src.tools.builtin.my_new_tool import MyNewTool

# Add to the load_builtin_tools function
def load_builtin_tools(server: MCPServer) -> None:
    # ...
    server.register_tool(MyNewTool())
    # ...
```

## Best Practices

When creating built-in tools, follow these best practices:

1. **Validation**: Always validate required arguments using `self.validate_args()`
2. **Error Handling**: Use try-except blocks to catch and handle errors
3. **Logging**: Use the logger to log important events and errors
4. **Documentation**: Include docstrings for the class and methods
5. **Type Hints**: Use type hints to improve code readability and IDE support
6. **Return Format**: Always return a dictionary with appropriate keys
7. **Security**: Be careful with user input, especially when executing commands or making API calls