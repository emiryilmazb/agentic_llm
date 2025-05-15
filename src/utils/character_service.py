"""
Character service utilities for handling character data operations.

This module provides a service class for managing character data, including
creation, storage, retrieval, and chat history management.
"""
import json
import os
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from src.utils.config import DATA_DIR, MAX_HISTORY_MESSAGES

# Create the data directory if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Create a logger for this module
logger = logging.getLogger(__name__)

class CharacterService:
    """
    Service class for handling character data operations.
    
    This class provides methods for creating, loading, and managing character data,
    including chat history management.
    """
    
    @staticmethod
    def create_prompt(
        name: str, 
        background: str, 
        personality: str, 
        wiki_info: Optional[str] = None
    ) -> str:
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
        logger.info(f"Creating prompt for character: {name}")
        
        # Base prompt with character information
        prompt = f"""You are {name}. Respond according to the following information:

Character Traits:
{personality}

Background Information:
{background}
"""
        # Add Wikipedia information if available
        if wiki_info:
            prompt += f"""
Wikipedia Information:
{wiki_info}

Based on this information, respond as {name}. Speak in first person and reflect the character's personality.
"""
        
        logger.debug(f"Created prompt for {name} ({len(prompt)} characters)")
        return prompt

    @staticmethod
    def save_character(
        name: str, 
        background: str, 
        personality: str, 
        prompt: str, 
        wiki_info: Optional[str] = None, 
        use_agentic: bool = False
    ) -> Path:
        """
        Save character data as a JSON file.
        
        Args:
            name: Character name
            background: Character background
            personality: Character personality
            prompt: System prompt for the character
            wiki_info: Wikipedia information
            use_agentic: Whether to use agentic capabilities
            
        Returns:
            Path to the saved file
        """
        logger.info(f"Saving character: {name} (agentic: {use_agentic})")
        
        # Create character data dictionary
        character_data = {
            "name": name,
            "background": background,
            "personality": personality,
            "prompt": prompt,
            "wiki_info": wiki_info,
            "use_agentic": use_agentic,
            "chat_history": [],
            "created_at": str(time.ctime()),
            "modified_at": str(time.ctime()),
            "version": "1.0"
        }
        
        # Create filename from character name
        file_path = DATA_DIR / f"{name.lower().replace(' ', '_')}.json"
        
        # Save to file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(character_data, f, ensure_ascii=False, indent=4)
            logger.debug(f"Character saved to: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving character {name}: {str(e)}")
            raise

    @staticmethod
    def load_character(name: str) -> Optional[Dict[str, Any]]:
        """
        Load a saved character.
        
        Args:
            name: Name of the character to load
            
        Returns:
            Character data dictionary or None if not found
        """
        logger.info(f"Loading character: {name}")
        
        # Create filename from character name
        file_path = DATA_DIR / f"{name.lower().replace(' ', '_')}.json"
        
        # Check if file exists
        if not file_path.exists():
            logger.warning(f"Character file not found: {file_path}")
            return None
        
        # Load from file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                character_data = json.load(f)
            logger.debug(f"Character loaded from: {file_path}")
            return character_data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing character file {file_path}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error loading character {name}: {str(e)}")
            return None

    @staticmethod
    def get_all_characters() -> List[str]:
        """
        List all saved characters.
        
        Returns:
            List of character names
        """
        logger.info("Getting all characters")
        characters = []
        
        try:
            # Iterate through all JSON files in the data directory
            for file in DATA_DIR.glob("*.json"):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        character_data = json.load(f)
                        characters.append(character_data["name"])
                except Exception as e:
                    logger.error(f"Error reading character file {file}: {str(e)}")
                    continue
            
            logger.debug(f"Found {len(characters)} characters")
            return characters
        except Exception as e:
            logger.error(f"Error getting all characters: {str(e)}")
            return []

    @staticmethod
    def update_chat_history(
        character_name: str,
        user_message: str,
        character_response: str,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update the chat history for a character.
        
        Args:
            character_name: Name of the character
            user_message: User's message
            character_response: Character's response
            response_data: Optional additional response data
        """
        logger.info(f"Updating chat history for: {character_name}")
        
        # For agentic mode, chat history is already updated and saved in get_character_response
        if response_data:
            logger.debug("Skipping chat history update (agentic mode)")
            return
            
        # For normal mode, manually update and save chat history
        try:
            # Load character data
            character_data = CharacterService.load_character(character_name)
            if not character_data:
                logger.error(f"Cannot update chat history: Character {character_name} not found")
                return
            
            # Update chat history
            character_data["chat_history"].append({"role": "user", "content": user_message})
            character_data["chat_history"].append({"role": "assistant", "content": character_response})
            character_data["modified_at"] = str(time.ctime())
            
            # Save updated character data
            file_path = DATA_DIR / f"{character_name.lower().replace(' ', '_')}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(character_data, f, ensure_ascii=False, indent=4)
            
            logger.debug(f"Chat history updated for {character_name}")
        except Exception as e:
            logger.error(f"Error updating chat history for {character_name}: {str(e)}")

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
        logger.debug(f"Formatting chat history for {character_name} ({len(chat_history)} messages)")
        
        history_text = ""
        if chat_history:
            # Include last N messages for context based on configuration
            recent_history = chat_history[-MAX_HISTORY_MESSAGES:] if len(chat_history) > MAX_HISTORY_MESSAGES else chat_history
            
            for msg in recent_history:
                if msg["role"] == "user":
                    history_text += f"User: {msg['content']}\n"
                else:
                    history_text += f"{character_name}: {msg['content']}\n"
        
        return history_text
        
    @staticmethod
    def save_character_data(character_name: str, character_data: Dict[str, Any]) -> None:
        """
        Save character data to file.
        
        Args:
            character_name: Name of the character
            character_data: Character data dictionary to save
        """
        logger.info(f"Saving character data for: {character_name}")
        
        try:
            # Update modified timestamp
            character_data["modified_at"] = str(time.ctime())
            
            # Save to file
            file_path = DATA_DIR / f"{character_name.lower().replace(' ', '_')}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(character_data, f, ensure_ascii=False, indent=4)
            
            logger.debug(f"Character data saved to: {file_path}")
        except Exception as e:
            logger.error(f"Error saving character data for {character_name}: {str(e)}")
            raise
    
    @staticmethod
    def delete_character(character_name: str) -> bool:
        """
        Delete a character.
        
        Args:
            character_name: Name of the character to delete
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting character: {character_name}")
        
        try:
            file_path = DATA_DIR / f"{character_name.lower().replace(' ', '_')}.json"
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Character deleted: {file_path}")
                return True
            else:
                logger.warning(f"Character file not found: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting character {character_name}: {str(e)}")
            return False
    
    @staticmethod
    def clear_chat_history(character_name: str) -> bool:
        """
        Clear the chat history for a character.
        
        Args:
            character_name: Name of the character
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Clearing chat history for: {character_name}")
        
        try:
            # Load character data
            character_data = CharacterService.load_character(character_name)
            if not character_data:
                logger.error(f"Cannot clear chat history: Character {character_name} not found")
                return False
            
            # Clear chat history
            character_data["chat_history"] = []
            character_data["modified_at"] = str(time.ctime())
            
            # Save updated character data
            CharacterService.save_character_data(character_name, character_data)
            
            logger.debug(f"Chat history cleared for {character_name}")
            return True
        except Exception as e:
            logger.error(f"Error clearing chat history for {character_name}: {str(e)}")
            return False