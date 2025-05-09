from mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List

class AnalyzeSentimentTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="analyze_sentiment",
            description="Analyzes the sentiment of a given text and returns a sentiment score (positive, negative, or neutral) along with a confidence level."
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if "text" not in args:
            return {"error": "Missing required parameter: text"}

        text = args["text"]

        try:
            # Using a simple sentiment analysis API (replace with a more robust solution if needed)
            api_url = "https://api.meaningcloud.com/sentiment-2.1"
            payload = {
                'key': 'YOUR_MEANINGCLOUD_API_KEY',  # Replace with your actual API key
                'lang': 'en',
                'txt': text
            }
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(api_url, data=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data['status']['code'] == '0':
                    sentiment_score = float(data['score_tag'].replace('P+', '1').replace('P', '0.5').replace('NEU', '0').replace('N', '-0.5').replace('N+', '-1'))
                    confidence = float(data['confidence']) / 100.0
                    return {"sentiment_score": sentiment_score, "confidence": confidence}
                else:
                    return {"error": f"Sentiment analysis failed: {data['status']['msg']}"}
            else:
                return {"error": f"API request failed with status code: {response.status_code}"}

        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {e}"}
        except json.JSONDecodeError:
            return {"error": "Failed to decode JSON response from API"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}