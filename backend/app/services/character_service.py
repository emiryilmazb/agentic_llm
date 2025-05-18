"""
Character service for handling character data operations.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.character import Character

class CharacterService:
    """Service class for handling character data operations."""
    
    @staticmethod
    def create_prompt(name: str, background: str, personality: str, wiki_info: Optional[str] = None) -> str:
        """
        Create a system prompt for a character.
        
        Args:
            name: Character name
            background: Character background information
            personality: Character personality traits
            wiki_info: Optional Wikipedia information about the character
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Sen {name} karakterisin. Aşağıdaki bilgilere göre davran ve cevap ver:

Karakter Özellikleri:
{personality}

Geçmiş Bilgisi:
{background}
"""
        if wiki_info:
            prompt += f"""
Wikipedia'dan elde edilen bilgiler:
{wiki_info}

Bu bilgilere dayanarak, {name} olarak cevap ver. İlk şahıs olarak konuş ve karakterin kişiliğini yansıt.
"""
        return prompt

    @staticmethod
    def save_character(db: Session,
                      name: str, 
                      background: str, 
                      personality: str, 
                      prompt: str, 
                      wiki_info: Optional[str] = None, 
                      use_agentic: bool = False) -> Character:
        """
        Save character data to the database.
        
        Args:
            db: Database session
            name: Character name
            background: Character background
            personality: Character personality
            prompt: System prompt for the character
            wiki_info: Wikipedia information
            use_agentic: Whether to use agentic capabilities
            
        Returns:
            Created Character model instance
        """
        # Create character model
        character = Character(
            name=name,
            background=background,
            personality=personality,
            prompt=prompt,
            wiki_info=wiki_info,
            use_agentic=use_agentic
        )
        
        # Add to database
        db.add(character)
        db.commit()
        db.refresh(character)
        
        return character

    @staticmethod
    def load_character(db: Session, name: str) -> Optional[Dict[str, Any]]:
        """
        Load a character from the database.
        
        Args:
            db: Database session
            name: Name of the character to load
            
        Returns:
            Character data dictionary or None if not found
        """
        character = db.query(Character).filter(Character.name == name).first()
        if not character:
            return None
        
        return character.to_dict()

    @staticmethod
    def get_all_characters(db: Session) -> List[str]:
        """
        List all saved characters.
        
        Args:
            db: Database session
            
        Returns:
            List of character names
        """
        characters = db.query(Character.name).all()
        return [character[0] for character in characters]

    @staticmethod
    def delete_character(db: Session, name: str) -> bool:
        """
        Delete a character by name.
        
        Args:
            db: Database session
            name: Name of the character to delete
            
        Returns:
            True if successful, False otherwise
        """
        character = db.query(Character).filter(Character.name == name).first()
        if not character:
            return False
        
        db.delete(character)
        db.commit()
        return True

    @staticmethod
    def save_character_data(db: Session, character_name: str, character_data: Dict[str, Any]) -> None:
        """
        Update character data in the database.
        
        Args:
            db: Database session
            character_name: Name of the character
            character_data: Character data dictionary to save
        """
        character = db.query(Character).filter(Character.name == character_name).first()
        if not character:
            return
        
        # Update fields
        character.personality = character_data.get("personality", character.personality)
        character.background = character_data.get("background", character.background)
        character.prompt = character_data.get("prompt", character.prompt)
        character.wiki_info = character_data.get("wiki_info", character.wiki_info)
        character.use_agentic = character_data.get("use_agentic", character.use_agentic)
        character.chat_history = character_data.get("chat_history", character.chat_history)
        
        # Save changes
        db.commit()
    
    @staticmethod
    def format_chat_history(chat_history: List[Dict[str, str]], character_name: str) -> str:
        """
        Format chat history for inclusion in prompts.
        
        Args:
            chat_history: List of chat message dictionaries
            character_name: Name of the character
            
        Returns:
            Formatted chat history text
        """
        history_text = ""
        if chat_history:
            # Include last N messages for context based on configuration
            for msg in chat_history[-settings.MAX_HISTORY_MESSAGES:]:
                if msg["role"] == "user":
                    history_text += f"Kullanıcı: {msg['content']}\n"
                else:
                    history_text += f"{character_name}: {msg['content']}\n"
        return history_text
