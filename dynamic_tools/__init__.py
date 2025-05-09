"""
Dynamic Tools Package

This package contains dynamically created tools that are generated on-the-fly
based on user needs. These tools are automatically registered with the MCP server
and can be used by agentic characters.
"""

# Import example tools
try:
    from .currency_converter_tool import CurrencyConverterTool
except ImportError:
    pass

try:
    from .weather_forecast_tool import WeatherForecastTool
except ImportError:
    pass

# The rest of the tools will be dynamically imported at runtime