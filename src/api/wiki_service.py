"""
Wikipedia service utilities for fetching information from Wikipedia.

This module provides a service class for interacting with the Wikipedia API
to fetch information about various topics.
"""
import logging
import wikipedia
from typing import Optional, List, Dict, Any

from src.utils.config import DEFAULT_WIKI_LANGUAGE, DEFAULT_WIKI_RESULTS

# Create a logger for this module
logger = logging.getLogger(__name__)

class WikiService:
    """
    Service class for handling Wikipedia interactions.
    
    This class provides methods for searching Wikipedia and retrieving
    information about various topics.
    """
    
    @staticmethod
    def set_language(language: str = DEFAULT_WIKI_LANGUAGE) -> None:
        """
        Set the language for Wikipedia searches.
        
        Args:
            language: Language code (e.g., 'tr' for Turkish, 'en' for English)
        """
        logger.debug(f"Setting Wikipedia language to: {language}")
        wikipedia.set_lang(language)
    
    @staticmethod
    def fetch_info(query: str, language: str = DEFAULT_WIKI_LANGUAGE) -> str:
        """
        Fetch information about a topic from Wikipedia.
        
        Args:
            query: The topic to search for
            language: Language code (e.g., 'tr' for Turkish, 'en' for English)
            
        Returns:
            Summary text from Wikipedia or error message
        """
        logger.info(f"Fetching Wikipedia information for: {query} (language: {language})")
        try:
            # Set language
            WikiService.set_language(language)
            
            # Search for the topic with configured number of results
            search_results = wikipedia.search(query, results=DEFAULT_WIKI_RESULTS)
            
            if not search_results:
                logger.warning(f"No information found about '{query}' on Wikipedia")
                return f"No information found about {query} on Wikipedia."
            
            # Get the most relevant page
            page_title = search_results[0]
            logger.debug(f"Selected Wikipedia page: {page_title}")
            page = wikipedia.page(page_title)
            
            # Get summary
            return page.summary
            
        except wikipedia.exceptions.DisambiguationError as e:
            # If there are multiple pages, choose the first option
            logger.warning(f"Disambiguation error for '{query}'. Options: {e.options}")
            try:
                page = wikipedia.page(e.options[0])
                logger.debug(f"Selected first disambiguation option: {e.options[0]}")
                return page.summary
            except Exception as inner_e:
                logger.error(f"Error getting first disambiguation option: {str(inner_e)}")
                return f"No clear information found about {query}."
                
        except wikipedia.exceptions.PageError as e:
            logger.error(f"Wikipedia page error for '{query}': {str(e)}")
            return f"No Wikipedia page found about {query}."
            
        except Exception as e:
            logger.error(f"Error fetching Wikipedia info for '{query}': {str(e)}")
            return f"An error occurred while fetching information: {str(e)}"
    
    @staticmethod
    def search(query: str, language: str = DEFAULT_WIKI_LANGUAGE, results: int = DEFAULT_WIKI_RESULTS) -> List[str]:
        """
        Search Wikipedia for a query.
        
        Args:
            query: Search query
            language: Language code
            results: Number of results to return
            
        Returns:
            List of search results
        """
        logger.info(f"Searching Wikipedia for: {query} (language: {language}, results: {results})")
        try:
            WikiService.set_language(language)
            search_results = wikipedia.search(query, results=results)
            logger.debug(f"Found {len(search_results)} results for '{query}'")
            return search_results
        except Exception as e:
            logger.error(f"Wikipedia search error for '{query}': {str(e)}")
            return []
    
    @staticmethod
    def get_page(title: str, language: str = DEFAULT_WIKI_LANGUAGE) -> Optional[Dict[str, Any]]:
        """
        Get a Wikipedia page by title.
        
        Args:
            title: Page title
            language: Language code
            
        Returns:
            Dictionary with page content or None if not found
        """
        logger.info(f"Getting Wikipedia page: {title} (language: {language})")
        try:
            WikiService.set_language(language)
            page = wikipedia.page(title)
            logger.debug(f"Successfully retrieved page: {title}")
            return {
                "title": page.title,
                "summary": page.summary,
                "content": page.content,
                "url": page.url,
                "images": page.images,
                "categories": page.categories,
                "links": page.links,
                "references": page.references
            }
        except wikipedia.exceptions.PageError as e:
            logger.error(f"Wikipedia page error for '{title}': {str(e)}")
            return None
        except wikipedia.exceptions.DisambiguationError as e:
            logger.warning(f"Disambiguation error for '{title}'. Options: {e.options}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Wikipedia page '{title}': {str(e)}")
            return None
    
    @staticmethod
    def get_summary(title: str, language: str = DEFAULT_WIKI_LANGUAGE, sentences: int = 5) -> Optional[str]:
        """
        Get a summary of a Wikipedia page.
        
        Args:
            title: Page title
            language: Language code
            sentences: Number of sentences to include in the summary
            
        Returns:
            Summary text or None if not found
        """
        logger.info(f"Getting Wikipedia summary: {title} (language: {language}, sentences: {sentences})")
        try:
            WikiService.set_language(language)
            summary = wikipedia.summary(title, sentences=sentences)
            logger.debug(f"Successfully retrieved summary for: {title}")
            return summary
        except wikipedia.exceptions.PageError as e:
            logger.error(f"Wikipedia page error for '{title}': {str(e)}")
            return None
        except wikipedia.exceptions.DisambiguationError as e:
            logger.warning(f"Disambiguation error for '{title}'. Options: {e.options}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Wikipedia summary for '{title}': {str(e)}")
            return None