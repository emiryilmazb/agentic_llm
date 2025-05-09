from mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List

class TranslateTextTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="translate_text",
            description="Translates text from one language to another."
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        text = args.get("text")
        target_language = args.get("target_language")
        source_language = args.get("source_language")

        if not text:
            return {"error": "Text to translate is required."}
        if not target_language:
            return {"error": "Target language is required."}

        try:
            # Using a free translation API (Lingva Translate)
            base_url = "https://libretranslate.de/translate"
            payload = {
                "q": text,
                "target": target_language,
                "source": source_language if source_language else "auto",
                "format": "text"
            }
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }

            response = requests.post(base_url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            translation = response.json().get("translatedText")

            if translation:
                return {"translated_text": translation}
            else:
                return {"error": "Translation failed."}

        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {e}"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from the translation API."}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}