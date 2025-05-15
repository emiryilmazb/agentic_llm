from src.tools.base import DynamicTool
import requests
import json
import datetime
from typing import Dict, Any, Optional, List
import re

class TranslateTextTool(DynamicTool):
    def __init__(self):
        super().__init__(
            name="translate_text",
            description="Translates text from one language to another.",
            parameters=[
                {
                    "name": "text",
                    "type": "string",
                    "description": "The text to be translated.",
                    "required": True
                },
                {
                    "name": "target_language",
                    "type": "string",
                    "description": "The language to translate the text into (e.g., 'en' for English, 'es' for Spanish).",
                    "required": True
                },
                {
                    "name": "source_language",
                    "type": "string",
                    "description": "The language of the input text. If not provided, attempt to auto-detect.",
                    "required": False
                }
            ],
            created_at=datetime.datetime.now().isoformat()
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        text = args.get("text")
        target_language = args.get("target_language")
        source_language = args.get("source_language")

        if not text:
            return {"error": "Text to translate is required."}
        if not target_language:
            return {"error": "Target language is required."}

        # Using a free translation API (LingvaTranslate) as no API key is provided.
        # This API is rate-limited, so it might not always work.
        base_url = "https://libretranslate.de/translate"
        payload = {
            "q": text,
            "source": source_language if source_language else "auto",
            "target": target_language,
            "format": "text"
        }

        try:
            response = requests.post(base_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            translation = response.json()
            if "error" in translation:
                return {"error": f"Translation failed: {translation['error']}"}
            translated_text = translation.get("translatedText")
            if translated_text is None:
                return {"error": "Translation failed: No translated text returned."}
            return {"translated_text": translated_text}

        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "Failed to decode JSON response from the translation API."}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}