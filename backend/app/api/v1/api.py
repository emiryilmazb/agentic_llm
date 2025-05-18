"""
Main API router combining all API endpoints.
"""
from fastapi import APIRouter

from app.api.v1.character_router import router as character_router
from app.api.v1.chat_router import router as chat_router
from app.api.v1.conversation_router import router as conversation_router
from app.api.v1.tool_router import router as tool_router

# Create the main API router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(character_router)
api_router.include_router(chat_router)
api_router.include_router(conversation_router)
api_router.include_router(tool_router)
