"""
Base classes for MCP tools.

This module provides the base classes for creating tools that can be used by
agentic characters through the Model Context Protocol (MCP).
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union

# Create a logger for this module
logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    This class defines the interface that all tools must implement.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the tool with a name and description.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
        """
        self.name = name
        self.description = description
        logger.debug(f"Initialized tool: {name}")
    
    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with the given arguments.
        
        Args:
            args: Dictionary of arguments for the tool
            
        Returns:
            Dictionary containing the results of the tool execution
        """
        pass
    
    def validate_args(self, args: Dict[str, Any], required_args: List[str]) -> Optional[Dict[str, Any]]:
        """
        Validate that all required arguments are present.
        
        Args:
            args: Dictionary of arguments to validate
            required_args: List of required argument names
            
        Returns:
            Error dictionary if validation fails, None if validation succeeds
        """
        logger.debug(f"Validating arguments for tool: {self.name}")
        
        for arg_name in required_args:
            if arg_name not in args:
                error_msg = f"Missing required argument: {arg_name}"
                logger.warning(f"Validation failed for {self.name}: {error_msg}")
                return {"error": error_msg}
        
        logger.debug(f"Arguments validated successfully for: {self.name}")
        return None
    
    def get_info(self) -> Dict[str, str]:
        """
        Get information about the tool.
        
        Returns:
            Dictionary containing tool information
        """
        return {
            "name": self.name,
            "description": self.description
        }
    
    def __str__(self) -> str:
        """
        Get a string representation of the tool.
        
        Returns:
            String representation
        """
        return f"{self.name}: {self.description}"


class MCPTool(BaseTool):
    """
    Base class for MCP tools.
    
    This class extends the BaseTool class with MCP-specific functionality.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the MCP tool.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
        """
        super().__init__(name, description)
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle an error that occurred during tool execution.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Error response dictionary
        """
        error_msg = str(error)
        logger.error(f"Error executing tool {self.name}: {error_msg}")
        return {"error": error_msg}
    
    def log_execution(self, args: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Log the execution of the tool.
        
        Args:
            args: The arguments that were passed to the tool
            result: The result of the tool execution
        """
        # Remove sensitive information from logs
        safe_args = args.copy()
        for key in safe_args:
            if "key" in key.lower() or "token" in key.lower() or "password" in key.lower():
                safe_args[key] = "***REDACTED***"
        
        # Log execution details
        logger.info(f"Executed tool: {self.name}")
        logger.debug(f"Tool {self.name} args: {safe_args}")
        
        # Log result summary (not the full result to avoid cluttering logs)
        if "error" in result:
            logger.warning(f"Tool {self.name} returned error: {result['error']}")
        else:
            result_keys = list(result.keys())
            logger.debug(f"Tool {self.name} returned keys: {result_keys}")


class DynamicTool(MCPTool):
    """
    Base class for dynamically created tools.
    
    This class extends the MCPTool class with functionality specific to
    dynamically created tools.
    """
    
    def __init__(self, name: str, description: str, created_at: Optional[str] = None):
        """
        Initialize the dynamic tool.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
            created_at: Timestamp when the tool was created
        """
        super().__init__(name, description)
        self.created_at = created_at
        self.dynamic = True
        logger.info(f"Initialized dynamic tool: {name}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the dynamic tool.
        
        Returns:
            Dictionary containing tool information
        """
        info = super().get_info()
        info.update({
            "dynamic": True,
            "created_at": self.created_at
        })
        return info