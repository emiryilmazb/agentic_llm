# Dynamic Tools

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

## Included Examples

This directory includes example dynamic tools that demonstrate how dynamic tools are structured:

1. **currency_converter_tool.py**: A tool for converting between different currencies using real-time exchange rates.
2. **weather_forecast_tool.py**: A tool for getting weather forecasts for specific locations.

## Tool Structure

Each dynamic tool follows this basic structure:

```python
from src.tools.base import DynamicTool
import datetime
from typing import Dict, Any

class MyToolName(DynamicTool):
    def __init__(self):
        super().__init__(
            name="my_tool_name",
            description="Description of what your tool does",
            created_at=datetime.datetime.now().isoformat()
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

## Deleted Tools

The system keeps track of deleted tools in the `deleted_tools.json` file. This prevents the system from recreating tools that were intentionally deleted by the user.

## Security Considerations

The dynamic tool creation system has security implications:

1. Generated code is executed in the application's environment
2. External API calls may expose sensitive information
3. Resource usage may be unpredictable

In a production environment, additional safeguards should be implemented:

1. Code sandboxing
2. Rate limiting
3. API key management
4. Resource usage monitoring