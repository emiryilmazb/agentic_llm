"""
Tool router for handling tool-related endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from typing import Dict, List, Any, Optional

from app.services.mcp_server import get_default_server
from app.services.tool_service import ToolService

router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
    responses={
        404: {"description": "Tool not found"},
        500: {"description": "Internal server error"}
    }
)

@router.get("/")
async def get_available_tools():
    """
    Get a list of all available tools.
    
    Returns:
        Dictionary containing built-in and dynamic tools
    """
    try:
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
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to retrieve tools", "error": str(e)}
        )

@router.get("/{tool_name}")
async def get_tool_details(
    tool_name: str = Path(..., description="Name of the tool")
):
    """
    Get details about a specific tool.
    
    Parameters:
        tool_name: Name of the tool
        
    Returns:
        Tool details
    """
    try:
        mcp_server = get_default_server()
        tools_info = mcp_server.get_tools_info()
        
        # Find the tool by name
        tool_info = next((tool for tool in tools_info if tool["name"] == tool_name), None)
        
        if not tool_info:
            raise HTTPException(
                status_code=404, 
                detail={"message": f"Tool '{tool_name}' not found"}
            )
        
        return tool_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to retrieve tool details", "error": str(e)}
        )

@router.delete("/{tool_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_name: str = Path(..., description="Name of the tool to delete")
):
    """
    Delete a dynamic tool by name.
    
    Parameters:
        tool_name: Name of the tool to delete
    """
    try:
        success = ToolService.delete_dynamic_tool(tool_name)
        if not success:
            raise HTTPException(
                status_code=404, 
                detail={"message": f"Tool '{tool_name}' not found or could not be deleted"}
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to delete tool", "error": str(e)}
        )
