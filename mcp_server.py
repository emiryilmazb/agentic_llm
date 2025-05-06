import json
import os
import requests
import datetime
import wikipedia
import re
import webbrowser
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
        
        # Note: In a real implementation, you would use an actual weather API
        # This is a mock implementation for demonstration purposes
        mock_weather_data = {
            "location": location,
            "temperature": 22,
            "condition": "Partly cloudy",
            "humidity": 65,
            "wind": "10 km/h"
        }
        
        return mock_weather_data

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

# Create and configure the default MCP server
default_server = MCPServer("character_tools")
default_server.register_tool(SearchWikipedia())
default_server.register_tool(GetCurrentTime())
default_server.register_tool(GetWeather())
default_server.register_tool(OpenWebsite())
default_server.register_tool(CalculateMath())

def get_default_server() -> MCPServer:
    """Get the default MCP server instance"""
    return default_server
