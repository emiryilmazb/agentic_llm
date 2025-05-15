"""
Wikipedia search tool implementation.

This module provides a tool for searching Wikipedia and retrieving information.
"""
import logging
from typing import Dict, Any, Optional, List

import wikipedia

from src.tools.base import MCPTool
from src.utils.config import DEFAULT_WIKI_LANGUAGE, DEFAULT_WIKI_RESULTS

# Create a logger for this module
logger = logging.getLogger(__name__)

class SearchWikipedia(MCPTool):
    """
    Tool to search Wikipedia for information.
    
    This tool allows characters to search Wikipedia for information on various topics.
    """
    
    def __init__(self):
        """Initialize the Wikipedia search tool."""
        super().__init__(
            name="search_wikipedia",
            description="Searches Wikipedia for information on a topic"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Wikipedia search tool.
        
        Args:
            args: Dictionary containing the following keys:
                - query: The search query (required)
                - language: The language code (optional, default: from config)
                - results: The number of results to return (optional, default: from config)
        
        Returns:
            Dictionary containing the search results and summary
        """
        # Validate required arguments
        validation_error = self.validate_args(args, ["query"])
        if validation_error:
            return validation_error
        
        # Extract arguments
        query = args.get("query", "")
        language = args.get("language", DEFAULT_WIKI_LANGUAGE)
        results_count = args.get("results", DEFAULT_WIKI_RESULTS)
        
        try:
            # Set the language
            wikipedia.set_lang(language)
            logger.debug(f"Set Wikipedia language to: {language}")
            
            # Search for the query
            logger.info(f"Searching Wikipedia for: {query}")
            search_results = wikipedia.search(query, results=results_count)
            
            if not search_results:
                logger.warning(f"No results found for query: {query}")
                return {
                    "results": [],
                    "summary": f"No results found for '{query}'",
                    "status": "no_results"
                }
            
            # Get summary of first result
            try:
                logger.debug(f"Getting page for first result: {search_results[0]}")
                page = wikipedia.page(search_results[0])
                summary = page.summary
                url = page.url
                title = page.title
                
                logger.info(f"Found Wikipedia page: {title}")
                
                return {
                    "results": search_results,
                    "title": title,
                    "summary": summary,
                    "url": url,
                    "language": language,
                    "status": "success"
                }
            except wikipedia.exceptions.DisambiguationError as e:
                logger.warning(f"Disambiguation error for query: {query}")
                return {
                    "results": e.options,
                    "summary": f"Multiple results found for '{query}', please be more specific. Options include: {', '.join(e.options[:5])}...",
                    "status": "disambiguation"
                }
            except wikipedia.exceptions.PageError as e:
                logger.warning(f"Page error for query: {query}")
                return {
                    "results": search_results,
                    "summary": f"Could not find a specific page for '{query}'. Similar topics: {', '.join(search_results)}",
                    "status": "page_error"
                }
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {str(e)}", exc_info=True)
            return self.handle_error(e)