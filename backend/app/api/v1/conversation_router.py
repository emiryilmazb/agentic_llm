"""
Conversation router for handling conversation-related endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from typing import Optional, List
from sqlalchemy.orm import Session

from app.services.conversation_service import ConversationService
from app.models.conversation import (
    ConversationCreate, 
    ConversationUpdate, 
    ConversationResponse, 
    ConversationList
)
from app.db.base import get_db

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
    responses={
        404: {"description": "Conversation or character not found"},
        500: {"description": "Internal server error"}
    }
)

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation with a character.
    
    Parameters:
        conversation: The conversation to create
        
    Returns:
        The created conversation
    """
    try:
        result = ConversationService.create_conversation(
            db, 
            conversation.character_name, 
            conversation.title
        )
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail={"message": f"Character '{conversation.character_name}' not found"}
            )
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to create conversation", "error": str(e)}
        )

@router.get("/", response_model=ConversationList)
async def list_conversations(
    character_name: Optional[str] = Query(None, description="Filter conversations by character name"),
    limit: int = Query(10, description="Maximum number of conversations to return", ge=1, le=100),
    offset: int = Query(0, description="Number of conversations to skip", ge=0),
    db: Session = Depends(get_db)
):
    """
    List conversations, optionally filtered by character.
    
    Parameters:
        character_name: Optional character name to filter by
        limit: Maximum number of conversations to return (default: 10, max: 100)
        offset: Number of conversations to skip (default: 0)
        
    Returns:
        List of conversations
    """
    try:
        if character_name:
            conversations = ConversationService.get_conversations_by_character(
                db, character_name, limit, offset
            )
        else:
            conversations = ConversationService.get_all_conversations(
                db, limit, offset
            )
            
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to list conversations", "error": str(e)}
        )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int = Path(..., description="ID of the conversation to get", ge=1),
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation by ID.
    
    Parameters:
        conversation_id: ID of the conversation to get
        
    Returns:
        The conversation
    """
    try:
        conversation = ConversationService.get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=404, 
                detail={"message": f"Conversation with ID {conversation_id} not found"}
            )
            
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to get conversation", "error": str(e)}
        )

@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    update_data: ConversationUpdate,
    conversation_id: int = Path(..., description="ID of the conversation to update", ge=1),
    db: Session = Depends(get_db)
):
    """
    Update a conversation's title.
    
    Parameters:
        conversation_id: ID of the conversation to update
        update_data: Data to update
        
    Returns:
        The updated conversation
    """
    try:
        conversation = ConversationService.update_conversation(
            db, conversation_id, update_data.title
        )
        
        if not conversation:
            raise HTTPException(
                status_code=404, 
                detail={"message": f"Conversation with ID {conversation_id} not found"}
            )
            
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to update conversation", "error": str(e)}
        )

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int = Path(..., description="ID of the conversation to delete", ge=1),
    db: Session = Depends(get_db)
):
    """
    Delete a conversation.
    
    Parameters:
        conversation_id: ID of the conversation to delete
    """
    try:
        success = ConversationService.delete_conversation(db, conversation_id)
        if not success:
            raise HTTPException(
                status_code=404, 
                detail={"message": f"Conversation with ID {conversation_id} not found"}
            )
            
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to delete conversation", "error": str(e)}
        )

@router.delete("/{conversation_id}/history", response_model=ConversationResponse)
async def clear_conversation_history(
    conversation_id: int = Path(..., description="ID of the conversation", ge=1),
    db: Session = Depends(get_db)
):
    """
    Clear the chat history for a conversation.
    
    Parameters:
        conversation_id: ID of the conversation
        
    Returns:
        The updated conversation
    """
    try:
        conversation = ConversationService.clear_chat_history(db, conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=404, 
                detail={"message": f"Conversation with ID {conversation_id} not found"}
            )
            
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to clear conversation history", "error": str(e)}
        )
