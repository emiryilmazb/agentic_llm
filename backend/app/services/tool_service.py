"""
Tool service for handling tool operations.
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Add parent directory to sys.path for relative imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.mcp_server import get_default_server
from app.utils.dynamic_tool_manager import DynamicToolManager
from app.core.config import settings

class ToolService:
    """Service class for handling tool operations."""
    
    @staticmethod
    def get_all_tools() -> Dict[str, List[Dict[str, str]]]:
        """
        Get all available tools, separated by type.
        
        Returns:
            Dictionary with built-in and dynamic tools
        """
        mcp_server = get_default_server()
        tools_info = mcp_server.get_tools_info()
        
        # Separate built-in and dynamic tools
        built_in_tools = []
        dynamic_tools = []
        
        for tool in tools_info:
            if tool['name'] in ['search_wikipedia', 'get_current_time', 'get_weather', 'open_website', 'calculate_math']:
                built_in_tools.append(tool)
            else:
                dynamic_tools.append(tool)
        
        return {
            "built_in_tools": built_in_tools,
            "dynamic_tools": dynamic_tools
        }
    
    @staticmethod
    def get_tool_by_name(tool_name: str) -> Optional[Dict[str, str]]:
        """
        Get a specific tool by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool information or None if not found
        """
        mcp_server = get_default_server()
        tools_info = mcp_server.get_tools_info()
        
        # Find the tool by name
        tool_info = next((tool for tool in tools_info if tool["name"] == tool_name), None)
        
        return tool_info
    
    @staticmethod
    def delete_dynamic_tool(tool_name: str) -> bool:
        """
        Delete a dynamic tool by name.
        
        Args:
            tool_name: Name of the tool to delete
            
        Returns:
            True if the tool was successfully deleted, False otherwise
        """
        try:
            # First check if the tool exists in the MCP server
            mcp_server = get_default_server()
            tool_exists = tool_name in [tool["name"] for tool in mcp_server.get_tools_info()]
            
            if not tool_exists:
                return False
            
            # Unregister the tool from the MCP server
            success = mcp_server.unregister_tool(tool_name)
            if not success:
                return False
            
            # Add the tool to the deleted_tools.json file for future reference
            deleted_tools_path = Path(settings.BASE_DIR / "dynamic_tools" / "deleted_tools.json")
            deleted_tools = []
            
            if deleted_tools_path.exists():
                try:
                    with open(deleted_tools_path, "r", encoding="utf-8") as f:
                        deleted_tools = json.load(f)
                except json.JSONDecodeError:
                    deleted_tools = []
            
            if tool_name not in deleted_tools:
                deleted_tools.append(tool_name)
                
                # Ensure the directory exists
                deleted_tools_path.parent.mkdir(exist_ok=True)
                
                with open(deleted_tools_path, "w", encoding="utf-8") as f:
                    json.dump(deleted_tools, f, ensure_ascii=False, indent=4)
            
            # Try to delete the tool file if it exists
            tool_file_name = f"{tool_name.lower()}_tool.py"
            if tool_name.endswith("_tool"):
                tool_file_name = f"{tool_name.lower()}.py"
            
            tool_file_path = Path(settings.BASE_DIR / "dynamic_tools" / tool_file_name)
            
            if tool_file_path.exists():
                try:
                    tool_file_path.unlink()
                    print(f"Deleted tool file: {tool_file_path}")
                except Exception as e:
                    print(f"Warning: Could not delete tool file {tool_file_path}: {str(e)}")
                    # Continue anyway as the tool is already unregistered from the MCP server
            
            return True
        except Exception as e:
            print(f"Error deleting dynamic tool: {str(e)}")
            return False
    
    @staticmethod
    def create_dynamic_tool(tool_description: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Create a new dynamic tool based on a description.
        
        Args:
            tool_description: Description of the tool to create
            
        Returns:
            Tuple of (success, tool_name, tool_info)
        """
        try:
            # Use the DynamicToolManager to create a new tool
            success, tool_name, tool_info = DynamicToolManager.create_and_register_tool(tool_description)
            
            if success and tool_name:
                return True, tool_name, tool_info
            
            return False, None, None
        except Exception as e:
            print(f"Error creating dynamic tool: {str(e)}")
            return False, None, None
