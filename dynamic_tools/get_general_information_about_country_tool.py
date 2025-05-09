from mcp_server import MCPTool
import requests
import json
import datetime
import re
from typing import Dict, Any, Optional, List

class GetGeneralInformationAboutCountryTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="get_general_information_about_country",
            description="Provides general information and impressions about a country, including aspects like culture, lifestyle, cost of living, and general atmosphere."
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        country = args.get("country")
        if not country:
            return {"error": "Country name is required."}

        try:
            # Wikipedia API for general overview
            wikipedia_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&titles={country}&explaintext=true"
            wikipedia_response = requests.get(wikipedia_url)
            wikipedia_response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            wikipedia_data = wikipedia_response.json()

            page_id = next(iter(wikipedia_data["query"]["pages"]))
            wikipedia_extract = wikipedia_data["query"]["pages"][page_id].get("extract", "No information found on Wikipedia.")

            # Scrape Wikitravel for travel-related information
            wikitravel_url = f"https://wikitravel.org/wiki/{country.replace(' ', '_')}"
            try:
                wikitravel_response = requests.get(wikitravel_url)
                wikitravel_response.raise_for_status()
                wikitravel_text = wikitravel_response.text

                # Extracting relevant sections (very basic, can be improved with more robust parsing)
                culture_match = re.search(r"<h2>\s*<span class=\"mw-headline\" id=\"Culture\">Culture<\/span>\s*<\/h2>(.*?)<h2>", wikitravel_text, re.DOTALL)
                lifestyle_match = re.search(r"<h2>\s*<span class=\"mw-headline\" id=\"Lifestyle\">Lifestyle<\/span>\s*<\/h2>(.*?)<h2>", wikitravel_text, re.DOTALL)
                cost_of_living_match = re.search(r"<h2>\s*<span class=\"mw-headline\" id=\"Cost_of_living\">Cost of living<\/span>\s*<\/h2>(.*?)<h2>", wikitravel_text, re.DOTALL)

                culture_info = culture_match.group(1) if culture_match else "No specific culture information found on Wikitravel."
                lifestyle_info = lifestyle_match.group(1) if lifestyle_match else "No specific lifestyle information found on Wikitravel."
                cost_of_living_info = cost_of_living_match.group(1) if cost_of_living_match else "No specific cost of living information found on Wikitravel."

            except requests.exceptions.RequestException as e:
                culture_info = f"Error fetching culture information from Wikitravel: {e}"
                lifestyle_info = f"Error fetching lifestyle information from Wikitravel: {e}"
                cost_of_living_info = f"Error fetching cost of living information from Wikitravel: {e}"

            # Combine information
            result = {
                "country": country,
                "wikipedia_overview": wikipedia_extract,
                "culture": culture_info,
                "lifestyle": lifestyle_info,
                "cost_of_living": cost_of_living_info
            }

            return result

        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching data: {e}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}