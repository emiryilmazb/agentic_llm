from app.services.mcp_server import MCPTool
import requests  # Only use standard library or these packages: requests, json, datetime, re
from typing import Dict, Any, Optional, List # Ensure typing is available

class SelfIntroductionTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="self_introduction", # Use the provided tool_name
            description="Provides a brief introduction of the AI assistant, including its capabilities and purpose." # Use the provided tool_description
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provides a brief introduction of the AI assistant.

        Returns:
            Dict[str, Any]: A dictionary containing the introduction message.
        """
        introduction = "I am an AI assistant designed to help you with various tasks. I can search the web, get the current time, provide weather information, open websites, and perform calculations. I am still under development, and my knowledge is limited to the data I have been trained on. I strive to provide accurate and helpful information, but please verify critical information independently."
        return {"introduction": introduction}