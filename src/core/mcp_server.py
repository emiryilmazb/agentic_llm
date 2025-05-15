"""
Model Context Protocol (MCP) Server Implementation.

This module provides the MCP server implementation that manages tools
that can be used by agentic characters.
"""
import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Type

from src.tools.base import BaseTool, MCPTool
from src.utils.config import ENABLE_DYNAMIC_TOOLS

# Create a logger for this module
logger = logging.getLogger(__name__)

class MCPServer:
    """
    MCP Server that provides tools for AI characters to use.
    
    This class manages the registration and execution of tools that can be
    used by agentic characters through the Model Context Protocol (MCP).
    """
    
    def __init__(self, server_name: str):
        """
        Initialize the MCP server.
        
        Args:
            server_name: The name of the server
        """
        self.server_name = server_name
        self.tools: Dict[str, MCPTool] = {}
        logger.info(f"Initialized MCP server: {server_name}")
    
    def register_tool(self, tool: MCPTool) -> None:
        """
        Register a tool with the server.
        
        Args:
            tool: The tool to register
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool from the server by name.
        
        Args:
            tool_name: The name of the tool to unregister
            
        Returns:
            bool: True if the tool was successfully unregistered, False otherwise
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
            return True
        
        logger.warning(f"Attempted to unregister non-existent tool: {tool_name}")
        return False
    
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with the given arguments.
        
        Args:
            tool_name: The name of the tool to execute
            args: Dictionary of arguments for the tool
            
        Returns:
            Dictionary containing the results of the tool execution
        """
        logger.info(f"Executing tool: {tool_name}")
        
        # Check if the tool exists
        if tool_name not in self.tools:
            error_msg = f"Tool '{tool_name}' not found"
            logger.error(error_msg)
            return {"error": error_msg}
        
        # Execute the tool
        try:
            tool = self.tools[tool_name]
            
            # Log execution attempt
            logger.debug(f"Executing {tool_name} with args: {args}")
            
            # Execute the tool
            result = tool.execute(args)
            
            # Log execution result
            if isinstance(tool, MCPTool):
                tool.log_execution(args, result)
            else:
                logger.debug(f"Tool {tool_name} execution completed")
            
            return result
        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg}
    
    def get_tools_info(self) -> List[Dict[str, str]]:
        """
        Get information about all available tools.
        
        Returns:
            List of dictionaries containing tool information
        """
        logger.debug(f"Getting info for {len(self.tools)} tools")
        return [tool.get_info() for tool in self.tools.values()]
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: The name of the tool to get
            
        Returns:
            The tool if found, None otherwise
        """
        return self.tools.get(tool_name)
    
    def has_tool(self, tool_name: str) -> bool:
        """
        Check if a tool exists.
        
        Args:
            tool_name: The name of the tool to check
            
        Returns:
            True if the tool exists, False otherwise
        """
        return tool_name in self.tools


def load_builtin_tools(server: MCPServer) -> None:
    """
    Load and register all built-in tools.
    
    Args:
        server: The MCPServer instance to register tools with
    """
    logger.info("Loading built-in tools")
    
    # Import built-in tool modules
    from src.tools.builtin.search_wikipedia import SearchWikipedia
    from src.tools.builtin.get_current_time import GetCurrentTime
    from src.tools.builtin.get_weather import GetWeather
    from src.tools.builtin.open_website import OpenWebsite
    from src.tools.builtin.calculate_math import CalculateMath
    
    # Register built-in tools
    server.register_tool(SearchWikipedia())
    server.register_tool(GetCurrentTime())
    server.register_tool(GetWeather())
    server.register_tool(OpenWebsite())
    server.register_tool(CalculateMath())
    
    logger.info(f"Loaded {5} built-in tools")


def load_dynamic_tools(server: MCPServer) -> None:
    """
    Load and register all dynamic tools from the dynamic_tools directory.
    
    Args:
        server: The MCPServer instance to register tools with
    """
    if not ENABLE_DYNAMIC_TOOLS:
        logger.info("Dynamic tools are disabled")
        return
    
    logger.info("Loading dynamic tools")
    
    try:
        # Import the dynamic_tools package
        from src.tools.dynamic import tool_manager
        
        # Get the package path
        package_path = Path(tool_manager.__file__).parent
        
        # Track the number of tools loaded
        tools_loaded = 0
        
        # Iterate through all modules in the package
        for _, module_name, is_pkg in pkgutil.iter_modules([str(package_path)]):
            if is_pkg or module_name == "__init__" or module_name == "tool_manager":
                continue
            
            try:
                # Import the module
                module = importlib.import_module(f"src.tools.dynamic.{module_name}")
                
                # Find all MCPTool subclasses in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and
                        issubclass(obj, MCPTool) and
                        obj != MCPTool and
                        obj.__module__ == module.__name__):
                        
                        # Create an instance of the tool and register it
                        tool = obj()
                        server.register_tool(tool)
                        tools_loaded += 1
                        logger.debug(f"Registered dynamic tool: {tool.name}")
            except Exception as e:
                logger.error(f"Error loading dynamic tool module {module_name}: {str(e)}")
        
        logger.info(f"Loaded {tools_loaded} dynamic tools")
    except ImportError:
        # dynamic_tools package doesn't exist yet
        logger.warning("No dynamic tools package found")
    except Exception as e:
        logger.error(f"Error loading dynamic tools: {str(e)}")


# Create and configure the default MCP server
default_server = MCPServer("character_tools")

# Load built-in and dynamic tools
load_builtin_tools(default_server)
load_dynamic_tools(default_server)


def get_default_server() -> MCPServer:
    """
    Get the default MCP server instance.
    
    Returns:
        The default MCP server instance
    """
    return default_server