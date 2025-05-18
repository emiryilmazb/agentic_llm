"""
Conversation service for handling conversation-related operations.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models.conversation import Conversation
from app.db.models.character import Character

class ConversationService:
    """Service class for handling conversation operations."""
    
    @staticmethod
    def create_conversation(db: Session, character_name: str, title: str = "New Conversation") -> Optional[Dict[str, Any]]:
        """
        Create a new conversation for a character.
        
        Args:
            db: Database session
            character_name: Name of the character for this conversation
            title: Optional title for the conversation
            
        Returns:
            Conversation data dictionary or None if character not found
        """
        # Find the character
        character = db.query(Character).filter(Character.name == character_name).first()
        if not character:
            return None
        
        # Create new conversation
        conversation = Conversation(
            character_id=character.id,
            title=title,
            chat_history=[]
        )
        
        # Add to database
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return conversation.to_dict()
    
    @staticmethod
    def get_conversation(db: Session, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID.
        
        Args:
            db: Database session
            conversation_id: ID of the conversation to get
            
        Returns:
            Conversation data dictionary or None if not found
        """
        print(f"DEBUG: ConversationService.get_conversation called with ID: {conversation_id}")
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            print(f"DEBUG: Conversation with ID {conversation_id} not found in DB.")
            return None
        
        print(f"DEBUG: Conversation with ID {conversation_id} found in DB.")
        return conversation.to_dict()
    
    @staticmethod
    def get_conversations_by_character(db: Session, character_name: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all conversations for a specific character.
        
        Args:
            db: Database session
            character_name: Name of the character
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
            
        Returns:
            List of conversation data dictionaries
        """
        # Get character ID
        character = db.query(Character).filter(Character.name == character_name).first()
        if not character:
            return []
        
        # Get conversations for character
        conversations = db.query(Conversation).filter(
            Conversation.character_id == character.id
        ).order_by(
            desc(Conversation.updated_at)
        ).offset(offset).limit(limit).all()
        
        return [conversation.to_dict() for conversation in conversations]
    
    @staticmethod
    def get_all_conversations(db: Session, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all conversations with optional pagination.
        
        Args:
            db: Database session
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
            
        Returns:
            List of conversation data dictionaries
        """
        conversations = db.query(Conversation).order_by(
            desc(Conversation.updated_at)
        ).offset(offset).limit(limit).all()
        
        return [conversation.to_dict() for conversation in conversations]
    
    @staticmethod
    def update_conversation(db: Session, conversation_id: int, title: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a conversation's title.
        
        Args:
            db: Database session
            conversation_id: ID of the conversation to update
            title: New title for the conversation
            
        Returns:
            Updated conversation data dictionary or None if not found
        """
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return None
        
        if title is not None:
            conversation.title = title
        
        db.commit()
        db.refresh(conversation)
        
        return conversation.to_dict()
    
    @staticmethod
    def delete_conversation(db: Session, conversation_id: int) -> bool:
        """
        Delete a conversation.
        
        Args:
            db: Database session
            conversation_id: ID of the conversation to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return False
        
        db.delete(conversation)
        db.commit()
        
        return True
    
    @staticmethod
    def update_chat_history(db: Session, conversation_id: int, user_message: str, assistant_message: str) -> Optional[Dict[str, Any]]:
        """
        Add messages to a conversation's chat history.
        
        Args:
            db: Database session
            conversation_id: ID of the conversation
            user_message: Message from the user
            assistant_message: Response from the assistant
            
        Returns:
            Updated conversation data dictionary or None if not found
        """
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return None
        
        # Get current history or initialize empty list
        history = conversation.chat_history or []
        
        # Add messages
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": assistant_message})
        
        # Update conversation
        conversation.chat_history = history
        db.commit()
        db.refresh(conversation)
        
        return conversation.to_dict()
    
    @staticmethod
    def clear_chat_history(db: Session, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        Clear a conversation's chat history.
        
        Args:
            db: Database session
            conversation_id: ID of the conversation
            
        Returns:
            Updated conversation data dictionary or None if not found
        """
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return None
        
        conversation.chat_history = []
        db.commit()
        db.refresh(conversation)
        
        return conversation.to_dict()
    
    @staticmethod
    def get_character_for_conversation(db: Session, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the character associated with a conversation.
        
        Args:
            db: Database session
            conversation_id: ID of the conversation
            
        Returns:
            Character data dictionary or None if conversation not found
        """
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation or not conversation.character:
            return None
        
        return conversation.character.to_dict()
    
    @staticmethod
    def format_chat_history(chat_history: List[Dict[str, str]], character_name: str, max_messages: int = 10) -> str:
        """
        Format chat history for inclusion in prompts.
        
        Args:
            chat_history: List of chat message dictionaries
            character_name: Name of the character
            max_messages: Maximum number of messages to include
            
        Returns:
            Formatted chat history text
        """
        history_text = ""
        if chat_history:
            # Include last N messages for context
            for msg in chat_history[-max_messages:]:
                if msg["role"] == "user":
                    history_text += f"Kullanıcı: {msg['content']}\n"
                else:
                    history_text += f"{character_name}: {msg['content']}\n"
        return history_text
