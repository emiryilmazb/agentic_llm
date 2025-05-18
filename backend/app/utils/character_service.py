"""
Character service utilities for handling character data operations.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

from utils.config import DATA_DIR, MAX_HISTORY_MESSAGES

# Create the data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

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
    def save_character(name: str, 
                      background: str, 
                      personality: str, 
                      prompt: str, 
                      wiki_info: Optional[str] = None, 
                      use_agentic: bool = False) -> Path:
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
        character_data = {
            "name": name,
            "background": background,
            "personality": personality,
            "prompt": prompt,
            "wiki_info": wiki_info,
            "use_agentic": use_agentic,
            "chat_history": []
        }
        
        file_path = DATA_DIR / f"{name.lower().replace(' ', '_')}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(character_data, f, ensure_ascii=False, indent=4)
        
        return file_path

    @staticmethod
    def load_character(name: str) -> Optional[Dict[str, Any]]:
        """
        Load a saved character.
        
        Args:
            name: Name of the character to load
            
        Returns:
            Character data dictionary or None if not found
        """
        file_path = DATA_DIR / f"{name.lower().replace(' ', '_')}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    @staticmethod
    def get_all_characters() -> List[str]:
        """
        List all saved characters.
        
        Returns:
            List of character names
        """
        characters = []
        for file in DATA_DIR.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                character_data = json.load(f)
                characters.append(character_data["name"])
        return characters

    @staticmethod
    def update_chat_history(character_name: str,
                          user_message: str,
                          character_response: str,
                          response_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the chat history for a character.
        
        Args:
            character_name: Name of the character
            user_message: User's message
            character_response: Character's response
            response_data: Optional additional response data
        """
        # Agentic modda, sohbet geçmişi zaten get_character_response içinde güncellenmiş ve kaydedilmiştir
        if response_data:
            return
            
        # Normal modda, sohbet geçmişini manuel olarak güncelle ve kaydet
        character_data = CharacterService.load_character(character_name)
        if character_data:
            character_data["chat_history"].append({"role": "user", "content": user_message})
            character_data["chat_history"].append({"role": "assistant", "content": character_response})
            
            file_path = DATA_DIR / f"{character_name.lower().replace(' ', '_')}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(character_data, f, ensure_ascii=False, indent=4)

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
            for msg in chat_history[-MAX_HISTORY_MESSAGES:]:
                if msg["role"] == "user":
                    history_text += f"Kullanıcı: {msg['content']}\n"
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
        file_path = DATA_DIR / f"{character_name.lower().replace(' ', '_')}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(character_data, f, ensure_ascii=False, indent=4)
