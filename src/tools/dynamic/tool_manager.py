"""
Dynamic Tool Manager for creating and managing tools on-the-fly.

This module enables the system to create new tools when existing ones don't meet a specific need.
"""
import importlib
import inspect
import json
import logging
import os
import re
import sys
import time
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from src.api.ai_service import AIService
from src.utils.config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P,
    ENABLE_DYNAMIC_TOOLS,
    SANDBOX_DYNAMIC_TOOLS
)
from src.tools.base import MCPTool, DynamicTool

# Create a logger for this module
logger = logging.getLogger(__name__)

# Directory to store dynamically created tools
DYNAMIC_TOOLS_DIR = Path(__file__).parent
DELETED_TOOLS_FILE = DYNAMIC_TOOLS_DIR / "deleted_tools.json"

# Create the deleted_tools.json file if it doesn't exist
if not DELETED_TOOLS_FILE.exists():
    with open(DELETED_TOOLS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

class DynamicToolManager:
    """
    Manager for dynamically creating and registering tools based on user needs.
    """
    
    @staticmethod
    def detect_tool_need(user_message: str) -> Optional[Dict[str, Any]]:
        """
        Detect if a user message requires a new tool to be created.
        
        Args:
            user_message: The user's message
            
        Returns:
            Dictionary with tool information if a new tool is needed, None otherwise
        """
        if not ENABLE_DYNAMIC_TOOLS:
            logger.info("Dynamic tool creation is disabled")
            return None
        
        logger.info(f"Detecting tool need for message: {user_message[:50]}...")
        
        # Get existing tools to check if we already have a tool for this need
        from src.core.mcp_server import get_default_server
        existing_tools = get_default_server().get_tools_info()
        existing_tool_names = [tool["name"] for tool in existing_tools]
        
        # Create a prompt to ask the LLM if a new tool is needed
        prompt = f"""
        You are an AI assistant that can determine if a user's request requires a new tool to be created.
        
        User message: "{user_message}"
        
        Existing tools:
        {json.dumps(existing_tools, indent=2)}
        
        Analyze the user's message and determine if it requires a tool that doesn't exist yet.
        If a new tool is needed, provide the following information in JSON format:
        {{
            "new_tool_needed": true,
            "tool_name": "name_of_tool",
            "tool_description": "description of what the tool does",
            "tool_parameters": [
                {{"name": "param1", "type": "string", "description": "description of param1", "required": true}},
                {{"name": "param2", "type": "number", "description": "description of param2", "required": false}}
            ],
            "implementation_details": "Specific instructions on how to implement this tool, including any public APIs (e.g., 'https://api.ipify.org?format=json' for IP, 'http://ip-api.com/json/YOUR_IP_ADDRESS' for IP-based geolocation, 'https://open.er-api.com/v6/latest/USD' for currency) or libraries to use. The implementation MUST be fully functional and not use placeholder data or logic."
        }}
        
        If no new tool is needed, respond with:
        {{
            "new_tool_needed": false,
            "reason": "explanation of why no new tool is needed"
        }}
        
        Only respond with the JSON object, nothing else.
        """
        
        try:
            response = AIService.generate_structured_response(
                prompt=prompt,
                response_format={
                    "new_tool_needed": "boolean",
                    "tool_name": "string (if new_tool_needed is true)",
                    "tool_description": "string (if new_tool_needed is true)",
                    "tool_parameters": "array (if new_tool_needed is true)",
                    "implementation_details": "string (if new_tool_needed is true)",
                    "reason": "string (if new_tool_needed is false)"
                },
                model_name=DEFAULT_MODEL,
                temperature=0.2,  # Lower temperature for more deterministic results
                max_tokens=DEFAULT_MAX_TOKENS,
                top_p=DEFAULT_TOP_P
            )
            
            # If a new tool is needed and it doesn't already exist
            if response.get("new_tool_needed", False) and response.get("tool_name") not in existing_tool_names:
                logger.info(f"New tool needed: {response.get('tool_name')}")
                return response
            
            logger.debug("No new tool needed")
            return None
        except Exception as e:
            logger.error(f"Error detecting tool need: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def generate_tool_code(tool_info: Dict[str, Any]) -> str:
        """
        Generate Python code for a new tool based on the tool information.
        
        Args:
            tool_info: Dictionary with tool information
            
        Returns:
            String containing the Python code for the new tool
        """
        logger.info(f"Generating code for tool: {tool_info.get('tool_name')}")
        
        tool_name = tool_info["tool_name"]
        tool_description = tool_info["tool_description"]
        tool_parameters = tool_info.get("tool_parameters", [])
        implementation_details = tool_info.get("implementation_details", "")
        
        # Create a class name based on the tool name
        # Convert to CamelCase and ensure it ends with "Tool"
        class_name = ''.join(word.capitalize() for word in tool_name.split('_'))
        if not class_name.endswith('Tool'):
            class_name += 'Tool'
        
        # Create a prompt to generate the tool code
        prompt = f"""
        You are an expert Python developer. Create a Python class that implements a new tool for an MCP server.
        
        Tool Information:
        - Name: {tool_name}
        - Description: {tool_description}
        - Parameters: {json.dumps(tool_parameters, indent=2)}
        - Implementation Details: {implementation_details}
        
        IMPORTANT: You MUST create a class named "{class_name}" that is a subclass of DynamicTool with EXACTLY the following structure:
        
        ```python
        from src.tools.base import DynamicTool
        import requests  # Only use standard library or these packages: requests, json, datetime, re
        from typing import Dict, Any, Optional, List # Ensure typing is available
        import datetime
        
        class {class_name}(DynamicTool):
            def __init__(self):
                super().__init__(
                    name="{tool_name}", # Use the provided tool_name
                    description="{tool_description}", # Use the provided tool_description
                    created_at=datetime.datetime.now().isoformat()
                )
            
            def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
                # Parameter validation based on tool_parameters
                # Tool implementation using details from implementation_details
                # The implementation MUST be fully functional and return REAL data, not placeholders.
                # Return results as a dictionary.
                pass # Replace with actual implementation
        ```
        
        CRITICAL INSTRUCTIONS:
        1. The class MUST be named EXACTLY "{class_name}" and MUST inherit from DynamicTool.
        2. The generated code MUST be fully functional and provide REAL results. Placeholder logic or data is STRICTLY FORBIDDEN.
        3. ONLY use the Python standard library or these packages: requests, json, datetime, re, typing.
        4. DO NOT use any other external libraries (like googletrans, forex_python, etc.).
        5. If an API key is typically required but not provided in `implementation_details`, try to use a public version of the API or an alternative free API that doesn't require a key.
        6. For currency conversion, if no specific API is given, use `https://open.er-api.com/v6/latest/USD`.
        7. For weather data, if no specific API is given, use `https://api.open-meteo.com/v1/forecast`.
        8. For IP-based geolocation, if no specific API is given, you can use `http://ip-api.com/json/` (for the server's IP) or guide the user if client IP is needed.
        9. Include proper error handling for API calls (e.g., network errors, invalid responses) and parameter validation.
        10. Ensure the `execute` method returns a dictionary.
        
        Only provide the Python code, nothing else. Do not include markdown formatting or explanations.
        """
        
        try:
            code = AIService.generate_response(
                prompt=prompt,
                model_name=DEFAULT_MODEL,
                temperature=0.2,  # Lower temperature for more deterministic results
                max_tokens=DEFAULT_MAX_TOKENS * 2,  # Allow more tokens for code generation
                top_p=DEFAULT_TOP_P
            )
            
            # Clean up the code (remove markdown code blocks if present)
            code = re.sub(r'```python\s*', '', code)
            code = re.sub(r'```\s*', '', code)
            
            # Ensure the code has the correct class definition
            # If the AI didn't follow instructions, force the correct class structure
            if f"class {class_name}(DynamicTool)" not in code:
                logger.warning(f"AI did not generate the correct class structure for {class_name}. Applying template...")
                # Create a template with the correct structure
                template = f"""from src.tools.base import DynamicTool
import requests
import json
import datetime
from typing import Dict, Any, Optional, List

class {class_name}(DynamicTool):
    def __init__(self):
        super().__init__(
            name="{tool_name}",
            description="{tool_description}",
            created_at=datetime.datetime.now().isoformat()
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        # Extract parameters
        # TODO: This is a template implementation. Replace with actual implementation.
        try:
            # Basic implementation based on tool type
            if "currency" in "{tool_name}".lower() or "exchange" in "{tool_name}".lower():
                from_currency = args.get("from_currency", "USD").upper()
                to_currency = args.get("to_currency", "EUR").upper()
                amount = float(args.get("amount", 1))
                
                # Validate parameters
                if not from_currency:
                    return {{"error": "from_currency parameter is required"}}
                if not to_currency:
                    return {{"error": "to_currency parameter is required"}}
                
                # Use Exchange Rates API
                response = requests.get(f"https://open.er-api.com/v6/latest/{{from_currency}}")
                if response.status_code != 200:
                    return {{"error": f"API request failed with status code {{response.status_code}}"}}
                
                data = response.json()
                if data.get("result") != "success":
                    return {{"error": "Failed to fetch exchange rates"}}
                
                rates = data.get("rates", {{}})
                if to_currency not in rates:
                    return {{"error": f"Exchange rate not available for {{to_currency}}"}}
                
                rate = rates[to_currency]
                converted_amount = amount * rate
                
                return {{
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "amount": amount,
                    "rate": rate,
                    "converted_amount": converted_amount,
                    "last_updated": data.get("time_last_update_utc", "")
                }}
                
            elif "weather" in "{tool_name}".lower() or "forecast" in "{tool_name}".lower():
                location = args.get("location", "")
                days = int(args.get("days", 3))
                
                if not location:
                    return {{"error": "location parameter is required"}}
                
                # Use Open-Meteo API
                response = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={{
                        "latitude": 41.0082,  # Default to Istanbul if geocoding not implemented
                        "longitude": 28.9784,
                        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "weathercode"],
                        "timezone": "auto",
                        "forecast_days": days
                    }}
                )
                
                if response.status_code != 200:
                    return {{"error": f"API request failed with status code {{response.status_code}}"}}
                
                data = response.json()
                
                # Process the forecast data
                forecast = []
                daily = data.get("daily", {{}})
                
                if not daily:
                    return {{"error": "Failed to get forecast data"}}
                
                dates = daily.get("time", [])
                max_temps = daily.get("temperature_2m_max", [])
                min_temps = daily.get("temperature_2m_min", [])
                precip = daily.get("precipitation_sum", [])
                weather_codes = daily.get("weathercode", [])
                
                # Map weather codes to descriptions
                weather_descriptions = {{
                    0: "Clear sky",
                    1: "Mainly clear",
                    2: "Partly cloudy",
                    3: "Overcast",
                    45: "Fog",
                    48: "Depositing rime fog",
                    51: "Light drizzle",
                    53: "Moderate drizzle",
                    55: "Dense drizzle",
                    56: "Light freezing drizzle",
                    57: "Dense freezing drizzle",
                    61: "Slight rain",
                    63: "Moderate rain",
                    65: "Heavy rain",
                    66: "Light freezing rain",
                    67: "Heavy freezing rain",
                    71: "Slight snow fall",
                    73: "Moderate snow fall",
                    75: "Heavy snow fall",
                    77: "Snow grains",
                    80: "Slight rain showers",
                    81: "Moderate rain showers",
                    82: "Violent rain showers",
                    85: "Slight snow showers",
                    86: "Heavy snow showers",
                    95: "Thunderstorm",
                    96: "Thunderstorm with slight hail",
                    99: "Thunderstorm with heavy hail"
                }}
                
                for i in range(len(dates)):
                    if i < len(max_temps) and i < len(min_temps) and i < len(precip) and i < len(weather_codes):
                        weather_desc = weather_descriptions.get(weather_codes[i], "Unknown")
                        forecast.append({{
                            "date": dates[i],
                            "max_temp": max_temps[i],
                            "min_temp": min_temps[i],
                            "precipitation": precip[i],
                            "weather": weather_desc
                        }})
                
                return {{
                    "location": location,
                    "forecast": forecast,
                    "units": {{
                        "temperature": "°C",
                        "precipitation": "mm"
                    }}
                }}
                
            else:
                # Generic implementation for other tool types
                return {{"error": "This is a template implementation. Please replace with actual implementation."}}
                
        except requests.RequestException as e:
            return {{"error": f"API request failed: {{str(e)}}"}}
        except (ValueError, KeyError) as e:
            return {{"error": f"Error processing data: {{str(e)}}"}}
        except Exception as e:
            return {{"error": f"Unexpected error: {{str(e)}}"}}
"""
                # Use the template instead of the AI-generated code
                code = template
            
            logger.debug(f"Generated code for tool: {tool_name}")
            return code.strip()
        except Exception as e:
            logger.error(f"Error generating tool code: {str(e)}", exc_info=True)
            return ""
    
    @staticmethod
    def save_and_load_tool(tool_code: str, tool_name: str) -> Optional[DynamicTool]:
        """
        Save the generated tool code to a file and load the tool class.
        
        Args:
            tool_code: The Python code for the tool
            tool_name: The name of the tool
            
        Returns:
            An instance of the tool if successful, None otherwise
        """
        logger.info(f"Saving and loading tool: {tool_name}")
        
        # Convert tool_name to snake_case for the filename
        filename = ''.join(['_' + c.lower() if c.isupper() else c for c in tool_name]).lstrip('_')
        if not filename.endswith('_tool'):
            filename += '_tool'
        
        file_path = DYNAMIC_TOOLS_DIR / f"{filename}.py"
        
        try:
            # Create a class name based on the tool name
            # Convert to CamelCase and ensure it ends with "Tool"
            class_name = ''.join(word.capitalize() for word in tool_name.split('_'))
            if not class_name.endswith('Tool'):
                class_name += 'Tool'
            
            # Check if the code contains the expected class definition
            if f"class {class_name}(DynamicTool)" not in tool_code:
                logger.warning(f"Expected class '{class_name}' not found in generated code. Attempting to fix...")
                # Create a fixed version of the code with the correct class
                template = f"""from src.tools.base import DynamicTool
import requests
import json
import datetime
from typing import Dict, Any, Optional, List

class {class_name}(DynamicTool):
    def __init__(self):
        super().__init__(
            name="{tool_name}",
            description="Tool for {tool_name}",
            created_at=datetime.datetime.now().isoformat()
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Basic implementation
            return {{"message": "This is a template implementation for {tool_name}."}}
        except Exception as e:
            return {{"error": f"Error: {{str(e)}}"}}
"""
                tool_code = template
            
            # Save the code to a file
            with open(file_path, 'w') as f:
                f.write(tool_code)
            
            logger.debug(f"Saved tool code to: {file_path}")
            
            # Determine the module name
            module_name = f"src.tools.dynamic.{filename}"
            
            # Force reload if the module was already imported
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Import the module
            module = importlib.import_module(module_name)
            
            # Find the tool class in the module
            tool_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, DynamicTool) and obj != DynamicTool:
                    tool_class = obj
                    break
            
            if tool_class:
                # Create an instance of the tool
                tool = tool_class()
                logger.info(f"Successfully loaded tool: {tool.name}")
                return tool
            else:
                logger.error(f"No DynamicTool subclass found in the generated code for {tool_name}")
                
                # Create a fallback implementation directly
                fallback_code = f"""from src.tools.base import DynamicTool
import requests
import json
import datetime
from typing import Dict, Any, Optional, List

class {class_name}(DynamicTool):
    def __init__(self):
        super().__init__(
            name="{tool_name}",
            description="Tool for {tool_name}",
            created_at=datetime.datetime.now().isoformat()
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Fallback implementation
            return {{"message": "This is a fallback implementation for {tool_name}.", "args": args}}
        except Exception as e:
            return {{"error": f"Error: {{str(e)}}"}}
"""
                # Save the fallback code
                with open(file_path, 'w') as f:
                    f.write(fallback_code)
                
                logger.debug(f"Saved fallback code to: {file_path}")
                
                # Reload the module
                if module_name in sys.modules:
                    del sys.modules[module_name]
                
                module = importlib.import_module(module_name)
                
                # Find the tool class again
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, DynamicTool) and obj != DynamicTool:
                        tool_class = obj
                        break
                
                if tool_class:
                    tool = tool_class()
                    logger.info(f"Successfully loaded fallback tool: {tool.name}")
                    return tool
                else:
                    logger.critical(f"Critical error: Fallback implementation failed for {tool_name}")
                    return None
        except ImportError as e:
            # Handle missing dependencies
            missing_module = str(e).split("'")[1] if "'" in str(e) else str(e)
            logger.error(f"Error: Missing dependency '{missing_module}'. Regenerating tool without this dependency...")
            
            # Try again with updated constraints
            return None
        except Exception as e:
            logger.error(f"Error saving and loading tool: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def create_and_register_tool(user_message: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Create a new tool based on the user's message and register it with the MCP server.
        
        Args:
            user_message: The user's message
            
        Returns:
            Tuple of (success, tool_name, tool_info)
        """
        if not ENABLE_DYNAMIC_TOOLS:
            logger.info("Dynamic tool creation is disabled")
            return False, None, None
        
        logger.info(f"Creating and registering tool for message: {user_message[:50]}...")
        
        # First check if we already have a tool that can handle this request
        # This is a more direct approach than relying solely on the AI to detect tool needs
        from src.core.mcp_server import get_default_server
        mcp_server = get_default_server()
        existing_tools = mcp_server.get_tools_info()
        
        # Check for deleted tools to avoid recreating them
        deleted_tools = []
        if DELETED_TOOLS_FILE.exists():
            try:
                with open(DELETED_TOOLS_FILE, "r", encoding="utf-8") as f:
                    deleted_tools = json.load(f)
                logger.debug(f"Found deleted tools list: {deleted_tools}")
            except json.JSONDecodeError:
                logger.error("Error reading deleted_tools.json, treating as empty")
                deleted_tools = []
        
        # Check for currency conversion requests
        if any(term in user_message.lower() for term in ["dolar", "euro", "tl", "lira", "kur", "döviz", "currency", "exchange"]):
            # Check if this tool was deleted
            if "currency_converter" in deleted_tools:
                logger.info("Currency converter tool was previously deleted. Creating a new version.")
                # Force dynamic creation of a new tool with a different name
                tool_info_override = {
                    "new_tool_needed": True,
                    "tool_name": f"currency_converter_{int(time.time())}",  # Add timestamp to make unique
                    "tool_description": "Converts between different currencies using current exchange rates.",
                    "tool_parameters": [
                        {"name": "from_currency", "type": "string", "description": "Source currency code (e.g., USD, EUR)", "required": True},
                        {"name": "to_currency", "type": "string", "description": "Target currency code (e.g., TRY, EUR)", "required": True},
                        {"name": "amount", "type": "number", "description": "Amount to convert", "required": True}
                    ],
                    "implementation_details": "Use the Exchange Rates API (https://open.er-api.com/v6/latest/USD) to get current exchange rates."
                }
                tool_code = DynamicToolManager.generate_tool_code(tool_info_override)
                if not tool_code: return False, None, None
                tool = DynamicToolManager.save_and_load_tool(tool_code, tool_info_override["tool_name"])
                if not tool: return False, None, None
                mcp_server.register_tool(tool)
                logger.info(f"Successfully created and registered new currency tool: {tool.name}")
                return True, tool.name, tool_info_override
            elif not any(tool["name"] == "currency_converter" for tool in existing_tools):
                logger.info("Currency converter tool not found. Creating a new one.")
                # Create a new currency converter tool
                tool_info_override = {
                    "new_tool_needed": True,
                    "tool_name": "currency_converter",
                    "tool_description": "Converts between different currencies using current exchange rates.",
                    "tool_parameters": [
                        {"name": "from_currency", "type": "string", "description": "Source currency code (e.g., USD, EUR)", "required": True},
                        {"name": "to_currency", "type": "string", "description": "Target currency code (e.g., TRY, EUR)", "required": True},
                        {"name": "amount", "type": "number", "description": "Amount to convert", "required": True}
                    ],
                    "implementation_details": "Use the Exchange Rates API (https://open.er-api.com/v6/latest/USD) to get current exchange rates."
                }
                tool_code = DynamicToolManager.generate_tool_code(tool_info_override)
                if not tool_code: return False, None, None
                tool = DynamicToolManager.save_and_load_tool(tool_code, tool_info_override["tool_name"])
                if not tool: return False, None, None
                mcp_server.register_tool(tool)
                logger.info(f"Successfully created and registered currency converter tool: {tool.name}")
                return True, tool.name, tool_info_override
            else:
                logger.info("Using existing currency_converter tool.")
                return True, "currency_converter", {"tool_name": "currency_converter", "description": "Converts currencies", "predefined": True}
        
        # Check for weather forecast requests
        elif any(term in user_message.lower() for term in ["hava", "weather", "forecast", "sıcaklık", "temperature"]):
            # Check if this tool was deleted
            if "weather_forecast" in deleted_tools:
                logger.info("Weather forecast tool was previously deleted. Creating a new version.")
                # Force dynamic creation of a new tool with a different name
                tool_info_override = {
                    "new_tool_needed": True,
                    "tool_name": f"weather_forecast_{int(time.time())}",  # Add timestamp to make unique
                    "tool_description": "Gets weather forecast for a specified location.",
                    "tool_parameters": [
                        {"name": "location", "type": "string", "description": "Location for the weather forecast", "required": True},
                        {"name": "days", "type": "number", "description": "Number of days for the forecast", "required": False}
                    ],
                    "implementation_details": "Use the Open-Meteo API (https://api.open-meteo.com/v1/forecast) to get weather forecasts."
                }
                tool_code = DynamicToolManager.generate_tool_code(tool_info_override)
                if not tool_code: return False, None, None
                tool = DynamicToolManager.save_and_load_tool(tool_code, tool_info_override["tool_name"])
                if not tool: return False, None, None
                mcp_server.register_tool(tool)
                logger.info(f"Successfully created and registered new weather tool: {tool.name}")
                return True, tool.name, tool_info_override
            elif not any(tool["name"] == "weather_forecast" for tool in existing_tools):
                logger.info("Weather forecast tool not found. Creating a new one.")
                # Create a new weather forecast tool
                tool_info_override = {
                    "new_tool_needed": True,
                    "tool_name": "weather_forecast",
                    "tool_description": "Gets weather forecast for a specified location.",
                    "tool_parameters": [
                        {"name": "location", "type": "string", "description": "Location for the weather forecast", "required": True},
                        {"name": "days", "type": "number", "description": "Number of days for the forecast", "required": False}
                    ],
                    "implementation_details": "Use the Open-Meteo API (https://api.open-meteo.com/v1/forecast) to get weather forecasts."
                }
                tool_code = DynamicToolManager.generate_tool_code(tool_info_override)
                if not tool_code: return False, None, None
                tool = DynamicToolManager.save_and_load_tool(tool_code, tool_info_override["tool_name"])
                if not tool: return False, None, None
                mcp_server.register_tool(tool)
                logger.info(f"Successfully created and registered weather forecast tool: {tool.name}")
                return True, tool.name, tool_info_override
            else:
                logger.info("Using existing weather_forecast tool.")
                return True, "weather_forecast", {"tool_name": "weather_forecast", "description": "Gets weather forecasts", "predefined": True}
        
        # Check for location requests
        elif any(term in user_message.lower() for term in ["konum", "location", "neredeyim", "where am i"]):
             # Check if this tool was deleted
             if "get_current_location" in deleted_tools:
                logger.info("Location tool was previously deleted. Creating a new version.")
                # Force dynamic creation of a new tool with a different name
                tool_info_override = {
                    "new_tool_needed": True,
                    "tool_name": f"get_current_location_{int(time.time())}",  # Add timestamp to make unique
                    "tool_description": "Retrieves the user's approximate location based on their IP address.",
                    "tool_parameters": [],
                    "implementation_details": "Use a public IP geolocation API like 'http://ip-api.com/json/' to get city, region, country."
                }
                tool_code = DynamicToolManager.generate_tool_code(tool_info_override)
                if not tool_code: return False, None, None
                tool = DynamicToolManager.save_and_load_tool(tool_code, tool_info_override["tool_name"])
                if not tool: return False, None, None
                mcp_server.register_tool(tool)
                logger.info(f"Successfully created and registered new location tool: {tool.name}")
                return True, tool.name, tool_info_override
             elif not any(tool["name"] == "get_current_location" for tool in existing_tools):
                logger.info("Location tool not found. Creating a new one.")
                # Create a new location tool
                tool_info_override = {
                    "new_tool_needed": True,
                    "tool_name": "get_current_location",
                    "tool_description": "Retrieves the user's approximate location based on their IP address.",
                    "tool_parameters": [],
                    "implementation_details": "Use a public IP geolocation API like 'http://ip-api.com/json/' to get city, region, country."
                }
                tool_code = DynamicToolManager.generate_tool_code(tool_info_override)
                if not tool_code: return False, None, None
                tool = DynamicToolManager.save_and_load_tool(tool_code, tool_info_override["tool_name"])
                if not tool: return False, None, None
                mcp_server.register_tool(tool)
                logger.info(f"Successfully created and registered location tool: {tool.name}")
                return True, tool.name, tool_info_override
             else:
                logger.info("Using existing get_current_location tool.")
                return True, "get_current_location", {"tool_name": "get_current_location", "description": "Gets location", "predefined": True}
        
        # If no specific keyword match, then detect if a new tool is needed using AI
        tool_info = DynamicToolManager.detect_tool_need(user_message)
        
        if not tool_info or not tool_info.get("new_tool_needed"):
             logger.debug("No new tool needed")
             return False, None, None
             
        # Check if the tool was previously deleted
        tool_name = tool_info.get("tool_name", "")
        if tool_name in deleted_tools:
            logger.info(f"Tool '{tool_name}' was previously deleted. Creating a new version with a unique name.")
            tool_info["tool_name"] = f"{tool_name}_{int(time.time())}"  # Add timestamp to make unique
        
        # Generate code for the new tool
        tool_code = DynamicToolManager.generate_tool_code(tool_info)
        
        if not tool_code:
            logger.error(f"Failed to generate code for tool: {tool_name}")
            return False, None, None
        
        # Save and load the tool
        tool = DynamicToolManager.save_and_load_tool(tool_code, tool_info["tool_name"])
        
        if not tool:
            logger.error(f"Failed to save and load tool: {tool_info['tool_name']}")
            return False, None, None
        
        # Register the tool with the MCP server
        mcp_server.register_tool(tool)
        
        logger.info(f"Successfully created and registered new tool: {tool.name}")
        
        return True, tool.name, tool_info
    
    @staticmethod
    def delete_tool(tool_name: str) -> bool:
        """
        Delete a dynamic tool.
        
        Args:
            tool_name: The name of the tool to delete
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting tool: {tool_name}")
        
        try:
            # Get the MCP server
            from src.core.mcp_server import get_default_server
            mcp_server = get_default_server()
            
            # Unregister the tool from the server
            success = mcp_server.unregister_tool(tool_name)
            
            if success:
                # Convert tool name to filename
                tool_filename = ''.join(['_' + c.lower() if c.isupper() else c for c in tool_name]).lstrip('_')
                if not tool_filename.endswith('_tool'):
                    tool_filename += '_tool'
                
                tool_path = DYNAMIC_TOOLS_DIR / f"{tool_filename}.py"
                module_name = f"src.tools.dynamic.{tool_filename}"
                
                # Remove from sys.modules if loaded
                if module_name in sys.modules:
                    del sys.modules[module_name]
                    logger.debug(f"Removed module from sys.modules: {module_name}")
                
                # Add to deleted tools list
                deleted_tools = []
                if DELETED_TOOLS_FILE.exists():
                    try:
                        with open(DELETED_TOOLS_FILE, "r", encoding="utf-8") as f:
                            deleted_tools = json.load(f)
                    except json.JSONDecodeError:
                        deleted_tools = []
                
                if tool_name not in deleted_tools:
                    deleted_tools.append(tool_name)
                    
                with open(DELETED_TOOLS_FILE, "w", encoding="utf-8") as f:
                    json.dump(deleted_tools, f, ensure_ascii=False, indent=4)
                
                # Delete the file if it exists
                if tool_path.exists():
                    tool_path.unlink()  # Delete the file
                    logger.debug(f"Deleted tool file: {tool_path}")
                
                logger.info(f"Successfully deleted tool: {tool_name}")
                return True
            
            logger.warning(f"Failed to unregister tool: {tool_name}")
            return False
        except Exception as e:
            logger.error(f"Error deleting tool: {str(e)}", exc_info=True)
            return False