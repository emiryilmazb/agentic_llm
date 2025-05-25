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
from mcp_server import MCPTool, MCPServer, get_default_server

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
        
        # Create a question for the thinking model to analyze if a new tool is needed
        question = f"""
        Analiz et: Kullanıcının aşağıdaki mesajı yeni bir tool oluşturmayı gerektiriyor mu?
        
        Yeni bir tool SADECE şu durumlarda gereklidir:
        1. İstek, harici veri veya API erişimi gerektiriyorsa
        2. Mevcut araçların hiçbiri bu işlevi gerçekleştiremiyorsa
        3. Bu, sık istenen ve tekrar kullanılabilecek bir işlevse
        4. İşlev basit bir konuşmayla halledilemiyorsa

        Kullanıcı mesajı: "{user_message}"

        Mevcut araçlar:
        {json.dumps(existing_tools, indent=2)}

        Önce, mevcut herhangi bir aracın bu ihtiyacı karşılayıp karşılayamayacağını dikkatlice analiz et.
        Eğer mevcut bir araç kullanılabilirse, yanıtın şu formatta olmalı:
        {{
            "new_tool_needed": false,
            "reason": "Mevcut araç kullanılabilir: [araç adı]"
        }}

        Eğer kesinlikle yeni bir araç gerekiyorsa, yanıtın şu formatta olmalı:
        {{
            "new_tool_needed": true,
            "tool_name": "önerilen_araç_adı",
            "tool_description": "Aracın ne yaptığının açıklaması",
            "tool_parameters": [
                {{"name": "parametre1", "type": "string/number/boolean", "description": "Parametre açıklaması", "required": true/false}},
                ...
            ],
            "implementation_details": "Aracın nasıl uygulanacağına dair detaylar"
        }}
        """

        try:
            # Thinking modeli ile analiz yap
            thinking_result = AIService.generate_thinking_response(
                question=question,
                model_name=DEFAULT_MODEL,
                temperature=0.2,  # Lower temperature for more deterministic results
                max_tokens=DEFAULT_MAX_TOKENS * 2,
                top_p=DEFAULT_TOP_P
            )
            
            # Düşünce sürecini logla
            print(f"Tool ihtiyacı analiz düşünce süreci:\n{thinking_result['thinking']}")
            
            # Yanıtı al
            response = thinking_result['answer']
            
            # Extract JSON from response
            json_match = re.search(r'({.*})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    result = json.loads(json_str)
                    
                    # If a new tool is needed
                    if result.get("new_tool_needed", False):
                        tool_name = result.get("tool_name")
                        print(f"AI detected need for new tool: {tool_name}")
                                                
                        # Eğer tool zaten varsa, yine de oluştur ama farklı bir isimle
                        if tool_name in existing_tool_names:
                            print(f"Tool '{tool_name}' already exists, but will be recreated")
                            # Var olan tool'u kaldır
                            from mcp_server import get_default_server
                            server = get_default_server()
                            server.unregister_tool(tool_name)
                            
                        return result
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON from AI response: {str(e)}")
                    print(f"Response was: {response}")
                
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
        from mcp_server import MCPTool
        import requests  # Only use standard library or these packages: requests, json, datetime, re
        from typing import Dict, Any, Optional, List # Ensure typing is available
        
        class {class_name}(MCPTool):
            def __init__(self):
                super().__init__(
                    name="{tool_name}", # Use the provided tool_name
                    description="{tool_description}" # Use the provided tool_description
                )
                # Store parameters as a class attribute if needed
                self.parameters = {json.dumps(tool_parameters, indent=2)}
            
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
        11. CRITICAL: DO NOT pass 'parameters' as an argument to super().__init__(). The MCPTool.__init__() method only accepts 'name' and 'description' parameters. If you need to store parameters, do it as a separate class attribute after the super().__init__() call.
        
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
                template = f"""from mcp_server import MCPTool
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
                template = f"""from mcp_server import MCPTool
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
                fallback_code = f"""from mcp_server import MCPTool
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
            # Burada tool_info değişkeni tanımlı değil, bu nedenle hata oluşabilir
            # Geçici bir tool_info oluşturalım
            temp_tool_info = {
                "tool_name": tool_name,
                "tool_description": f"Tool for {tool_name}",
                "implementation_details": f"DO NOT use {missing_module} library. Only use standard library and requests."
            }
            
            # Try again with updated constraints
            new_tool_code = DynamicToolManager.generate_tool_code(temp_tool_info)
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
        # Get MCP server and existing tools
        mcp_server = get_default_server()
        existing_tools = mcp_server.get_tools_info()
        
        # Tool creation logic continues
        
        # Detect if a new tool is needed using AI
        print(f"Analyzing user message with AI to detect tool need: '{user_message}'")
        tool_info = DynamicToolManager.detect_tool_need(user_message)
        
        # AI'nın yanıtını kontrol et
        if not tool_info:
            print("AI did not detect a need for a new tool.")
            return False, None, None
        
        if not tool_info.get("new_tool_needed"):
            print(f"AI determined no new tool is needed: {tool_info.get('reason', 'No reason provided')}")
            return False, None, None
            
        print(f"AI determined a new tool is needed: {tool_info.get('tool_name')}")
        print(f"Tool description: {tool_info.get('tool_description')}")
             
        # Get tool name
        tool_name = tool_info.get("tool_name", "")

        # Generate code for the new tool
        print(f"Generating code for the new tool: {tool_info.get('tool_name')}")
        tool_code = DynamicToolManager.generate_tool_code(tool_info)
        
        if not tool_code:
            print("Failed to generate tool code.")
            return False, None, None
        
        # Save and load the tool
        print(f"Saving and loading the tool: {tool_info.get('tool_name')}")
        tool = DynamicToolManager.save_and_load_tool(tool_code, tool_info["tool_name"])
        
        if not tool:
            print("Failed to save and load the tool.")
            return False, None, None
        
        # Register the tool with the MCP server
        mcp_server.register_tool(tool)
        
        print(f"Successfully created and registered new tool: {tool.name}")
        
        return True, tool.name, tool_info
    
    @staticmethod
    def debug_and_fix_tool(tool_name: str, error_message: str, args: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Hata veren bir tool'u otomatik olarak debug edip düzeltmeye çalışır.
        
        Args:
            tool_name: Hata veren tool'un adı
            error_message: Hata mesajı
            args: Tool'a geçilen argümanlar
            
        Returns:
            Tuple of (success, tool_name, tool_info)
        """
        print(f"Tool otomatik debug başlatılıyor: {tool_name}")
        print(f"Hata mesajı: {error_message}")
        print(f"Argümanlar: {args}")
        
        try:
            # MCP sunucusundan tool'u al
            mcp_server = get_default_server()
            
            # Tool dosyasını bul
            tool_filename = ''.join(['_' + c.lower() if c.isupper() else c for c in tool_name]).lstrip('_')
            if not tool_filename.endswith('_tool'):
                tool_filename += '_tool'
            
            tool_path = DYNAMIC_TOOLS_DIR / f"{tool_filename}.py"
            
            # Tool dosyasının içeriğini oku
            if not tool_path.exists():
                print(f"Tool dosyası bulunamadı: {tool_path}")
                return False, None, None
            
            with open(tool_path, 'r') as f:
                tool_code = f.read()
            
            # Hata türünü analiz et ve uygun çözümü uygula
            fixed_code = None
            
            # 1. "unexpected keyword argument" hatası
            if "unexpected keyword argument" in error_message:
                param_match = re.search(r"unexpected keyword argument '(\w+)'", error_message)
                if param_match:
                    problematic_param = param_match.group(1)
                    print(f"Tespit edilen sorunlu parametre: '{problematic_param}'")
                    
                    # __init__ metodunu bul ve düzelt
                    init_pattern = r"def __init__\(self\):\s+super\(\)\.__init__\("
                    init_match = re.search(init_pattern, tool_code)
                    
                    if init_match:
                        # super().__init__() çağrısını bul
                        super_init_pattern = r"super\(\)\.__init__\(([\s\S]*?)\)"
                        super_init_match = re.search(super_init_pattern, tool_code)
                        
                        if super_init_match:
                            init_args = super_init_match.group(1)
                            
                            # Sorunlu parametreyi bul
                            param_pattern = rf"{problematic_param}=(?:\[[\s\S]*?\]|{{[\s\S]*?}}|\".*?\"|'.*?'|[^,)]+)"
                            param_match = re.search(param_pattern, init_args)
                            
                            if param_match:
                                param_value = param_match.group(0)
                                
                                # Sorunlu parametreyi çıkar
                                new_init_args = re.sub(rf",\s*{param_pattern}", "", init_args)
                                new_init_args = re.sub(rf"{param_pattern},\s*", "", new_init_args)
                                
                                # Yeni super().__init__() çağrısı
                                new_super_init = f"super().__init__({new_init_args})"
                                
                                # Parametreyi self.parameters olarak ekle
                                param_value_only = param_value.split("=", 1)[1]
                                param_assignment = f"        self.{problematic_param} = {param_value_only}"
                                
                                # Kodu güncelle
                                updated_code = tool_code.replace(super_init_match.group(0), new_super_init)
                                
                                # self.parameters atamasını ekle
                                init_end_pattern = r"super\(\)\.__init__\([\s\S]*?\)([\s\S]*?)def"
                                init_end_match = re.search(init_end_pattern, updated_code)
                                
                                if init_end_match:
                                    init_end = init_end_match.group(1)
                                    new_init_end = f"\n{param_assignment}{init_end}"
                                    updated_code = updated_code.replace(init_end, new_init_end)
                                
                                fixed_code = updated_code
                                print(f"'unexpected keyword argument' hatası düzeltildi")
            
            # 2. "missing required argument" hatası
            elif "missing required argument" in error_message or "required positional argument" in error_message:
                param_match = re.search(r"missing required (?:positional )?argument '(\w+)'", error_message)
                if param_match:
                    missing_param = param_match.group(1)
                    print(f"Tespit edilen eksik parametre: '{missing_param}'")
                    
                    # execute metodunu bul
                    execute_pattern = r"def execute\(self, args: Dict\[str, Any\]\)[\s\S]*?:"
                    execute_match = re.search(execute_pattern, tool_code)
                    
                    if execute_match:
                        # Parametreyi kontrol et ve varsayılan değer ekle
                        param_check_pattern = rf"{missing_param}\s*=\s*args\.get\(['\"]?{missing_param}['\"]?(?:,\s*[^)]+)?\)"
                        param_check_match = re.search(param_check_pattern, tool_code)
                        
                        if param_check_match:
                            # Zaten bir args.get kullanımı var, varsayılan değer ekle
                            old_param_check = param_check_match.group(0)
                            if "," not in old_param_check:
                                # Varsayılan değer yok, ekle
                                new_param_check = old_param_check.replace(")", ", None)")
                                fixed_code = tool_code.replace(old_param_check, new_param_check)
                                print(f"Eksik parametre için varsayılan değer eklendi: {missing_param}")
                        else:
                            # Parametre kontrolü yok, ekle
                            execute_body_start = execute_match.end()
                            param_assignment = f"\n        {missing_param} = args.get('{missing_param}', None)"
                            fixed_code = tool_code[:execute_body_start] + param_assignment + tool_code[execute_body_start:]
                            print(f"Eksik parametre için kontrol eklendi: {missing_param}")
            
            # 3. "module not found" hatası (ImportError)
            elif "No module named" in error_message:
                module_match = re.search(r"No module named '([^']+)'", error_message)
                if module_match:
                    missing_module = module_match.group(1)
                    print(f"Tespit edilen eksik modül: '{missing_module}'")
                    
                    # Import ifadesini bul
                    import_pattern = rf"import\s+{missing_module}|from\s+{missing_module}\s+import"
                    import_match = re.search(import_pattern, tool_code)
                    
                    if import_match:
                        # Problematik import ifadesini kaldır
                        import_line = tool_code.splitlines()[import_match.start():import_match.end()].pop(0)
                        fixed_code = tool_code.replace(import_line, f"# {import_line} # Removed due to missing module")
                        
                        # Alternatif çözüm ekle
                        if missing_module == "googletrans":
                            # googletrans yerine requests kullan
                            fixed_code = fixed_code.replace("# import requests", "import requests")
                            print(f"Eksik modül '{missing_module}' için alternatif çözüm eklendi")
                        elif missing_module == "forex_python":
                            # forex_python yerine requests kullan
                            fixed_code = fixed_code.replace("# import requests", "import requests")
                            print(f"Eksik modül '{missing_module}' için alternatif çözüm eklendi")
            
            # 4. "attribute error" hatası (AttributeError)
            elif "has no attribute" in error_message:
                attr_match = re.search(r"'[^']+' object has no attribute '([^']+)'", error_message)
                if attr_match:
                    missing_attr = attr_match.group(1)
                    print(f"Tespit edilen eksik özellik: '{missing_attr}'")
                    
                    # Özelliği kullanan kodu bul
                    attr_pattern = rf"\.{missing_attr}\b"
                    attr_matches = list(re.finditer(attr_pattern, tool_code))
                    
                    if attr_matches:
                        # İlk eşleşmeyi düzelt
                        match = attr_matches[0]
                        line_start = tool_code.rfind('\n', 0, match.start()) + 1
                        line_end = tool_code.find('\n', match.end())
                        if line_end == -1:
                            line_end = len(tool_code)
                        
                        problematic_line = tool_code[line_start:line_end]
                        fixed_line = f"# {problematic_line} # AttributeError\n        # Düzeltilmiş kod:"
                        
                        # Alternatif çözüm ekle
                        if missing_attr == "json":
                            fixed_line += "\n        import json\n        data = json.loads(response.text)"
                        elif missing_attr == "text":
                            fixed_line += "\n        data = response.content.decode('utf-8')"
                        else:
                            fixed_line += f"\n        # '{missing_attr}' özelliği bulunamadı, alternatif bir çözüm kullanın"
                        
                        fixed_code = tool_code.replace(problematic_line, fixed_line)
                        print(f"AttributeError için düzeltme eklendi: {missing_attr}")
            
            # 5. "type error" hatası (TypeError)
            elif "TypeError" in error_message:
                # Tip hatası için genel bir düzeltme
                type_match = re.search(r"TypeError: (.+)", error_message)
                if type_match:
                    type_error = type_match.group(1)
                    print(f"Tespit edilen tip hatası: '{type_error}'")
                    
                    if "not callable" in type_error:
                        # Çağrılabilir olmayan bir nesneyi çağırma hatası
                        callable_match = re.search(r"'([^']+)' object is not callable", type_error)
                        if callable_match:
                            obj_name = callable_match.group(1)
                            # Nesneyi çağıran kodu bul
                            call_pattern = rf"{obj_name}\s*\("
                            call_matches = list(re.finditer(call_pattern, tool_code))
                            
                            if call_matches:
                                # İlk eşleşmeyi düzelt
                                match = call_matches[0]
                                line_start = tool_code.rfind('\n', 0, match.start()) + 1
                                line_end = tool_code.find('\n', match.end())
                                if line_end == -1:
                                    line_end = len(tool_code)
                                
                                problematic_line = tool_code[line_start:line_end]
                                fixed_line = f"# {problematic_line} # TypeError: not callable\n        # Düzeltilmiş kod:"
                                
                                if obj_name == "json":
                                    fixed_line += "\n        import json\n        data = json.loads(response.text)"
                                else:
                                    fixed_line += f"\n        # '{obj_name}' çağrılabilir değil, alternatif bir çözüm kullanın"
                                
                                fixed_code = tool_code.replace(problematic_line, fixed_line)
                                print(f"TypeError (not callable) için düzeltme eklendi: {obj_name}")
            
            # 6. "value error" hatası (ValueError)
            elif "ValueError" in error_message:
                # Değer hatası için genel bir düzeltme
                value_match = re.search(r"ValueError: (.+)", error_message)
                if value_match:
                    value_error = value_match.group(1)
                    print(f"Tespit edilen değer hatası: '{value_error}'")
                    
                    if "JSON" in value_error or "json" in value_error:
                        # JSON ayrıştırma hatası
                        # JSON işleme kodunu bul
                        json_pattern = r"json\.loads\(([^)]+)\)"
                        json_matches = list(re.finditer(json_pattern, tool_code))
                        
                        if json_matches:
                            # İlk eşleşmeyi düzelt
                            match = json_matches[0]
                            line_start = tool_code.rfind('\n', 0, match.start()) + 1
                            line_end = tool_code.find('\n', match.end())
                            if line_end == -1:
                                line_end = len(tool_code)
                            
                            problematic_line = tool_code[line_start:line_end]
                            fixed_line = f"# {problematic_line} # ValueError: JSON\n        # Düzeltilmiş kod:"
                            fixed_line += "\n        try:\n            data = json.loads(response.text)\n        except ValueError:\n            data = {}"
                            
                            fixed_code = tool_code.replace(problematic_line, fixed_line)
                            print(f"ValueError (JSON) için düzeltme eklendi")
            
            # 7. "key error" hatası (KeyError)
            elif "KeyError" in error_message:
                # Anahtar hatası için genel bir düzeltme
                key_match = re.search(r"KeyError: ['\"]?([^'\"]+)['\"]?", error_message)
                if key_match:
                    missing_key = key_match.group(1)
                    print(f"Tespit edilen eksik anahtar: '{missing_key}'")
                    
                    # Anahtarı kullanan kodu bul
                    key_pattern = rf"\[['\"]?{missing_key}['\"]?\]"
                    key_matches = list(re.finditer(key_pattern, tool_code))
                    
                    if key_matches:
                        # İlk eşleşmeyi düzelt
                        match = key_matches[0]
                        line_start = tool_code.rfind('\n', 0, match.start()) + 1
                        line_end = tool_code.find('\n', match.end())
                        if line_end == -1:
                            line_end = len(tool_code)
                        
                        problematic_line = tool_code[line_start:line_end]
                        fixed_line = f"# {problematic_line} # KeyError\n        # Düzeltilmiş kod:"
                        
                        # dict.get() kullanarak düzelt
                        dict_name = problematic_line.split('[')[0].strip()
                        fixed_line += f"\n        {missing_key}_value = {dict_name}.get('{missing_key}')"
                        
                        fixed_code = tool_code.replace(problematic_line, fixed_line)
                        print(f"KeyError için düzeltme eklendi: {missing_key}")
            
            # 8. API hatası (requests.exceptions.RequestException)
            elif "RequestException" in error_message or "ConnectionError" in error_message or "HTTPError" in error_message:
                # API hatası için genel bir düzeltme
                print(f"API hatası tespit edildi")
                
                # requests.get veya requests.post çağrısını bul
                request_pattern = r"requests\.(get|post)\(([^)]+)\)"
                request_matches = list(re.finditer(request_pattern, tool_code))
                
                if request_matches:
                    # İlk eşleşmeyi düzelt
                    match = request_matches[0]
                    line_start = tool_code.rfind('\n', 0, match.start()) + 1
                    line_end = tool_code.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(tool_code)
                    
                    problematic_line = tool_code[line_start:line_end]
                    fixed_line = f"# {problematic_line} # RequestException\n        # Düzeltilmiş kod:"
                    fixed_line += "\n        try:\n            " + problematic_line + "\n        except requests.exceptions.RequestException as e:\n            return {\"error\": f\"API request failed: {str(e)}\"}"
                    
                    fixed_code = tool_code.replace(problematic_line, fixed_line)
                    print(f"API hatası için düzeltme eklendi")
            
            # Özel çözüm bulunamadıysa, AI ile düzeltme dene
            if not fixed_code:
                print(f"Özel bir çözüm bulunamadı, AI ile düzeltme deneniyor...")
                
                # AI'ya hata mesajını ve kodu gönder
                prompt = f"""
                Aşağıdaki Python kodunda bir hata var. Hatayı düzelt.
                
                Hata mesajı: {error_message}
                
                Kod:
                ```python
                {tool_code}
                ```
                
                Lütfen hatayı düzelt ve düzeltilmiş kodu döndür. Sadece kodu döndür, açıklama yapma.
                """
                
                # AI'dan düzeltilmiş kodu al
                fixed_code = AIService.generate_response(
                    prompt=prompt,
                    model_name=DEFAULT_MODEL,
                    temperature=0.2,
                    max_tokens=DEFAULT_MAX_TOKENS * 2,
                    top_p=DEFAULT_TOP_P
                )
                
                # Markdown kod bloklarını temizle
                fixed_code = re.sub(r'```python\s*', '', fixed_code)
                fixed_code = re.sub(r'```\s*', '', fixed_code)
                
                print(f"Tool kodu AI ile düzeltildi")
            
            # Düzeltilmiş kodu kaydet
            if fixed_code:
                with open(tool_path, 'w') as f:
                    f.write(fixed_code)
                
                print(f"Tool kodu güncellendi: {tool_path}")
                
                # Tool'u yeniden yükle
                module_name = f"dynamic_tools.{tool_filename}"
                if module_name in sys.modules:
                    del sys.modules[module_name]
                
                # Tool'u yeniden oluştur
                tool = DynamicToolManager.save_and_load_tool(fixed_code, tool_name)
                
                if tool:
                    # MCP sunucusuna kaydet
                    mcp_server.register_tool(tool)
                    print(f"Tool başarıyla düzeltildi ve kaydedildi: {tool_name}")
                    
                    # Tool bilgilerini oluştur
                    tool_info = {
                        "new_tool_needed": True,
                        "tool_name": tool_name,
                        "tool_description": tool.description
                    }
                    
                    return True, tool.name, tool_info
            
            return False, None, None
        except Exception as e:
            print(f"Tool debug ve düzeltme sırasında hata: {str(e)}")
            return False, None, None