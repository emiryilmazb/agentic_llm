"""
Character name suggestion service.
"""
import time
from typing import List, Optional, Dict, Tuple
from utils.ai_service import AIService

class SuggestionService:
    """Service class for character name suggestions."""
    
    # Suggestion cache - {searched_name: (suggestions, timestamp)}
    _suggestion_cache: Dict[str, Tuple[List[str], float]] = {}
    
    # Cache duration (seconds)
    _cache_duration = 3600  # 1 hour
    
    @classmethod
    def get_character_name_suggestions(cls, partial_name: str, limit: int = 5) -> List[str]:
        """
        Get character name suggestions based on the given partial name.
        
        Args:
            partial_name: Partial name entered by the user
            limit: Maximum number of suggestions
            
        Returns:
            List of character name suggestions
        """
        if not partial_name or len(partial_name) < 2:
            return []
        
        # Clean expired cache entries
        cls._clean_expired_cache()
        
        # Search in cache
        cache_key = partial_name.lower()
        if cache_key in cls._suggestion_cache:
            suggestions, _ = cls._suggestion_cache[cache_key]
            return suggestions[:limit]  # Return suggestions up to the limit
            
        prompt = f"""
        The user has started typing a character name: "{partial_name}"
        
        Suggest {limit} popular characters, historical figures, or famous names that match this beginning.
        Return only the names as a list, without any additional explanation.
        Suggestions may include:
        - Characters from movies, TV shows, books
        - Historical figures
        - Celebrities
        - Mythological characters
        
        Return suggestions in the following format (names only):
        name1
        name2
        name3
        """
        
        try:
            response = AIService.generate_response(
                prompt=prompt,
                temperature=0.7,
                max_tokens=150
            )
            
            # Process the response and return as a list
            suggestions = [name.strip() for name in response.split('\n') if name.strip()]
            suggestions = suggestions[:limit]  # Return suggestions up to the limit
            
            # Add to cache
            cls._suggestion_cache[cache_key] = (suggestions, time.time())
            
            return suggestions
        except Exception as e:
            print(f"Error getting suggestions: {str(e)}")
            return []
    
    @classmethod
    def _clean_expired_cache(cls):
        """Clean expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        for key, (_, timestamp) in cls._suggestion_cache.items():
            if current_time - timestamp > cls._cache_duration:
                expired_keys.append(key)
                
        for key in expired_keys:
            del cls._suggestion_cache[key]
    
    @classmethod
    def clear_cache(cls):
        """Clear all cache."""
        cls._suggestion_cache.clear()
