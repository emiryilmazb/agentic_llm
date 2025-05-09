import json
import os
import requests
import datetime
import wikipedia
import re
import webbrowser
import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

class MCPTool:
    """Base class for MCP tools that characters can use"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool and return results"""
        raise NotImplementedError("Subclasses must implement execute method")

class SearchWikipedia(MCPTool):
    """Tool to search Wikipedia for information"""
    def __init__(self):
        super().__init__(
            name="search_wikipedia",
            description="Searches Wikipedia for information on a topic"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        query = args.get("query", "")
        language = args.get("language", "tr")
        
        if not query:
            return {"error": "Query parameter is required"}
        
        try:
            wikipedia.set_lang(language)
            search_results = wikipedia.search(query, results=3)
            
            if not search_results:
                return {"results": [], "summary": f"No results found for '{query}'"}
            
            # Get summary of first result
            try:
                page = wikipedia.page(search_results[0])
                summary = page.summary
                url = page.url
            except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
                summary = f"Multiple results found for '{query}', please be more specific"
                url = None
            
            return {
                "results": search_results,
                "summary": summary,
                "url": url
            }
        except Exception as e:
            return {"error": str(e)}

class GetCurrentTime(MCPTool):
    """Tool to get the current date and time"""
    def __init__(self):
        super().__init__(
            name="get_current_time",
            description="Returns the current date and time"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        timezone = args.get("timezone", "Europe/Istanbul")
        format_str = args.get("format", "%Y-%m-%d %H:%M:%S")
        
        now = datetime.datetime.now()
        formatted_time = now.strftime(format_str)
        
        return {
            "current_time": formatted_time,
            "timezone": timezone
        }

class GetWeather(MCPTool):
    """Tool to get weather information for a location"""
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="Gets weather information for a specified location"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        location = args.get("location", "")
        
        if not location:
            return {"error": "Location parameter is required"}
        
        # Basit bir geocoding işlemi
        geocode_result = self._geocode_location(location)
        
        if "warning" in geocode_result:
            print(f"Warning: {geocode_result['warning']}")
        
        latitude = geocode_result["latitude"]
        longitude = geocode_result["longitude"]
        
        # Open-Meteo API'sini kullan
        try:
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": ["temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m"],
                    "timezone": "auto"
                }
            )
            
            if response.status_code != 200:
                # API çağrısı başarısız olursa, hata mesajı döndür
                error_message = f"API request failed with status code {response.status_code}"
                print(error_message)
                return {"error": error_message}
            
            data = response.json()
            
            # Hava durumu kodlarını açıklamalara dönüştür
            weather_descriptions = {
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
            }
            
            current = data.get("current", {})
            
            if not current:
                # Veri alınamazsa, hata mesajı döndür
                error_message = "Failed to get current weather data from API response"
                print(error_message)
                return {"error": error_message}
            
            temperature = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            weather_code = current.get("weather_code")
            wind_speed = current.get("wind_speed_10m")
            
            # Herhangi bir veri eksikse, hata mesajı döndür
            if temperature is None or humidity is None or weather_code is None or wind_speed is None:
                missing_fields = []
                if temperature is None: missing_fields.append("temperature")
                if humidity is None: missing_fields.append("humidity")
                if weather_code is None: missing_fields.append("weather_code")
                if wind_speed is None: missing_fields.append("wind_speed")
                
                error_message = f"Missing data fields in API response: {', '.join(missing_fields)}"
                print(error_message)
                return {"error": error_message}
            
            weather_condition = weather_descriptions.get(weather_code, "Unknown")
            
            return {
                "location": location,
                "temperature": temperature,
                "condition": weather_condition,
                "humidity": humidity,
                "wind": f"{wind_speed} km/h"
            }
        except Exception as e:
            error_message = f"Error getting weather data: {str(e)}"
            print(error_message)
            return {"error": error_message}
    
    def _geocode_location(self, location: str) -> Dict[str, Any]:
        """
        Basit bir geocoding işlemi
        Gerçek uygulamada daha gelişmiş bir geocoding servisi kullanılabilir
        """
        # Bazı yaygın şehirler ve ülkeler için sabit koordinatlar
        geocode_map = {
            # Türkiye şehirleri
            "istanbul": {"latitude": 41.0082, "longitude": 28.9784},
            "ankara": {"latitude": 39.9334, "longitude": 32.8597},
            "izmir": {"latitude": 38.4237, "longitude": 27.1428},
            "antalya": {"latitude": 36.8969, "longitude": 30.7133},
            "bursa": {"latitude": 40.1885, "longitude": 29.0610},
            "adana": {"latitude": 37.0000, "longitude": 35.3213},
            
            # Avrupa şehirleri
            "london": {"latitude": 51.5074, "longitude": -0.1278},
            "paris": {"latitude": 48.8566, "longitude": 2.3522},
            "berlin": {"latitude": 52.5200, "longitude": 13.4050},
            "rome": {"latitude": 41.9028, "longitude": 12.4964},
            "madrid": {"latitude": 40.4168, "longitude": -3.7038},
            "amsterdam": {"latitude": 52.3676, "longitude": 4.9041},
            "brussels": {"latitude": 50.8503, "longitude": 4.3517},
            "vienna": {"latitude": 48.2082, "longitude": 16.3738},
            "athens": {"latitude": 37.9838, "longitude": 23.7275},
            
            # Amerika şehirleri
            "new york": {"latitude": 40.7128, "longitude": -74.0060},
            "los angeles": {"latitude": 34.0522, "longitude": -118.2437},
            "chicago": {"latitude": 41.8781, "longitude": -87.6298},
            "toronto": {"latitude": 43.6532, "longitude": -79.3832},
            "mexico city": {"latitude": 19.4326, "longitude": -99.1332},
            "rio de janeiro": {"latitude": -22.9068, "longitude": -43.1729},
            "buenos aires": {"latitude": -34.6037, "longitude": -58.3816},
            
            # Asya şehirleri
            "tokyo": {"latitude": 35.6762, "longitude": 139.6503},
            "beijing": {"latitude": 39.9042, "longitude": 116.4074},
            "shanghai": {"latitude": 31.2304, "longitude": 121.4737},
            "hong kong": {"latitude": 22.3193, "longitude": 114.1694},
            "singapore": {"latitude": 1.3521, "longitude": 103.8198},
            "mumbai": {"latitude": 19.0760, "longitude": 72.8777},
            "delhi": {"latitude": 28.6139, "longitude": 77.2090},
            "seoul": {"latitude": 37.5665, "longitude": 126.9780},
            
            # Orta Doğu şehirleri
            "dubai": {"latitude": 25.2048, "longitude": 55.2708},
            "riyadh": {"latitude": 24.7136, "longitude": 46.6753},
            "jeddah": {"latitude": 21.5433, "longitude": 39.1728},
            "mecca": {"latitude": 21.3891, "longitude": 39.8579},
            "tehran": {"latitude": 35.6892, "longitude": 51.3890},
            "cairo": {"latitude": 30.0444, "longitude": 31.2357},
            
            # Afrika şehirleri
            "lagos": {"latitude": 6.5244, "longitude": 3.3792},
            "nairobi": {"latitude": 1.2921, "longitude": 36.8219},
            "cape town": {"latitude": -33.9249, "longitude": 18.4241},
            "johannesburg": {"latitude": -26.2041, "longitude": 28.0473},
            
            # Okyanusya şehirleri
            "sydney": {"latitude": -33.8688, "longitude": 151.2093},
            "melbourne": {"latitude": -37.8136, "longitude": 144.9631},
            "auckland": {"latitude": -36.8509, "longitude": 174.7645},
            
            # Ülkeler (ülke merkezleri)
            "turkey": {"latitude": 38.9637, "longitude": 35.2433},
            "usa": {"latitude": 37.0902, "longitude": -95.7129},
            "uk": {"latitude": 55.3781, "longitude": -3.4360},
            "france": {"latitude": 46.2276, "longitude": 2.2137},
            "germany": {"latitude": 51.1657, "longitude": 10.4515},
            "italy": {"latitude": 41.8719, "longitude": 12.5674},
            "spain": {"latitude": 40.4637, "longitude": -3.7492},
            "russia": {"latitude": 61.5240, "longitude": 105.3188},
            "china": {"latitude": 35.8617, "longitude": 104.1954},
            "japan": {"latitude": 36.2048, "longitude": 138.2529},
            "india": {"latitude": 20.5937, "longitude": 78.9629},
            "brazil": {"latitude": -14.2350, "longitude": -51.9253},
            "australia": {"latitude": -25.2744, "longitude": 133.7751},
            "canada": {"latitude": 56.1304, "longitude": -106.3468},
            "saudi arabia": {"latitude": 23.8859, "longitude": 45.0792},
            "arabia": {"latitude": 23.8859, "longitude": 45.0792},  # Arabistan için özel giriş
            "egypt": {"latitude": 26.8206, "longitude": 30.8025},
            "south africa": {"latitude": -30.5595, "longitude": 22.9375}
        }
        
        # Lokasyonu küçük harfe çevir ve haritada ara
        location_lower = location.lower().strip()
        
        # Tam eşleşme kontrolü
        if location_lower in geocode_map:
            print(f"Exact match found for '{location}': {geocode_map[location_lower]}")
            return geocode_map[location_lower]
        
        # Kısmi eşleşme kontrolü - daha akıllı algoritma
        best_match = None
        best_match_score = 0
        
        for key, coords in geocode_map.items():
            # Tam içerme kontrolü
            if key in location_lower:
                match_score = len(key) / len(location_lower)
                if match_score > best_match_score:
                    best_match = key
                    best_match_score = match_score
            elif location_lower in key:
                match_score = len(location_lower) / len(key)
                if match_score > best_match_score:
                    best_match = key
                    best_match_score = match_score
        
        # Eğer iyi bir eşleşme bulunduysa (skor > 0.5)
        if best_match and best_match_score > 0.5:
            print(f"Partial match found for '{location}': {best_match} (score: {best_match_score})")
            return geocode_map[best_match]
        
        # Geocoding API kullanma (bu örnekte taklit ediyoruz)
        try:
            # Gerçek bir uygulamada burada bir geocoding API'si kullanılabilir
            # Örneğin: Nominatim, Google Maps Geocoding API, vb.
            
            # Bazı özel durumlar için manuel eşleştirme
            if "arab" in location_lower:
                print(f"Special case for '{location}': Using Saudi Arabia coordinates")
                return geocode_map["saudi arabia"]
            
            if "amster" in location_lower:
                print(f"Special case for '{location}': Using Amsterdam coordinates")
                return geocode_map["amsterdam"]
            
            # Eşleşme bulunamazsa, varsayılan olarak İstanbul koordinatlarını döndür
            # ve bir uyarı ekle
            print(f"No match found for '{location}'. Using default coordinates for Istanbul.")
            return {
                "latitude": 41.0082,
                "longitude": 28.9784,
                "warning": f"Could not geocode '{location}'. Using default coordinates for Istanbul."
            }
        except Exception as e:
            print(f"Error in geocoding: {str(e)}")
            return {
                "latitude": 41.0082,
                "longitude": 28.9784,
                "warning": f"Error geocoding '{location}': {str(e)}. Using default coordinates for Istanbul."
            }

class OpenWebsite(MCPTool):
    """Tool to open a website in the browser"""
    def __init__(self):
        super().__init__(
            name="open_website",
            description="Opens a specified URL in the browser"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        url = args.get("url", "")
        
        if not url:
            return {"error": "URL parameter is required"}
        
        # Validate URL format
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            # In a real implementation, this would be handled differently in a web app
            # This is for demonstration purposes
            webbrowser.open(url)
            return {"status": "success", "message": f"Opened {url} in browser"}
        except Exception as e:
            return {"error": str(e)}

class CalculateMath(MCPTool):
    """Tool to evaluate mathematical expressions"""
    def __init__(self):
        super().__init__(
            name="calculate_math",
            description="Evaluates a mathematical expression"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        expression = args.get("expression", "")
        
        if not expression:
            return {"error": "Expression parameter is required"}
        
        # Basic validation to prevent code execution
        if not re.match(r'^[0-9+\-*/().%\s]+$', expression):
            return {"error": "Invalid characters in expression"}
        
        try:
            # Using eval for demonstration - in production, use a safer alternative
            result = eval(expression)
            return {
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {"error": str(e)}

class MCPServer:
    """MCP Server that provides tools for AI characters to use"""
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.tools: Dict[str, MCPTool] = {}
    
    def register_tool(self, tool: MCPTool) -> None:
        """Register a tool with the server"""
        self.tools[tool.name] = tool
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool from the server by name
        
        Args:
            tool_name: The name of the tool to unregister
            
        Returns:
            bool: True if the tool was successfully unregistered, False otherwise
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            return True
        return False
    
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with the given arguments"""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}
        
        try:
            return self.tools[tool_name].execute(args)
        except Exception as e:
            return {"error": str(e)}
    
    def get_tools_info(self) -> List[Dict[str, str]]:
        """Get information about all available tools"""
        return [{"name": t.name, "description": t.description} for t in self.tools.values()]

def load_dynamic_tools(server: MCPServer) -> None:
    """
    Load and register all dynamic tools from the dynamic_tools directory.
    
    Args:
        server: The MCPServer instance to register tools with
    """
    try:
        # Import the dynamic_tools package
        import dynamic_tools
        
        # Get the package path
        package_path = Path(dynamic_tools.__file__).parent
        
        # Iterate through all modules in the package
        for _, module_name, is_pkg in pkgutil.iter_modules([str(package_path)]):
            if is_pkg or module_name == "__init__":
                continue
                
            try:
                # Import the module
                module = importlib.import_module(f"dynamic_tools.{module_name}")
                
                # Find all MCPTool subclasses in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and
                        issubclass(obj, MCPTool) and
                        obj != MCPTool and
                        obj.__module__ == module.__name__):
                        
                        # Create an instance of the tool and register it
                        tool = obj()
                        server.register_tool(tool)
                        print(f"Registered dynamic tool: {tool.name}")
            except Exception as e:
                print(f"Error loading dynamic tool module {module_name}: {str(e)}")
    except ImportError:
        # dynamic_tools package doesn't exist yet
        print("No dynamic tools package found")
    except Exception as e:
        print(f"Error loading dynamic tools: {str(e)}")

# Create and configure the default MCP server
default_server = MCPServer("character_tools")
default_server.register_tool(SearchWikipedia())
default_server.register_tool(GetCurrentTime())
default_server.register_tool(GetWeather())
default_server.register_tool(OpenWebsite())
default_server.register_tool(CalculateMath())

# Load any existing dynamic tools
load_dynamic_tools(default_server)

def get_default_server() -> MCPServer:
    """Get the default MCP server instance"""
    return default_server
