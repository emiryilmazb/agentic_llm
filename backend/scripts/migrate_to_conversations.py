"""
Migration script to convert existing character chat history to the new Conversation model.

This script should be run after database schema updates to ensure no data is lost.
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def main():
    """
    Run the migration from Character chat_history to Conversation model.
    """
    print("Starting migration to separate character and chat history data...")
    
    try:
        # Import database models and services
        from app.db.base import engine, Base, SessionLocal
        from app.db.models.character import Character
        from app.db.models.conversation import Conversation
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("Database schema updated")
        
        # Create a database session
        db = SessionLocal()
        
        try:
            # Get all characters
            characters = db.query(Character).all()
            print(f"Found {len(characters)} characters to check for chat history migration")
            
            conversations_created = 0
            
            # For each character, check if it has chat history
            for character in characters:
                try:
                    # Check if the character has chat history attribute
                    # We need __dict__ because the to_dict method might not include the field anymore
                    if hasattr(character, 'chat_history') and character.chat_history and len(character.chat_history) > 0:
                        chat_history = character.chat_history
                        
                        # Create a new conversation with the character's chat history
                        conversation = Conversation(
                            character_id=character.id,
                            title=f"Previous Conversation ({datetime.now().strftime('%Y-%m-%d')})",
                            chat_history=chat_history
                        )
                        
                        db.add(conversation)
                        conversations_created += 1
                        print(f"Migrated chat history for character '{character.name}' to a new conversation")
                    else:
                        print(f"No chat history found for character '{character.name}', skipping")
                        
                except Exception as e:
                    print(f"Error migrating chat history for character {character.name}: {e}")
            
            # Commit all changes
            db.commit()
            
            print(f"Migration complete. Created {conversations_created} conversations from existing chat history.")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error during migration: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
