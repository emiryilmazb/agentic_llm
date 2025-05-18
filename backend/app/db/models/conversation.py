"""
SQLAlchemy ORM model for Conversation entity.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from typing import Dict, Any, List

from app.db.base import Base
from app.db.models.character import JSONEncodedDict

class Conversation(Base):
    """SQLAlchemy ORM model for conversations."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    title = Column(String(255), nullable=False, default="New Conversation")
    chat_history = Column(JSONEncodedDict, default=lambda: "[]")  # Stored as JSON string
    
    # Timestamp fields for tracking creation and updates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    character = relationship("Character", back_populates="conversations")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary for API responses.
        
        Returns:
            Dict: Dictionary with conversation data
        """
        return {
            "id": self.id,
            "character_id": self.character_id,
            "character_name": self.character.name if self.character else None,
            "title": self.title,
            "chat_history": self.chat_history or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """
        Create a Conversation model from a dictionary.
        
        Args:
            data: Dictionary with conversation data
            
        Returns:
            Conversation: ORM model instance
        """
        return cls(
            character_id=data.get("character_id"),
            title=data.get("title", "New Conversation"),
            chat_history=data.get("chat_history", [])
        )
