"""
Wikipedia service for fetching information about characters.
"""
import wikipedia
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path

# Add parent directory to sys.path for relative imports
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings

class WikiService:
    """Service class for handling Wikipedia interactions."""
    
    @staticmethod
    def fetch_info(query: str, language: str = None, results_count: int = None) -> Optional[str]:
        """
        Fetch information from Wikipedia for a given query.
        
        Args:
            query: Search query string
            language: Wikipedia language (e.g., 'en', 'tr', defaults to settings.DEFAULT_WIKI_LANGUAGE)
            results_count: Number of search results to return (defaults to settings.DEFAULT_WIKI_RESULTS)
            
        Returns:
            Wikipedia summary or None if not found
        """
        try:
            # Set language
            wikipedia.set_lang(language or settings.DEFAULT_WIKI_LANGUAGE)
            
            # Search for pages
            search_results = wikipedia.search(
                query, 
                results=results_count or settings.DEFAULT_WIKI_RESULTS
            )
            
            if not search_results:
                print(f"No Wikipedia results found for '{query}'")
                return None
            
            # Try to get the first result page
            try:
                page = wikipedia.page(search_results[0])
                return page.summary
            except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError) as e:
                # Handle disambiguation pages or page errors
                if isinstance(e, wikipedia.exceptions.DisambiguationError):
                    # If it's a disambiguation page, try the first option
                    try:
                        page = wikipedia.page(e.options[0])
                        return page.summary
                    except Exception as inner_e:
                        print(f"Error getting first disambiguation option: {inner_e}")
                        return None
                else:
                    print(f"Page error for '{query}': {e}")
                    return None
        except Exception as e:
            print(f"Error fetching Wikipedia info for '{query}': {e}")
            return None
    
    @staticmethod
    def search(query: str, language: str = None, results_count: int = None) -> List[str]:
        """
        Search Wikipedia for a given query.
        
        Args:
            query: Search query string
            language: Wikipedia language (e.g., 'en', 'tr', defaults to settings.DEFAULT_WIKI_LANGUAGE)
            results_count: Number of search results to return (defaults to settings.DEFAULT_WIKI_RESULTS)
            
        Returns:
            List of search result titles
        """
        try:
            # Set language
            wikipedia.set_lang(language or settings.DEFAULT_WIKI_LANGUAGE)
            
            # Search for pages
            return wikipedia.search(
                query, 
                results=results_count or settings.DEFAULT_WIKI_RESULTS
            )
        except Exception as e:
            print(f"Error searching Wikipedia for '{query}': {e}")
            return []
    
    @staticmethod
    def get_page_details(title: str, language: str = None) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific Wikipedia page.
        
        Args:
            title: Page title
            language: Wikipedia language (e.g., 'en', 'tr', defaults to settings.DEFAULT_WIKI_LANGUAGE)
            
        Returns:
            Dictionary containing page details or None if not found
        """
        try:
            # Set language
            wikipedia.set_lang(language or settings.DEFAULT_WIKI_LANGUAGE)
            
            # Get page
            page = wikipedia.page(title)
            
            return {
                "title": page.title,
                "summary": page.summary,
                "content": page.content,
                "url": page.url,
                "categories": page.categories,
                "links": page.links,
                "references": page.references,
                "images": page.images
            }
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"Disambiguation error for '{title}': {e}")
            return {
                "error": "disambiguation",
                "options": e.options
            }
        except wikipedia.exceptions.PageError as e:
            print(f"Page error for '{title}': {e}")
            return None
        except Exception as e:
            print(f"Error getting Wikipedia page details for '{title}': {e}")
            return None
