from src.tools.base import DynamicTool
import requests  # Only use standard library or these packages: requests, json, datetime, re
from typing import Dict, Any, Optional, List # Ensure typing is available
import datetime
import re

class SetLanguageTool(DynamicTool):
    def __init__(self):
        super().__init__(
            name="set_language", # Use the provided tool_name
            description="Sets the language for the AI's responses.", # Use the provided tool_description
            parameters=[
                {
                    "name": "language",
                    "type": "string",
                    "description": "The language to set for the AI's responses. Must be a valid language code (e.g., 'tr' for Turkish, 'en' for English).",
                    "required": True
                }
            ],
            created_at=datetime.datetime.now().isoformat()
        )
        self.current_language = "en"  # Default language

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        # Parameter validation based on tool_parameters
        if not isinstance(args, dict):
            return {"error": "Invalid input: Input must be a dictionary."}

        language = args.get("language")

        if not language:
            return {"error": "Missing required parameter: language"}

        if not isinstance(language, str):
            return {"error": "Invalid parameter type: language must be a string."}

        if not re.match(r"^[a-z]{2}$", language):
            return {"error": "Invalid language code: language must be a two-letter ISO 639-1 code (e.g., 'en', 'tr')."}

        # Tool implementation using details from implementation_details
        # This is a simplified implementation. In a real-world scenario,
        # this would involve loading language-specific resources,
        # translating prompts, or adjusting the AI's output format.
        # For this example, we'll just store the language code.

        self.current_language = language
        result = {"success": True, "message": f"Language set to {language}"}

        return result