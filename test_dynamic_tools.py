"""
Test script for demonstrating the dynamic tool creation functionality.
This script simulates user queries that would trigger the creation of new tools.
"""
import json
import time
from pathlib import Path

from utils.dynamic_tool_manager import DynamicToolManager
from mcp_server import get_default_server, MCPTool
from agentic_character import AgenticCharacter
from utils.character_service import CharacterService
from utils.config import DATA_DIR

def print_separator():
    """Print a separator line"""
    print("\n" + "="*80 + "\n")

def create_test_character():
    """Create a test character for demonstration"""
    character_name = "Test Assistant"
    character_data = {
        "name": character_name,
        "background": "A helpful AI assistant that can use tools and create new ones when needed.",
        "personality": "Helpful, friendly, and resourceful. Always tries to find a way to assist the user.",
        "prompt": "You are a helpful AI assistant named Test Assistant. You help users by answering questions and performing tasks.",
        "chat_history": [],
        "use_agentic": True
    }
    
    # Create the character prompt
    prompt = CharacterService.create_prompt(
        character_name,
        character_data["background"],
        character_data["personality"],
        None  # No wiki data
    )
    character_data["prompt"] = prompt
    
    # Create an agentic character
    character = AgenticCharacter(character_data)
    return character

def test_existing_tools():
    """Test using existing tools"""
    character = create_test_character()
    
    print("Testing existing tools...")
    
    # Test the weather tool
    user_message = "What's the weather like in Istanbul?"
    print(f"User: {user_message}")
    
    response = character.get_response(user_message)
    print(f"Assistant: {response['display_text']}")
    
    print_separator()
    
    # Test the Wikipedia tool
    user_message = "Tell me about Albert Einstein"
    print(f"User: {user_message}")
    
    response = character.get_response(user_message)
    print(f"Assistant: {response['display_text']}")
    
    print_separator()

def test_dynamic_tool_creation():
    """Test the dynamic tool creation functionality"""
    character = create_test_character()
    
    print("Testing dynamic tool creation...")
    
    # Test currency conversion (should trigger creation of a currency converter tool if it doesn't exist)
    user_message = "What is 1 US Dollar in Turkish Lira?"
    print(f"User: {user_message}")
    
    # Check if a new tool is needed
    print("Checking if a new tool is needed...")
    tool_info = DynamicToolManager.detect_tool_need(user_message)
    
    if tool_info:
        print(f"New tool needed: {json.dumps(tool_info, indent=2)}")
        
        # Generate code for the new tool
        print("Generating code for the new tool...")
        tool_code = DynamicToolManager.generate_tool_code(tool_info)
        print(f"Generated code snippet:\n{tool_code[:200]}...\n")
        
        # Save and load the tool
        print("Saving and loading the tool...")
        tool = DynamicToolManager.save_and_load_tool(tool_code, tool_info["tool_name"])
        
        if tool:
            print(f"Successfully created tool: {tool.name}")
            
            # Register the tool with the MCP server
            mcp_server = get_default_server()
            mcp_server.register_tool(tool)
            
            # List all available tools
            tools_info = mcp_server.get_tools_info()
            print("Available tools:")
            for t in tools_info:
                print(f"- {t['name']}: {t['description']}")
            
            # Use the new tool
            print("\nUsing the new tool...")
            response = character.get_response(user_message)
            print(f"Assistant: {response['display_text']}")
        else:
            print("Failed to create the tool")
    else:
        print("No new tool needed or tool already exists")
        
        # Use existing tool
        response = character.get_response(user_message)
        print(f"Assistant: {response['display_text']}")
    
    print_separator()

def main():
    """Main function to run the tests"""
    print("Dynamic Tool Creation System Test\n")
    
    # Ensure the data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    # Test existing tools
    test_existing_tools()
    
    # Test dynamic tool creation
    test_dynamic_tool_creation()
    
    print("Test completed!")

if __name__ == "__main__":
    main()
