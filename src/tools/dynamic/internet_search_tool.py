from src.tools.base import DynamicTool
import requests
import json
import datetime
from typing import Dict, Any, Optional, List
import re

class InternetSearchTool(DynamicTool):
    def __init__(self):
        super().__init__(
            name="internet_search",
            description="Searches the internet for information on a given topic and returns relevant results.",
            created_at=datetime.datetime.now().isoformat()
        )
        # Store parameters information as a class attribute instead
        self.parameters = [
            {
                "name": "query",
                "type": "string",
                "description": "The search query to use.",
                "required": True
            }
        ]
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        query = args.get("query")
        if not query:
            return {"error": "Query is required."}
        
        try:
            from duckduckgo_search import ddg
            results = ddg(query, max_results=5)
            
            if results:
                summarized_results = []
                for result in results:
                    summarized_results.append({
                        "title": result["title"],
                        "href": result["href"],
                        "body": result["body"]
                    })
                return {"results": summarized_results}
            else:
                return {"results": []}
        except ImportError:
            return {"error": "DuckDuckGo Search API is not available. Please install duckduckgo_search."}
        except Exception as e:
            return {"error": f"An error occurred during the search: {str(e)}"}