from mcp_server import MCPTool
import requests
from typing import Dict, Any, Optional, List
import json

class ImageGeneratorTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="image_generator",
            description="Generates an image based on a text description."
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        prompt = args.get("prompt")

        if not prompt:
            return {"status": "error", "message": "Prompt is required."}

        # Using a free image generation API (requires signup and API key)
        # Replace with your actual API key and API endpoint if needed.
        api_url = "https://api.craiyon.com/ai/dalle"  # Example API, might require changes
        headers = {'Content-Type': 'application/json'}
        data = {'prompt': prompt}

        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            result = response.json()

            if 'images' in result and len(result['images']) > 0:
                # Craiyon returns base64 encoded images.  We'll just return the first one.
                image_data = result['images'][0]
                return {"status": "success", "image_data": image_data, "prompt": prompt}
            else:
                return {"status": "error", "message": "Image generation failed.", "response": result}

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"API request failed: {e}"}
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"Failed to decode JSON response: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred: {e}"}