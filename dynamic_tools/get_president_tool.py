from mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List

class GetPresidentTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="get_president",
            description="Retrieves the current president of a given country."
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        country = args.get("country")

        if not country:
            return {"error": "Country name is required."}

        try:
            # Use a public API to get the president's name.  This API is not perfect, but it's free and doesn't require an API key.
            # It relies on Wikidata.
            url = f"https://query.wikidata.org/sparql?format=json&query=SELECT ?presidentLabel WHERE {{ ?country wdt:P31 wd:Q6256; rdfs:label '{country}'@en. ?president wdt:P39 wd:P35; wdt:P102 ?country. SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'en'. ?president rdfs:label ?presidentLabel. }} }}"
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if data and data["results"]["bindings"]:
                president_name = data["results"]["bindings"][0]["presidentLabel"]["value"]
                return {"president": president_name}
            else:
                return {"result": f"Could not find the president for {country}."}

        except requests.exceptions.RequestException as e:
            return {"error": f"Error during API request: {e}"}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON response: {e}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}