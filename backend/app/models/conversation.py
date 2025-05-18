"""
Pydantic models for conversation functionality.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class ConversationBase(BaseModel):
    """Base model for conversation data."""
    title: str = Field(default="New Conversation", description="Title of the conversation")

class ConversationCreate(ConversationBase):
    """Model for creating a new conversation."""
    character_name: str = Field(..., description="Name of the character for this conversation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character_name": "Sherlock Holmes",
                "title": "The Case of the Missing Keys"
            }
        }

class ConversationUpdate(ConversationBase):
    """Model for updating a conversation."""
    title: Optional[str] = Field(None, description="New title for the conversation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "The Adventure of the Blue Carbuncle"
            }
        }

class ConversationResponse(ConversationBase):
    """Model for conversation responses."""
    id: int = Field(..., description="Conversation ID")
    character_id: int = Field(..., description="ID of the character")
    character_name: str = Field(..., description="Name of the character")
    chat_history: List[Dict[str, Any]] = Field(default=[], description="Conversation history")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "character_id": 2,
                "character_name": "Sherlock Holmes",
                "title": "The Case of the Missing Keys",
                "chat_history": [
                    {"role": "user", "content": "Hello, can you help me solve a mystery?"},
                    {"role": "assistant", "content": "Indeed, I would be delighted to assist you. What are the particulars of your case?"}
                ],
                "created_at": "2025-05-17T12:34:56.789Z",
                "updated_at": "2025-05-17T13:45:12.345Z"
            }
        }

class ConversationList(BaseModel):
    """Model for returning lists of conversations."""
    conversations: List[ConversationResponse] = Field(..., description="List of conversations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversations": [
                    {
                        "id": 1,
                        "character_id": 2,
                        "character_name": "Sherlock Holmes",
                        "title": "The Case of the Missing Keys",
                        "chat_history": [],
                        "created_at": "2025-05-17T12:34:56.789Z",
                        "updated_at": "2025-05-17T13:45:12.345Z"
                    },
                    {
                        "id": 2,
                        "character_id": 2,
                        "character_name": "Sherlock Holmes",
                        "title": "The Mystery of the Stolen Painting",
                        "chat_history": [],
                        "created_at": "2025-05-18T09:12:34.567Z",
                        "updated_at": "2025-05-18T09:12:34.567Z"
                    }
                ]
            }
        }
