"""
Wikipedia service utilities for fetching information from Wikipedia.
"""
import wikipedia
from typing import Optional, List, Dict, Any

from utils.config import DEFAULT_WIKI_LANGUAGE, DEFAULT_WIKI_RESULTS

class WikiService:
    """Service class for handling Wikipedia interactions."""
    
    @staticmethod
    def set_language(language: str = DEFAULT_WIKI_LANGUAGE) -> None:
        """
        Set the language for Wikipedia searches.
        
        Args:
            language: Language code (e.g., 'tr' for Turkish)
        """
        wikipedia.set_lang(language)
    
    @staticmethod
    def fetch_info(character_name: str, language: str = DEFAULT_WIKI_LANGUAGE) -> str:
        """
        Fetch information about a character from Wikipedia.
        
        Args:
            character_name: Name of the character to search for
            language: Language code (e.g., 'tr' for Turkish)
            
        Returns:
            Summary text from Wikipedia or error message
        """
        try:
            # Set language
            WikiService.set_language(language)
            
            # Search for the character with configured number of results
            search_results = wikipedia.search(character_name, results=DEFAULT_WIKI_RESULTS)
            
            if not search_results:
                return f"No information found about {character_name} on Wikipedia."
            
            # Get the most relevant page
            page_title = search_results[0]
            page = wikipedia.page(page_title)
            
            # Get summary
            return page.summary
            
        except wikipedia.exceptions.DisambiguationError as e:
            # If there are multiple pages, choose the first option
            try:
                page = wikipedia.page(e.options[0])
                return page.summary
            except:
                return f"No clear information found about {character_name}."
                
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found about {character_name}."
            
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
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
        try:
            WikiService.set_language(language)
            return wikipedia.search(query, results=results)
        except Exception as e:
            print(f"Wikipedia search error: {str(e)}")
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
        try:
            WikiService.set_language(language)
            page = wikipedia.page(title)
            return {
                "title": page.title,
                "summary": page.summary,
                "content": page.content,
                "url": page.url
            }
        except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError):
            return None
        except Exception as e:
            print(f"Error fetching Wikipedia page: {str(e)}")
            return None
