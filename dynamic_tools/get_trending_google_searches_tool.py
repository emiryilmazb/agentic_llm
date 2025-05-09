from mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List

class GetTrendingGoogleSearchesTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="get_trending_google_searches",
            description="Retrieves the most popular search terms on Google in a specific country, along with their search volume."
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        country = args.get("country")
        if not country:
            return {"error": "Country is required."}

        try:
            # Use a public API for Google Trends data.  This is a simplified approach.
            # A more robust solution would involve web scraping or a paid API.
            # This API provides a list of trending searches for a given country code.
            # Note: This API might not be a direct Google Trends API, but it serves the purpose of demonstrating the tool.
            api_url = f"https://trends.google.com/trends/api/dailytrends?geo={country}&hl=en-US&ed=20240101" # Example date, replace with current date logic if needed
            
            # Attempt to fetch data from the Google Trends API.  If this fails, fall back to a different approach.
            response = requests.get(api_url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            
            # The response from Google Trends is often prefixed with some characters.
            # We need to strip those characters to get valid JSON.
            json_data = json.loads(response.text[4:])
            
            trending_searches = []
            for topic in json_data['default']['trendingSearches']:
                trending_searches.append({
                    'title': topic['title']['query'],
                    'traffic': topic['formattedTraffic']
                })
            
            return {"trending_searches": trending_searches}

        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching data from Google Trends API: {e}"}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON response: {e}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}