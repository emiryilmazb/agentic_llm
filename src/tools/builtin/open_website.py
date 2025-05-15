"""
Website opening tool implementation.

This module provides a tool for opening websites in a browser.
"""
import logging
import re
import webbrowser
from typing import Dict, Any, Optional

from src.tools.base import MCPTool

# Create a logger for this module
logger = logging.getLogger(__name__)

class OpenWebsite(MCPTool):
    """
    Tool to open a website in the browser.
    
    This tool allows characters to open specified URLs in the user's browser.
    """
    
    def __init__(self):
        """Initialize the website opening tool."""
        super().__init__(
            name="open_website",
            description="Opens a specified URL in the browser"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the website opening tool.
        
        Args:
            args: Dictionary containing the following keys:
                - url: The URL to open (required)
        
        Returns:
            Dictionary containing the status of the operation
        """
        # Validate required arguments
        validation_error = self.validate_args(args, ["url"])
        if validation_error:
            return validation_error
        
        # Extract arguments
        url = args.get("url", "")
        
        logger.info(f"Opening website: {url}")
        
        try:
            # Validate URL format
            if not self._is_valid_url(url):
                # Try to fix the URL by adding https:// if missing
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                    logger.debug(f"Added https:// prefix to URL: {url}")
                
                # Check again after fixing
                if not self._is_valid_url(url):
                    error_msg = "Invalid URL format"
                    logger.warning(f"Invalid URL: {url}")
                    return {"error": error_msg}
            
            # Open the URL in the browser
            webbrowser.open(url)
            
            logger.debug(f"Successfully opened URL: {url}")
            
            # Return success status
            return {
                "status": "success",
                "message": f"Opened {url} in browser",
                "url": url
            }
        except Exception as e:
            error_msg = f"Error opening website: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.handle_error(e)
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is valid.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL is valid, False otherwise
        """
        # Basic URL validation
        # This is a simplified version - a production version would use a more robust validation
        if not url:
            return False
        
        # Check if the URL starts with http:// or https://
        if not url.startswith(("http://", "https://")):
            return False
        
        # Check for basic domain format
        domain_pattern = r'^https?://([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(/.*)?$'
        return bool(re.match(domain_pattern, url))