"""
Chat service for handling character chat functionality.
"""
from typing import Dict, List, Any, Optional, Tuple, AsyncGenerator
import sys
import asyncio
from pathlib import Path
from sqlalchemy.orm import Session

# Add parent directory to sys.path for relative imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import agentic_character from app directory and our local AI service
from app.services.agentic_character_service import AgenticCharacter
from app.services.ai_service import AIService
from app.services.character_service import CharacterService
from app.services.conversation_service import ConversationService
from app.core.config import settings

class ChatService:
    """Service class for handling character chat functionality."""
    
    @staticmethod
    def get_character_response(conversation_id: int, user_message: str, db: Session) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Get a response from a character in a specific conversation, using either normal or agentic mode.
        
        Args:
            conversation_id: ID of the conversation
            user_message: User message
            db: Database session
            
        Returns:
            Tuple of (character_response, response_data)
        """
        try:
            # Get conversation data
            conversation_data = ConversationService.get_conversation(db, conversation_id)
            if not conversation_data:
                error_msg = f"Conversation with ID {conversation_id} not found"
                return error_msg, None
            
            # Get character data for this conversation
            character_data = ConversationService.get_character_for_conversation(db, conversation_id)
            if not character_data:
                error_msg = "Character for this conversation not found"
                return error_msg, None
            
            use_agentic = character_data.get("use_agentic", False)
            
            if use_agentic:
                # For agentic mode, we need to provide chat history to the character
                # Create a copy of character data with chat history from conversation
                agentic_character_data = character_data.copy()
                agentic_character_data["chat_history"] = conversation_data.get("chat_history", [])
                
                # Create agentic character and get response
                character = AgenticCharacter(agentic_character_data)
                response = character.get_response(user_message)
                
                # Update conversation with new chat history from agentic character
                ConversationService.update_chat_history(
                    db, 
                    conversation_id, 
                    user_message, 
                    response["display_text"]
                )
                
                # Return response
                return response["display_text"], response
            else:
                # Normal mode - use ConversationService and AIService
                prompt = character_data["prompt"]
                
                # Create text with conversation history
                history_text = ConversationService.format_chat_history(
                    conversation_data.get("chat_history", []), 
                    character_data["name"],
                    settings.MAX_HISTORY_MESSAGES
                )
                
                # Create full prompt
                full_prompt = f"""{prompt}

Sohbet geçmişi:
{history_text}

Kullanıcı: {user_message}
{character_data['name']}:"""
                
                # Get response using AIService
                response_text = AIService.generate_response(
                    prompt=full_prompt,
                    model_name=settings.DEFAULT_MODEL,
                    temperature=settings.DEFAULT_TEMPERATURE,
                    max_tokens=settings.DEFAULT_CHAT_TOKENS,
                    top_p=settings.DEFAULT_TOP_P
                )
                
                # Update conversation history
                ConversationService.update_chat_history(
                    db, 
                    conversation_id, 
                    user_message, 
                    response_text
                )
                
                return response_text, None
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            return error_msg, None
    
    @staticmethod
    async def get_streaming_character_response(conversation_id: int, user_message: str, db: Session) -> AsyncGenerator[str, None]:
        """
        Get a streaming response from a character in a specific conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_message: User message
            db: Database session
            
        Yields:
            Chunks of the character's response for streaming
        """
        try:
            print(f"DEBUG: ChatService.get_streaming_character_response called with conversation_id: {conversation_id}")
            # Get conversation data
            conversation_data = ConversationService.get_conversation(db, conversation_id)
            print(f"DEBUG: ConversationService.get_conversation returned: {conversation_data is not None}")
            if not conversation_data:
                yield f"Error: Conversation with ID {conversation_id} not found"
                return
            
            # Get character data for this conversation
            character_data = ConversationService.get_character_for_conversation(db, conversation_id)
            if not character_data:
                yield "Error: Character for this conversation not found"
                return
            
            use_agentic = character_data.get("use_agentic", False)
            
            if use_agentic:
                # For agentic characters, we don't support streaming yet
                # This is because agentic responses involve tool calls which are complex to stream
                # Instead, we'll get the full response and stream it as one chunk
                
                # Create a copy of character data with chat history from conversation
                agentic_character_data = character_data.copy()
                agentic_character_data["chat_history"] = conversation_data.get("chat_history", [])
                
                # Create agentic character and get response
                character = AgenticCharacter(agentic_character_data)
                response = character.get_response(user_message)
                
                # Update conversation with new chat history from agentic character
                ConversationService.update_chat_history(
                    db,
                    conversation_id,
                    user_message,
                    response["display_text"]
                )
                
                # Return response as a single chunk
                yield response["display_text"]
            else:
                # For normal mode, we can stream the response
                prompt = character_data["prompt"]
                
                # Create text with conversation history
                history_text = ConversationService.format_chat_history(
                    conversation_data.get("chat_history", []),
                    character_data["name"],
                    settings.MAX_HISTORY_MESSAGES
                )
                
                # Create full prompt
                full_prompt = f"""{prompt}

Sohbet geçmişi:
{history_text}

Kullanıcı: {user_message}
{character_data['name']}:"""
                
                # Collect all the response chunks to save in history later
                complete_response = ""
                
                # Get streaming response
                async for chunk in AIService.generate_streaming_response(
                    prompt=full_prompt,
                    model_name=settings.DEFAULT_MODEL,
                    temperature=settings.DEFAULT_TEMPERATURE,
                    max_tokens=settings.DEFAULT_CHAT_TOKENS,
                    top_p=settings.DEFAULT_TOP_P
                ):
                    # Append to complete response
                    complete_response += chunk
                    # Yield the chunk for streaming
                    yield chunk
                
                # Update conversation history with the complete response
                ConversationService.update_chat_history(
                    db, 
                    conversation_id, 
                    user_message, 
                    complete_response
                )
        
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            yield error_msg
