# Dynamic Tool Creation System

This directory contains dynamically created tools that are generated on-the-fly based on user needs. The system can automatically create new tools when existing ones don't meet a specific requirement.

## How It Works

1. When a user asks a question that requires information not available through existing tools, the system detects this need.
2. The Dynamic Tool Manager analyzes the request and determines what kind of tool would be needed.
3. It generates code for a new tool using the AI model.
4. The new tool is saved as a Python file in this directory.
5. The tool is automatically loaded and registered with the MCP server.
6. The character can then use the new tool to respond to the user's request.

## Example Use Cases

- **Currency Conversion**: If a user asks "What is 1 USD in Turkish Lira?", the system can create a currency conversion tool that fetches real-time exchange rates.
- **Weather Forecasts**: If a user asks about weather forecasts for specific locations, a weather forecast tool can be created.
- **Stock Prices**: If a user asks about stock prices, a stock price tool can be created.
- **Translation**: If a user needs text translated between languages, a translation tool can be created.

## Included Example

This directory includes an example currency converter tool (`currency_converter_tool.py`) that demonstrates how dynamic tools are structured. This tool:

1. Fetches real-time exchange rates from a public API
2. Converts amounts between different currencies
3. Returns detailed information about the conversion

## Creating Your Own Tools

While the system can create tools automatically, you can also manually create tools by:

1. Creating a new Python file in this directory
2. Defining a class that inherits from `MCPTool`
3. Implementing the required methods (`__init__` and `execute`)
4. The tool will be automatically loaded when the application starts

## Tool Structure

Each tool should follow this basic structure:

```python
from mcp_server import MCPTool

class YourToolName(MCPTool):
    def __init__(self):
        super().__init__(
            name="your_tool_name",
            description="Description of what your tool does"
        )
    
    def execute(self, args):
        # Tool implementation
        # Process args and return results
        return {"result": "your result"}
```

## Security Considerations

The dynamic tool creation system has some security implications:

1. Generated code is executed in the application's environment
2. External API calls may expose sensitive information
3. Resource usage may be unpredictable

In a production environment, additional safeguards should be implemented:

1. Code sandboxing
2. Rate limiting
3. API key management
4. Resource usage monitoring