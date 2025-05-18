"""
Chat router for handling chat-related endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import asyncio

from app.services.character_service import CharacterService
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService
from app.models.chat import ChatMessage, ChatResponse, ChatHistoryResponse, StreamingChatResponse
from app.db.base import get_db

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={
        404: {"description": "Conversation not found"},
        500: {"description": "Internal server error"}
    }
)

@router.post("/{conversation_id}", response_model=ChatResponse, tags=["Chat"])
async def chat_in_conversation(
    message: ChatMessage,
    conversation_id: int = Path(..., description="ID of the conversation", ge=1),
    db: Session = Depends(get_db)
):
    """
    Send a message in a conversation and get a response.
    
    Parameters:
        conversation_id: ID of the conversation
        message: The message to send
        
    Returns:
        The character's response
    """
    try:
        # Check if conversation exists
        conversation_data = ConversationService.get_conversation(db, conversation_id)
        if not conversation_data:
            raise HTTPException(
                status_code=404, 
                detail={"message": f"Conversation with ID {conversation_id} not found"}
            )
        
        # Get character info for this conversation
        character_data = ConversationService.get_character_for_conversation(db, conversation_id)
        if not character_data:
            raise HTTPException(
                status_code=404, 
                detail={"message": "Character for this conversation not found"}
            )
        
        # Get response from character
        character_response, response_data = ChatService.get_character_response(
            conversation_id,
            message.message,
            db
        )
        
        # Create response object
        response = {
            "character": character_data["name"],
            "message": character_response,
            "data": response_data
        }
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to get character response", "error": str(e)}
        )

@router.post("/{conversation_id}/stream")
async def stream_chat_in_conversation(
    message: ChatMessage,
    conversation_id: int = Path(..., description="ID of the conversation", ge=1),
    db: Session = Depends(get_db)
):
    """
    Send a message in a conversation and get a streaming response.
    
    Parameters:
        conversation_id: ID of the conversation
        message: The message to send
        
    Returns:
        A streaming response with the character's message
    """
    print(f"DEBUG: Entering stream_chat_in_conversation for conversation_id: {conversation_id}")
    
    async def response_generator():
        try:
            print(f"DEBUG: Calling ChatService.get_streaming_character_response for conversation_id: {conversation_id}")
            async for chunk in ChatService.get_streaming_character_response(
                conversation_id,
                message.message,
                db
            ):
                # Format each chunk as a Server-Sent Event
                yield f"data: {chunk}\n\n"
        except Exception as e:
            # Handle any exceptions that might occur during streaming
            yield f"data: Error: {str(e)}\n\n"
        
        # Send a final message to indicate the stream is complete
        yield "data: [DONE]\n\n"
    
    # Create and return a streaming response
    return StreamingChatResponse.create(response_generator())

@router.get("/{conversation_id}/history", response_model=ChatHistoryResponse, tags=["Chat"])
async def get_chat_history(
    conversation_id: int = Path(..., description="ID of the conversation", ge=1),
    limit: Optional[int] = Query(100, description="Maximum number of messages to return", ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get chat history for a specific conversation.
    
    Parameters:
        conversation_id: ID of the conversation
        limit: Maximum number of messages to return (default: 100, max: 1000)
        
    Returns:
        The chat history for the conversation
    """
    try:
        # Get conversation data
        conversation_data = ConversationService.get_conversation(db, conversation_id)
        if not conversation_data:
            raise HTTPException(
                status_code=404, 
                detail={"message": f"Conversation with ID {conversation_id} not found"}
            )
        
        # Get character info for this conversation
        character_data = ConversationService.get_character_for_conversation(db, conversation_id)
        if not character_data:
            raise HTTPException(
                status_code=404, 
                detail={"message": "Character for this conversation not found"}
            )
        
        # Get chat history (limited to the specified number of messages)
        chat_history = conversation_data.get("chat_history", [])[-limit:]
        
        return {
            "character": character_data["name"],
            "history": chat_history
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to retrieve chat history", "error": str(e)}
        )
