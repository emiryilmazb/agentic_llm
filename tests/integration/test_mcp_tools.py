"""
Integration tests for MCP tools.

These tests verify that the MCP tools work correctly with the MCP server.
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from src.core.mcp_server import MCPServer, get_default_server
from src.tools.base import MCPTool
from src.tools.builtin.search_wikipedia import SearchWikipedia
from src.tools.builtin.get_current_time import GetCurrentTime

class TestMCPTools:
    """Integration tests for MCP tools."""

    def test_mcp_server_registration(self):
        """Test that tools can be registered with the MCP server."""
        # Create a new MCP server
        server = MCPServer("test_server")
        
        # Create a test tool
        class TestTool(MCPTool):
            def __init__(self):
                super().__init__(
                    name="test_tool",
                    description="A test tool"
                )
            
            def execute(self, args):
                return {"result": "test_result"}
        
        # Register the tool
        tool = TestTool()
        server.register_tool(tool)
        
        # Check that the tool was registered
        assert "test_tool" in server.tools
        assert server.tools["test_tool"] == tool
        
        # Get tool info
        tools_info = server.get_tools_info()
        assert any(t["name"] == "test_tool" for t in tools_info)
        
        # Execute the tool
        result = server.execute_tool("test_tool", {})
        assert result["result"] == "test_result"
        
        # Unregister the tool
        success = server.unregister_tool("test_tool")
        assert success is True
        assert "test_tool" not in server.tools

    @patch('wikipedia.search')
    @patch('wikipedia.page')
    def test_search_wikipedia_tool(self, mock_page, mock_search):
        """Test the SearchWikipedia tool."""
        # Create mock data
        mock_search.return_value = ["Test Page", "Other Page"]
        
        mock_page_obj = MagicMock()
        mock_page_obj.summary = "This is a test page summary."
        mock_page_obj.url = "https://en.wikipedia.org/wiki/Test_Page"
        mock_page_obj.title = "Test Page"
        mock_page.return_value = mock_page_obj
        
        # Create the tool
        tool = SearchWikipedia()
        
        # Execute the tool
        result = tool.execute({"query": "test query"})
        
        # Check the result
        assert result["status"] == "success"
        assert result["title"] == "Test Page"
        assert result["summary"] == "This is a test page summary."
        assert result["url"] == "https://en.wikipedia.org/wiki/Test_Page"
        assert result["results"] == ["Test Page", "Other Page"]
        
        # Check that the Wikipedia API was called correctly
        mock_search.assert_called_once_with("test query", results=5)
        mock_page.assert_called_once_with("Test Page")

    @patch('datetime.datetime')
    def test_get_current_time_tool(self, mock_datetime):
        """Test the GetCurrentTime tool."""
        # Create mock data
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2025-05-14 21:00:00"
        mock_datetime.now.return_value = mock_now
        
        # Create the tool
        tool = GetCurrentTime()
        
        # Execute the tool
        result = tool.execute({})
        
        # Check the result
        assert result["current_time"] == "2025-05-14 21:00:00"
        assert "timezone" in result
        
        # Check that datetime.now was called
        mock_datetime.now.assert_called_once()
        mock_now.strftime.assert_called_once()

    def test_default_server(self):
        """Test that the default server is properly configured."""
        # Get the default server
        server = get_default_server()
        
        # Check that it has the expected tools
        tools_info = server.get_tools_info()
        tool_names = [tool["name"] for tool in tools_info]
        
        # Check for built-in tools
        assert "search_wikipedia" in tool_names
        assert "get_current_time" in tool_names
        assert "get_weather" in tool_names
        assert "open_website" in tool_names
        assert "calculate_math" in tool_names

    def test_tool_error_handling(self):
        """Test that tools properly handle errors."""
        # Create a new MCP server
        server = MCPServer("test_server")
        
        # Create a test tool that raises an exception
        class ErrorTool(MCPTool):
            def __init__(self):
                super().__init__(
                    name="error_tool",
                    description="A tool that raises an error"
                )
            
            def execute(self, args):
                raise ValueError("Test error")
        
        # Register the tool
        tool = ErrorTool()
        server.register_tool(tool)
        
        # Execute the tool and check that the error is handled
        result = server.execute_tool("error_tool", {})
        assert "error" in result
        assert "Test error" in result["error"]

    def test_tool_validation(self):
        """Test that tools properly validate arguments."""
        # Create a new MCP server
        server = MCPServer("test_server")
        
        # Create a test tool that requires arguments
        class ValidationTool(MCPTool):
            def __init__(self):
                super().__init__(
                    name="validation_tool",
                    description="A tool that validates arguments"
                )
            
            def execute(self, args):
                # Validate required arguments
                validation_error = self.validate_args(args, ["required_param"])
                if validation_error:
                    return validation_error
                
                return {"result": args["required_param"]}
        
        # Register the tool
        tool = ValidationTool()
        server.register_tool(tool)
        
        # Execute the tool without the required parameter
        result = server.execute_tool("validation_tool", {})
        assert "error" in result
        assert "required_param" in result["error"]
        
        # Execute the tool with the required parameter
        result = server.execute_tool("validation_tool", {"required_param": "test_value"})
        assert result["result"] == "test_value"

    def test_tool_chain(self):
        """Test that tools can be chained together."""
        # Create a new MCP server
        server = MCPServer("test_server")
        
        # Create test tools
        class ToolA(MCPTool):
            def __init__(self):
                super().__init__(
                    name="tool_a",
                    description="Tool A"
                )
            
            def execute(self, args):
                return {"result": "result_a"}
        
        class ToolB(MCPTool):
            def __init__(self):
                super().__init__(
                    name="tool_b",
                    description="Tool B"
                )
            
            def execute(self, args):
                # Use the result from Tool A
                tool_a_result = args.get("tool_a_result", "")
                return {"result": f"{tool_a_result}_result_b"}
        
        # Register the tools
        server.register_tool(ToolA())
        server.register_tool(ToolB())
        
        # Execute Tool A
        result_a = server.execute_tool("tool_a", {})
        
        # Execute Tool B with the result from Tool A
        result_b = server.execute_tool("tool_b", {"tool_a_result": result_a["result"]})
        
        # Check the final result
        assert result_b["result"] == "result_a_result_b"