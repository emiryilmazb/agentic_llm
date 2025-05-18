"""
SQLAlchemy ORM model for Character entity.
"""
import json
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import mapped_column, relationship
from typing import List, Dict, Any, Optional

from app.db.base import Base

class JSONEncodedDict(TypeDecorator):
    """
    Represents a JSON-encoded value as a Text column.
    """
    impl = Text
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)

class Character(Base):
    """SQLAlchemy ORM model for characters."""
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    personality = Column(Text, nullable=False)
    background = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)
    wiki_info = Column(Text, nullable=True)
    use_agentic = Column(Boolean, default=False)
    
    # Timestamp fields for tracking creation and updates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to conversations
    conversations = relationship("Conversation", back_populates="character", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary for API responses.
        
        Returns:
            Dict: Dictionary with character data
        """
        return {
            "id": self.id,
            "name": self.name,
            "personality": self.personality,
            "background": self.background,
            "prompt": self.prompt,
            "wiki_info": self.wiki_info,
            "use_agentic": self.use_agentic,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        """
        Create a Character model from a dictionary.
        
        Args:
            data: Dictionary with character data
            
        Returns:
            Character: ORM model instance
        """
        return cls(
            name=data.get("name"),
            personality=data.get("personality"),
            background=data.get("background"),
            prompt=data.get("prompt"),
            wiki_info=data.get("wiki_info"),
            use_agentic=data.get("use_agentic", False)
        )
