"""
Dynamic Tool Manager for creating and managing tools on-the-fly.
This module enables the system to create new tools when existing ones don't meet a specific need.
"""
import importlib
import inspect
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from utils.ai_service import AIService
from utils.config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P,
    BASE_DIR
)
from app.services.mcp_server import MCPTool, MCPServer, get_default_server

# Directory to store dynamically created tools
DYNAMIC_TOOLS_DIR = BASE_DIR / "dynamic_tools"
DYNAMIC_TOOLS_DIR.mkdir(exist_ok=True)

# Create an __init__.py file if it doesn't exist
init_file = DYNAMIC_TOOLS_DIR / "__init__.py"
if not init_file.exists():
    init_file.touch()

class DynamicToolManager:
    """
    Manager for dynamically creating and registering tools based on user needs.
    """
    
    @staticmethod
    def generate_direct_response(user_message: str) -> str:
        """
        Generate a direct response from the LLM when tool creation fails.
        
        Args:
            user_message: The user's message
            
        Returns:
            A direct response from the LLM
        """
        prompt = f"""
        You are an AI assistant that provides helpful responses to user queries.
        The user request cannot be fulfilled by creating a specialized tool or using existing tools.
        Instead, provide a direct and informative response to the best of your knowledge.
        
        User query: "{user_message}"
        
        Provide a helpful, informative response that answers the user's question directly.
        If you don't have specific information to answer the query, acknowledge the limitations
        and provide general information that might still be useful to the user.
        """
        
        try:
            response = AIService.generate_response(
                prompt=prompt,
                model_name=DEFAULT_MODEL,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_MAX_TOKENS,
                top_p=DEFAULT_TOP_P
            )
            return response.strip()
        except Exception as e:
            print(f"Error generating direct response: {str(e)}")
            return "I apologize, but I'm unable to provide a response to your request at this time."
    
    @staticmethod
    def detect_tool_need(user_message: str) -> Optional[Dict[str, Any]]:
        """
        Detect if a user message requires a new tool to be created.
        
        Args:
            user_message: The user's message
            
        Returns:
            Dictionary with tool information if a new tool is needed, None otherwise
        """
        # Get existing tools to check if we already have a tool for this need
        existing_tools = get_default_server().get_tools_info()
        existing_tool_names = [tool["name"] for tool in existing_tools]
        
        # Create a prompt to ask the LLM if a new tool is needed
        prompt = f"""
        You are an AI assistant that analyzes if a user's request ABSOLUTELY requires a new tool. 
        Be EXTREMELY conservative - only suggest a new tool if:
        1. The request requires external data or API access
        2. None of the existing tools can perform this function
        3. This is a commonly requested functionality that will be reused
        4. The functionality cannot be handled with simple conversation

        User message: "{user_message}"

        Existing tools:
        {json.dumps(existing_tools, indent=2)}

        First, carefully analyze if ANY existing tool can fulfill this need, even partially. 
        If an existing tool can be used, ALWAYS respond with:
        {{
            "new_tool_needed": false,
            "reason": "Can be handled by existing tool: [tool name]"
        }}

        Only if absolutely necessary, suggest a new tool.
        """
        
        try:
            response = AIService.generate_response(
                prompt=prompt,
                model_name=DEFAULT_MODEL,
                temperature=0.2,  # Lower temperature for more deterministic results
                max_tokens=DEFAULT_MAX_TOKENS,
                top_p=DEFAULT_TOP_P
            )
            
            # Extract JSON from response
            json_match = re.search(r'({.*})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
                
                # If a new tool is needed and it doesn't already exist
                if result.get("new_tool_needed", False) and result.get("tool_name") not in existing_tool_names:
                    return result
                
            return None
        except Exception as e:
            print(f"Error detecting tool need: {str(e)}")
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
        
        IMPORTANT: You MUST create a class named "{class_name}" that is a subclass of MCPTool with EXACTLY the following structure:
        
        ```python
        from app.services.mcp_server import MCPTool
        import requests  # Only use standard library or these packages: requests, json, datetime, re
        from typing import Dict, Any, Optional, List # Ensure typing is available
        
        class {class_name}(MCPTool):
            def __init__(self):
                super().__init__(
                    name="{tool_name}", # Use the provided tool_name
                    description="{tool_description}" # Use the provided tool_description
                )
            
            def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
                # Parameter validation based on tool_parameters
                # Tool implementation using details from implementation_details
                # The implementation MUST be fully functional and return REAL data, not placeholders.
                # Return results as a dictionary.
                pass # Replace with actual implementation
        ```
        
        CRITICAL INSTRUCTIONS:
        1. The class MUST be named EXACTLY "{class_name}" and MUST inherit from MCPTool.
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
            if f"class {class_name}(MCPTool)" not in code:
                print(f"AI did not generate the correct class structure. Applying template...")
                # Create a template with the correct structure
                template = f"""from app.services.mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List

class {class_name}(MCPTool):
    def __init__(self):
        super().__init__(
            name="{tool_name}",
            description="{tool_description}"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        # Extract parameters
        # TODO: This is a template implementation. Replace with actual implementation.
        try:
            # Basic implementation based on tool type
            if "currency" in tool_name.lower() or "exchange" in tool_name.lower():
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
                
            elif "weather" in tool_name.lower() or "forecast" in tool_name.lower():
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
            
            return code.strip()
        except Exception as e:
            print(f"Error generating tool code: {str(e)}")
            return ""
    
    @staticmethod
    def save_and_load_tool(tool_code: str, tool_name: str) -> Optional[MCPTool]:
        """
        Save the generated tool code to a file and load the tool class.
        
        Args:
            tool_code: The Python code for the tool
            tool_name: The name of the tool
            
        Returns:
            An instance of the tool if successful, None otherwise
        """
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
            if f"class {class_name}(MCPTool)" not in tool_code:
                print(f"Warning: Expected class '{class_name}' not found in generated code. Attempting to fix...")
                # Create a fixed version of the code with the correct class
                template = f"""from app.services.mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List

class {class_name}(MCPTool):
    def __init__(self):
        super().__init__(
            name="{tool_name}",
            description="Tool for {tool_name}"
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
            
            # Determine the module name
            module_name = f"dynamic_tools.{filename}"
            
            # Force reload if the module was already imported
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Import the module
            module = importlib.import_module(module_name)
            
            # Find the tool class in the module
            tool_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, MCPTool) and obj != MCPTool:
                    tool_class = obj
                    break
            
            if tool_class:
                # Create an instance of the tool
                return tool_class()
            else:
                print(f"No MCPTool subclass found in the generated code. Using fallback implementation.")
                
                # Create a fallback implementation directly
                fallback_code = f"""from app.services.mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List

class {class_name}(MCPTool):
    def __init__(self):
        super().__init__(
            name="{tool_name}",
            description="Tool for {tool_name}"
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
                
                # Reload the module
                if module_name in sys.modules:
                    del sys.modules[module_name]
                
                module = importlib.import_module(module_name)
                
                # Find the tool class again
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, MCPTool) and obj != MCPTool:
                        tool_class = obj
                        break
                
                if tool_class:
                    return tool_class()
                else:
                    print(f"Critical error: Fallback implementation failed.")
                    return None
        except ImportError as e:
            # Handle missing dependencies
            missing_module = str(e).split("'")[1] if "'" in str(e) else str(e)
            print(f"Error: Missing dependency '{missing_module}'. Regenerating tool without this dependency...")
            
            # Regenerate the tool code without the problematic dependency
            updated_tool_info = tool_info.copy()
            updated_tool_info["implementation_details"] = (
                f"{tool_info.get('implementation_details', '')} "
                f"DO NOT use {missing_module} library. Only use standard library and requests."
            )
            
            # Try again with updated constraints
            new_tool_code = DynamicToolManager.generate_tool_code(updated_tool_info)
            if new_tool_code:
                return DynamicToolManager.save_and_load_tool(new_tool_code, tool_name)
            return None
        except Exception as e:
            print(f"Error saving and loading tool: {str(e)}")
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
        mcp_server = get_default_server()
        existing_tools = mcp_server.get_tools_info()
        
        # Check for deleted tools to avoid recreating them
        deleted_tools = []
        deleted_tools_path = Path(DYNAMIC_TOOLS_DIR / "deleted_tools.json")
        if deleted_tools_path.exists():
            try:
                with open(deleted_tools_path, "r", encoding="utf-8") as f:
                    deleted_tools = json.load(f)
                print(f"Found deleted tools list: {deleted_tools}")
            except json.JSONDecodeError:
                print("Error reading deleted_tools.json, treating as empty")
                deleted_tools = []
        
        # Detect if a new tool is needed using AI
        tool_info = DynamicToolManager.detect_tool_need(user_message)
        
        if not tool_info or not tool_info.get("new_tool_needed"):
             return False, None, None
             
        # Check if the tool was previously deleted
        tool_name = tool_info.get("tool_name", "")
        if tool_name in deleted_tools:
            print(f"Tool '{tool_name}' was previously deleted. Creating a new version with a unique name.")
            tool_info["tool_name"] = f"{tool_name}_{int(time.time())}"  # Add timestamp to make unique

        # Generate code for the new tool
        tool_code = DynamicToolManager.generate_tool_code(tool_info)
        
        if not tool_code:
            return False, None, None
        
        # Save and load the tool
        tool = DynamicToolManager.save_and_load_tool(tool_code, tool_info["tool_name"])
        
        # If tool creation failed, generate a direct LLM response instead
        if not tool:
            print(f"Tool creation failed. Generating direct LLM response for user query: {user_message}")
            direct_response = DynamicToolManager.generate_direct_response(user_message)
            
            # Return a special format that indicates this is a direct response
            return False, None, {"direct_response": direct_response}
        
        # Register the tool with the MCP server
        mcp_server.register_tool(tool)
        
        print(f"Successfully created and registered new tool: {tool.name}")
        
        return True, tool.name, tool_info
