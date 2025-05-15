"""
Unit tests for the CharacterService class.
"""
import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils.character_service import CharacterService

# Test data
TEST_CHARACTER_NAME = "Test Character"
TEST_BACKGROUND = "This is a test background."
TEST_PERSONALITY = "This is a test personality."
TEST_PROMPT = "This is a test prompt."
TEST_WIKI_INFO = "This is test wiki info."

@pytest.fixture
def mock_data_dir(tmp_path):
    """Create a temporary directory for test data."""
    return tmp_path

@pytest.fixture
def character_data():
    """Create test character data."""
    return {
        "name": TEST_CHARACTER_NAME,
        "background": TEST_BACKGROUND,
        "personality": TEST_PERSONALITY,
        "prompt": TEST_PROMPT,
        "wiki_info": TEST_WIKI_INFO,
        "use_agentic": True,
        "chat_history": []
    }

class TestCharacterService:
    """Test cases for the CharacterService class."""

    def test_create_prompt(self):
        """Test creating a prompt."""
        # Test without wiki info
        prompt = CharacterService.create_prompt(
            TEST_CHARACTER_NAME,
            TEST_BACKGROUND,
            TEST_PERSONALITY
        )
        
        assert TEST_CHARACTER_NAME in prompt
        assert TEST_BACKGROUND in prompt
        assert TEST_PERSONALITY in prompt
        
        # Test with wiki info
        prompt_with_wiki = CharacterService.create_prompt(
            TEST_CHARACTER_NAME,
            TEST_BACKGROUND,
            TEST_PERSONALITY,
            TEST_WIKI_INFO
        )
        
        assert TEST_CHARACTER_NAME in prompt_with_wiki
        assert TEST_BACKGROUND in prompt_with_wiki
        assert TEST_PERSONALITY in prompt_with_wiki
        assert TEST_WIKI_INFO in prompt_with_wiki

    @patch('src.utils.character_service.DATA_DIR')
    def test_save_character(self, mock_data_dir, mock_data_dir_fixture, character_data):
        """Test saving a character."""
        # Set the mock DATA_DIR to our temporary directory
        mock_data_dir.return_value = mock_data_dir_fixture
        
        # Create a mock open function
        mock_open = MagicMock()
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Patch the open function
        with patch('builtins.open', mock_open):
            # Call the function
            file_path = CharacterService.save_character(
                character_data["name"],
                character_data["background"],
                character_data["personality"],
                character_data["prompt"],
                character_data["wiki_info"],
                character_data["use_agentic"]
            )
            
            # Check that the file was opened with the correct path
            expected_path = mock_data_dir_fixture / f"{TEST_CHARACTER_NAME.lower().replace(' ', '_')}.json"
            assert file_path == expected_path
            
            # Check that json.dump was called with the correct data
            mock_file.write.assert_called_once()

    @patch('src.utils.character_service.DATA_DIR')
    def test_load_character(self, mock_data_dir, mock_data_dir_fixture, character_data):
        """Test loading a character."""
        # Set the mock DATA_DIR to our temporary directory
        mock_data_dir.return_value = mock_data_dir_fixture
        
        # Create the character file
        file_path = mock_data_dir_fixture / f"{TEST_CHARACTER_NAME.lower().replace(' ', '_')}.json"
        with open(file_path, 'w') as f:
            json.dump(character_data, f)
        
        # Load the character
        loaded_character = CharacterService.load_character(TEST_CHARACTER_NAME)
        
        # Check that the loaded character matches the original
        assert loaded_character["name"] == character_data["name"]
        assert loaded_character["background"] == character_data["background"]
        assert loaded_character["personality"] == character_data["personality"]
        assert loaded_character["prompt"] == character_data["prompt"]
        assert loaded_character["wiki_info"] == character_data["wiki_info"]
        assert loaded_character["use_agentic"] == character_data["use_agentic"]
        assert loaded_character["chat_history"] == character_data["chat_history"]

    @patch('src.utils.character_service.DATA_DIR')
    def test_get_all_characters(self, mock_data_dir, mock_data_dir_fixture, character_data):
        """Test getting all characters."""
        # Set the mock DATA_DIR to our temporary directory
        mock_data_dir.return_value = mock_data_dir_fixture
        
        # Create multiple character files
        for i in range(3):
            name = f"{TEST_CHARACTER_NAME}_{i}"
            data = character_data.copy()
            data["name"] = name
            file_path = mock_data_dir_fixture / f"{name.lower().replace(' ', '_')}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f)
        
        # Get all characters
        characters = CharacterService.get_all_characters()
        
        # Check that all characters were found
        assert len(characters) == 3
        for i in range(3):
            assert f"{TEST_CHARACTER_NAME}_{i}" in characters

    @patch('src.utils.character_service.DATA_DIR')
    def test_update_chat_history(self, mock_data_dir, mock_data_dir_fixture, character_data):
        """Test updating chat history."""
        # Set the mock DATA_DIR to our temporary directory
        mock_data_dir.return_value = mock_data_dir_fixture
        
        # Create the character file
        file_path = mock_data_dir_fixture / f"{TEST_CHARACTER_NAME.lower().replace(' ', '_')}.json"
        with open(file_path, 'w') as f:
            json.dump(character_data, f)
        
        # Update chat history
        user_message = "Hello, character!"
        character_response = "Hello, user!"
        
        CharacterService.update_chat_history(
            TEST_CHARACTER_NAME,
            user_message,
            character_response
        )
        
        # Load the character and check that the chat history was updated
        updated_character = CharacterService.load_character(TEST_CHARACTER_NAME)
        assert len(updated_character["chat_history"]) == 2
        assert updated_character["chat_history"][0]["role"] == "user"
        assert updated_character["chat_history"][0]["content"] == user_message
        assert updated_character["chat_history"][1]["role"] == "assistant"
        assert updated_character["chat_history"][1]["content"] == character_response

    def test_format_chat_history(self, character_data):
        """Test formatting chat history."""
        # Create chat history
        chat_history = [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm good, thanks!"}
        ]
        
        # Format chat history
        formatted_history = CharacterService.format_chat_history(
            chat_history,
            TEST_CHARACTER_NAME
        )
        
        # Check the formatted history
        assert "User: Hello!" in formatted_history
        assert f"{TEST_CHARACTER_NAME}: Hi there!" in formatted_history
        assert "User: How are you?" in formatted_history
        assert f"{TEST_CHARACTER_NAME}: I'm good, thanks!" in formatted_history

    @patch('src.utils.character_service.DATA_DIR')
    def test_save_character_data(self, mock_data_dir, mock_data_dir_fixture, character_data):
        """Test saving character data."""
        # Set the mock DATA_DIR to our temporary directory
        mock_data_dir.return_value = mock_data_dir_fixture
        
        # Create a mock open function
        mock_open = MagicMock()
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Patch the open function
        with patch('builtins.open', mock_open):
            # Call the function
            CharacterService.save_character_data(
                TEST_CHARACTER_NAME,
                character_data
            )
            
            # Check that the file was opened with the correct path
            expected_path = mock_data_dir_fixture / f"{TEST_CHARACTER_NAME.lower().replace(' ', '_')}.json"
            mock_open.assert_called_once_with(expected_path, 'w', encoding='utf-8')
            
            # Check that json.dump was called with the correct data
            mock_file.write.assert_called_once()

    @patch('src.utils.character_service.DATA_DIR')
    def test_delete_character(self, mock_data_dir, mock_data_dir_fixture, character_data):
        """Test deleting a character."""
        # Set the mock DATA_DIR to our temporary directory
        mock_data_dir.return_value = mock_data_dir_fixture
        
        # Create the character file
        file_path = mock_data_dir_fixture / f"{TEST_CHARACTER_NAME.lower().replace(' ', '_')}.json"
        with open(file_path, 'w') as f:
            json.dump(character_data, f)
        
        # Delete the character
        result = CharacterService.delete_character(TEST_CHARACTER_NAME)
        
        # Check that the character was deleted
        assert result is True
        assert not file_path.exists()
        
        # Try to delete a non-existent character
        result = CharacterService.delete_character("NonExistentCharacter")
        assert result is False

    @patch('src.utils.character_service.DATA_DIR')
    def test_clear_chat_history(self, mock_data_dir, mock_data_dir_fixture, character_data):
        """Test clearing chat history."""
        # Set the mock DATA_DIR to our temporary directory
        mock_data_dir.return_value = mock_data_dir_fixture
        
        # Add some chat history
        character_data["chat_history"] = [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        # Create the character file
        file_path = mock_data_dir_fixture / f"{TEST_CHARACTER_NAME.lower().replace(' ', '_')}.json"
        with open(file_path, 'w') as f:
            json.dump(character_data, f)
        
        # Clear chat history
        result = CharacterService.clear_chat_history(TEST_CHARACTER_NAME)
        
        # Check that the chat history was cleared
        assert result is True
        
        # Load the character and check that the chat history is empty
        updated_character = CharacterService.load_character(TEST_CHARACTER_NAME)
        assert updated_character["chat_history"] == []