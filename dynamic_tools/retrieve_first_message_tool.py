from mcp_server import MCPTool
import requests  # Only use standard library or these packages: requests, json, datetime, re
from typing import Dict, Any, Optional, List # Ensure typing is available

class RetrieveFirstMessageTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="retrieve_first_message", # Use the provided tool_name
            description="Retrieves the first message sent by the user to the AI assistant." # Use the provided tool_description
        )
        self.conversation_history = [] # Initialize conversation history

    def set_conversation_history(self, history: List[Dict[str, Any]]):
        """
        Sets the conversation history for the tool.
        """
        self.conversation_history = history

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieves the first message sent by the user to the AI assistant.
        """
        if not self.conversation_history:
            return {"first_message": None, "error": "No conversation history available."}

        first_message = None
        for message in self.conversation_history:
            if message.get("role") == "user":
                first_message = message.get("content")
                break

        if first_message:
            return {"first_message": first_message}
        else:
            return {"first_message": None, "error": "No user messages found in conversation history."}

if __name__ == '__main__':
    # Example Usage (for testing purposes only)
    tool = RetrieveFirstMessageTool()
    
    # Simulate a conversation history
    conversation_history = [
        {"role": "assistant", "content": "Hello, how can I help you?"},
        {"role": "user", "content": "What is the weather like today?"},
        {"role": "assistant", "content": "I am checking the weather for you."},
        {"role": "user", "content": "Thank you!"},
    ]
    
    tool.set_conversation_history(conversation_history)
    
    # Execute the tool
    result = tool.execute({})
    
    # Print the result
    print(result)