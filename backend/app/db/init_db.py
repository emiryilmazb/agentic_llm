"""
Database initialization and migration utilities.
"""
import json
import os
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.config import settings
from app.db.base import engine, Base
from app.db.models.character import Character
from app.db.models.conversation import Conversation

def create_tables() -> None:
    """Create all database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    
def migrate_chat_history(db: Session) -> int:
    """
    Migrate existing chat history from Character model to Conversation model.
    
    Args:
        db: Database session
        
    Returns:
        Number of conversations created
    """
    conversations_created = 0
    
    # Get all characters with chat history
    characters = db.query(Character).all()
    print(f"Found {len(characters)} characters to check for chat history migration")
    
    for character in characters:
        try:
            # Get the character data as a dictionary
            character_dict = character.to_dict()
            
            # Check if this is a pre-migration character that had chat_history
            # We need to use __dict__ to access the attribute directly since it's been removed from to_dict()
            if hasattr(character, 'chat_history') and character.chat_history and len(character.chat_history) > 0:
                chat_history = character.chat_history
                
                # Create a new conversation with the existing chat history
                conversation = Conversation(
                    character_id=character.id,
                    title=f"Previous Conversation ({datetime.now().strftime('%Y-%m-%d')})",
                    chat_history=chat_history
                )
                
                db.add(conversation)
                conversations_created += 1
                print(f"Migrated chat history for character '{character.name}' to a new conversation")
                
                # Reset the chat history on the character model 
                # (This will be ignored after model update but helps with the transition)
                character.chat_history = []
                
            else:
                print(f"No chat history found for character '{character.name}', skipping")
                
        except Exception as e:
            print(f"Error migrating chat history for character {character.name}: {e}")
    
    # Commit all changes
    db.commit()
    print(f"Migration complete. {conversations_created} conversations created from existing chat history.")
    return conversations_created

def migrate_character_data(db: Session) -> int:
    """
    Migrate existing character data from JSON files to the database.
    
    Args:
        db: Database session
        
    Returns:
        Number of characters migrated
    """
    characters_migrated = 0
    
    # Skip migration if the character_data directory doesn't exist
    if not settings.DATA_DIR.exists() or not settings.DATA_DIR.is_dir():
        print(f"Character data directory not found: {settings.DATA_DIR}")
        return characters_migrated
    
    # Get all JSON files in the character_data directory
    json_files = list(settings.DATA_DIR.glob("*.json"))
    print(f"Found {len(json_files)} character files to migrate")
    
    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                character_data = json.load(f)
            
            # Check if character already exists in database
            existing = db.query(Character).filter(Character.name == character_data["name"]).first()
            if existing:
                print(f"Character '{character_data['name']}' already exists in database, skipping")
                continue
            
            # Create new character record
            character = Character.from_dict(character_data)
            db.add(character)
            characters_migrated += 1
            print(f"Migrated character: {character_data['name']}")
            
        except Exception as e:
            print(f"Error migrating character from {file_path}: {e}")
    
    # Commit all changes
    db.commit()
    print(f"Migration complete. {characters_migrated} characters migrated to database.")
    return characters_migrated
