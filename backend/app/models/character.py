"""
Pydantic models for character data.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class CharacterBase(BaseModel):
    """Base model with common character attributes."""
    name: str = Field(..., description="Character name")
    personality: str = Field(..., description="Character personality traits")
    background: Optional[str] = Field(None, description="Character background information")

class CharacterCreate(CharacterBase):
    """Model for creating a new character."""
    use_wiki: bool = Field(False, description="Whether to fetch information from Wikipedia")
    use_agentic: bool = Field(True, description="Whether to enable agentic capabilities")

class CharacterResponse(CharacterBase):
    """Model for character response data."""
    prompt: str = Field(..., description="System prompt for the character")
    wiki_info: Optional[str] = Field(None, description="Wikipedia information")
    use_agentic: bool = Field(False, description="Whether agentic capabilities are enabled")
    chat_history: List[Dict[str, Any]] = Field([], description="Chat history")
    created_at: Optional[str] = Field(None, description="Timestamp when character was created")
    updated_at: Optional[str] = Field(None, description="Timestamp when character was last updated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sherlock Holmes",
                "personality": "Brilliant detective with exceptional analytical skills.",
                "background": "Famous detective from London, created by Sir Arthur Conan Doyle.",
                "prompt": "You are Sherlock Holmes, the world's most famous detective...",
                "wiki_info": "Sherlock Holmes is a fictional detective created by British author Sir Arthur Conan Doyle...",
                "use_agentic": True,
                "chat_history": [
                    {"role": "user", "content": "Hello, can you help me solve a mystery?"},
                    {"role": "assistant", "content": "Indeed, I would be delighted to assist you. What are the particulars of your case?"}
                ],
                "created_at": "2025-05-18T04:30:00",
                "updated_at": "2025-05-18T04:45:00"
            }
        }

class CharacterList(BaseModel):
    """Model for a list of characters."""
    characters: List[str] = Field(..., description="List of character names")
    
    class Config:
        json_schema_extra = {
            "example": {
                "characters": ["Sherlock Holmes", "Albert Einstein", "Marie Curie"]
            }
        }
