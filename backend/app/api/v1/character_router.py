"""
Character router for handling character-related endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.character_service import CharacterService
from app.services.wiki_service import WikiService
from app.models.character import CharacterCreate, CharacterResponse, CharacterList
from app.db.base import get_db

router = APIRouter(
    prefix="/characters",
    tags=["Characters"],
    responses={
        404: {"description": "Character not found"},
        500: {"description": "Internal server error"}
    }
)

@router.get("/", response_model=CharacterList)
async def get_characters(db: Session = Depends(get_db)):
    """
    Get a list of all available characters.
    
    Returns:
        List of character names
    """
    try:
        characters = CharacterService.get_all_characters(db)
        return {"characters": characters}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to retrieve characters", "error": str(e)}
        )

@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    """
    Create a new character.
    
    Parameters:
        character: The character data
        
    Returns:
        The created character data
    """
    try:
        # Generate the prompt based on provided character information
        wiki_info = None
        if character.use_wiki:
            wiki_info = WikiService.fetch_info(character.name)
        
        prompt = CharacterService.create_prompt(
            character.name, 
            character.background, 
            character.personality, 
            wiki_info
        )
        
        # Save the character data
        character_db = CharacterService.save_character(
            db,
            character.name, 
            character.background, 
            character.personality, 
            prompt, 
            wiki_info, 
            character.use_agentic
        )
        
        # Load the character data to return in the response
        character_data = CharacterService.load_character(db, character.name)
        if not character_data:
            raise HTTPException(
                status_code=500, 
                detail={"message": "Character created but could not be loaded"}
            )
            
        return character_data
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to create character", "error": str(e)}
        )

@router.get("/{character_name}", response_model=CharacterResponse)
async def get_character(
    character_name: str = Path(..., description="Name of the character"),
    db: Session = Depends(get_db)
):
    """
    Get a specific character by name.
    
    Parameters:
        character_name: Name of the character
        
    Returns:
        The character data
    """
    try:
        character_data = CharacterService.load_character(db, character_name)
        if not character_data:
            raise HTTPException(
                status_code=404, 
                detail={"message": f"Character '{character_name}' not found"}
            )
        return character_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to retrieve character", "error": str(e)}
        )

@router.delete("/{character_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    character_name: str = Path(..., description="Name of the character"),
    db: Session = Depends(get_db)
):
    """
    Delete a character by name.
    
    Parameters:
        character_name: Name of the character to delete
    """
    try:
        success = CharacterService.delete_character(db, character_name)
        if not success:
            raise HTTPException(
                status_code=404, 
                detail={"message": f"Character '{character_name}' not found"}
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"message": "Failed to delete character", "error": str(e)}
        )
