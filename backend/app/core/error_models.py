"""
Standard error models for API responses.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union

class ErrorDetail(BaseModel):
    """Model for detailed error information."""
    loc: Optional[List[str]] = Field(None, description="Error location")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")

class ErrorResponse(BaseModel):
    """Standard error response model."""
    status: str = Field("error", description="Response status")
    message: str = Field(..., description="Error message")
    details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = Field(
        None, description="Additional error details"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Validation error",
                "details": [
                    {
                        "loc": ["body", "name"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            }
        }

class ValidationErrorResponse(ErrorResponse):
    """Validation error response model."""
    message: str = Field("Validation error", description="Error message")
    details: List[ErrorDetail] = Field(..., description="Validation error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Validation error",
                "details": [
                    {
                        "loc": ["body", "name"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            }
        }

class NotFoundErrorResponse(ErrorResponse):
    """Not found error response model."""
    message: str = Field(..., description="Error message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Character 'Sherlock Holmes' not found",
                "details": None
            }
        }
