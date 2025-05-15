"""
Current time tool implementation.

This module provides a tool for getting the current date and time.
"""
import logging
import datetime
from typing import Dict, Any, Optional

from src.tools.base import MCPTool

# Create a logger for this module
logger = logging.getLogger(__name__)

class GetCurrentTime(MCPTool):
    """
    Tool to get the current date and time.
    
    This tool allows characters to get the current date and time,
    optionally in a specific format or timezone.
    """
    
    def __init__(self):
        """Initialize the current time tool."""
        super().__init__(
            name="get_current_time",
            description="Returns the current date and time"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the current time tool.
        
        Args:
            args: Dictionary containing the following keys:
                - timezone: The timezone to use (optional, default: 'Europe/Istanbul')
                - format: The format string for the date/time (optional, default: '%Y-%m-%d %H:%M:%S')
        
        Returns:
            Dictionary containing the current time information
        """
        logger.info("Executing get_current_time tool")
        
        try:
            # Extract arguments
            timezone = args.get("timezone", "Europe/Istanbul")
            format_str = args.get("format", "%Y-%m-%d %H:%M:%S")
            
            # Get current time
            now = datetime.datetime.now()
            formatted_time = now.strftime(format_str)
            
            logger.debug(f"Current time: {formatted_time} (timezone: {timezone})")
            
            # Return the result
            return {
                "current_time": formatted_time,
                "timezone": timezone,
                "timestamp": now.timestamp(),
                "iso_format": now.isoformat(),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error getting current time: {str(e)}", exc_info=True)
            return self.handle_error(e)