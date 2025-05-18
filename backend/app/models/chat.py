"""
Pydantic models for chat functionality.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from fastapi.responses import StreamingResponse

class ChatMessage(BaseModel):
    """Model for user chat messages."""
    message: str = Field(..., description="User message content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, how are you today?"
            }
        }

class ChatResponse(BaseModel):
    """Model for character responses."""
    character: str = Field(..., description="Name of the character responding")
    message: str = Field(..., description="Character's response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data (for agentic responses)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character": "Sherlock Holmes",
                "message": "I am quite well, thank you. How may I be of assistance today?",
                "data": {
                    "type": "text",
                    "content": "I am quite well, thank you. How may I be of assistance today?",
                    "display_text": "I am quite well, thank you. How may I be of assistance today?"
                }
            }
        }

class ChatHistoryResponse(BaseModel):
    """Model for chat history responses."""
    character: str = Field(..., description="Name of the character")
    history: List[Dict[str, Any]] = Field(..., description="Chat history messages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character": "Sherlock Holmes",
                "history": [
                    {"role": "user", "content": "Hello, can you help me solve a mystery?"},
                    {"role": "assistant", "content": "Indeed, I would be delighted to assist you. What are the particulars of your case?"},
                    {"role": "user", "content": "I've lost my keys and can't find them anywhere."},
                    {"role": "assistant", "content": "A curious case. Let me think... Have you checked the last place you distinctly remember having them? Often the most obvious locations are overlooked."}
                ]
            }
        }

# For streaming responses
class StreamingChatResponse:
    """
    A utility class to handle streaming chat responses.
    
    This is not a Pydantic model but a helper class that creates a FastAPI StreamingResponse
    with the correct media type and content generator.
    """
    
    @staticmethod
    def create(content_generator):
        """
        Create a FastAPI StreamingResponse for chat content.
        
        Args:
            content_generator: An async generator that yields chunks of response
            
        Returns:
            A configured StreamingResponse
        """
        return StreamingResponse(
            content_generator,
            media_type="text/event-stream"
        )
