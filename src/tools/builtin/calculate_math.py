"""
Mathematical calculation tool implementation.

This module provides a tool for evaluating mathematical expressions.
"""
import logging
import re
from typing import Dict, Any, Optional

from src.tools.base import MCPTool

# Create a logger for this module
logger = logging.getLogger(__name__)

class CalculateMath(MCPTool):
    """
    Tool to evaluate mathematical expressions.
    
    This tool allows characters to evaluate mathematical expressions
    safely and return the results.
    """
    
    def __init__(self):
        """Initialize the math calculation tool."""
        super().__init__(
            name="calculate_math",
            description="Evaluates a mathematical expression"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the math calculation tool.
        
        Args:
            args: Dictionary containing the following keys:
                - expression: The mathematical expression to evaluate (required)
        
        Returns:
            Dictionary containing the calculation result
        """
        # Validate required arguments
        validation_error = self.validate_args(args, ["expression"])
        if validation_error:
            return validation_error
        
        # Extract arguments
        expression = args.get("expression", "")
        
        logger.info(f"Calculating expression: {expression}")
        
        try:
            # Basic validation to prevent code execution
            if not self._is_safe_expression(expression):
                error_msg = "Invalid characters in expression. Only numbers, basic operators, parentheses, and decimal points are allowed."
                logger.warning(f"Unsafe expression: {expression}")
                return {"error": error_msg}
            
            # Evaluate the expression
            result = self._safe_eval(expression)
            
            logger.debug(f"Calculation result: {result}")
            
            # Return the result
            return {
                "expression": expression,
                "result": result,
                "status": "success"
            }
        except Exception as e:
            error_msg = f"Error evaluating expression: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.handle_error(e)
    
    def _is_safe_expression(self, expression: str) -> bool:
        """
        Check if an expression is safe to evaluate.
        
        Args:
            expression: The expression to check
            
        Returns:
            True if the expression is safe, False otherwise
        """
        # Only allow numbers, basic operators, parentheses, and decimal points
        return bool(re.match(r'^[0-9+\-*/().%\s]+$', expression))
    
    def _safe_eval(self, expression: str) -> float:
        """
        Safely evaluate a mathematical expression.
        
        Args:
            expression: The expression to evaluate
            
        Returns:
            The result of the evaluation
            
        Raises:
            ValueError: If the expression is invalid
            ZeroDivisionError: If the expression involves division by zero
        """
        # Replace % with * 0.01 * for percentage calculations
        expression = expression.replace('%', '* 0.01 *')
        
        # Evaluate the expression
        try:
            # Using eval for demonstration - in production, use a safer alternative like ast.literal_eval
            # or a dedicated math expression parser
            result = eval(expression)
            return result
        except SyntaxError:
            raise ValueError("Invalid syntax in expression")
        except ZeroDivisionError:
            raise ZeroDivisionError("Division by zero")
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {str(e)}")