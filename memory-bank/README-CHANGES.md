# Separating Character from Conversation History

## Overview
This implementation separates character data from conversation history, allowing users to have multiple distinct conversations with the same character. This is accomplished by creating a new Conversation model that stores chat history, while the Character model now focuses solely on character attributes.

## Changes Made

### Database Models
1. **New Conversation Model**: 
   - Created `backend/app/db/models/conversation.py` to store conversation data
   - Each conversation belongs to a character and has its own chat history

2. **Updated Character Model**:
   - Removed `chat_history` field from Character model
   - Added relationship to Conversation model

### API Implementation
1. **New Conversation Service**:
   - Created `backend/app/services/conversation_service.py` with methods for:
     - Creating new conversations
     - Getting conversations for a character
     - Managing conversation history
     - Formatting chat history for prompts

2. **New Conversation Router**:
   - Created `backend/app/api/v1/conversation_router.py` with endpoints for:
     - `POST /api/v1/conversations/` - Create a new conversation
     - `GET /api/v1/conversations/` - List all conversations (with optional character filter)
     - `GET /api/v1/conversations/{id}` - Get a specific conversation
     - `PATCH /api/v1/conversations/{id}` - Update a conversation's title
     - `DELETE /api/v1/conversations/{id}` - Delete a conversation
     - `DELETE /api/v1/conversations/{id}/history` - Clear a conversation's history

3. **Updated Chat Service and Router**:
   - Modified to work with conversation IDs instead of character names
   - Updated chat history storage to use conversations
   - Conversation-based chat endpoints:
     - `POST /api/v1/chat/{conversation_id}` - Send a message in a conversation
     - `GET /api/v1/chat/{conversation_id}/history` - Get chat history for a conversation

### Migration
1. **Database Migration**:
   - Added migration function to `backend/app/db/init_db.py` to migrate existing chat history
   - Updated `backend/app/backend.py` to call the migration function
   - Created separate migration script `backend/scripts/migrate_to_conversations.py` for manual migration

## Testing Instructions

### Starting the Backend with Migrations
1. Run the backend with automatic migrations:
   ```
   cd backend
   python run.py
   ```
   This will:
   - Create the new Conversation table
   - Migrate existing character chat histories to new conversations

2. For manual migration (if needed):
   ```
   cd backend
   python scripts/migrate_to_conversations.py
   ```

### API Testing
1. Test creating a character:
   ```
   curl -X POST http://localhost:8000/api/v1/characters/ -H "Content-Type: application/json" -d '{"name":"Test Character","personality":"Friendly","background":"Sample background","prompt":"You are a test character"}'
   ```

2. Test creating a conversation for the character:
   ```
   curl -X POST http://localhost:8000/api/v1/conversations/ -H "Content-Type: application/json" -d '{"character_name":"Test Character","title":"Test Conversation"}'
   ```
   Note the conversation ID in the response.

3. Test sending a message in the conversation:
   ```
   curl -X POST http://localhost:8000/api/v1/chat/1 -H "Content-Type: application/json" -d '{"message":"Hello, how are you?"}'
   ```
   (Replace '1' with the actual conversation ID)

4. Get the conversation history:
   ```
   curl http://localhost:8000/api/v1/chat/1/history
   ```
   (Replace '1' with the actual conversation ID)

5. List all conversations for a character:
   ```
   curl "http://localhost:8000/api/v1/conversations/?character_name=Test%20Character"
   ```

## Frontend Integration
The frontend already has a ConversationList component and conversation management in ChatContext.js that uses mock data. Update the following functions to use the new API endpoints:

1. `fetchConversations`
2. `fetchMessages`
3. `createConversation`
4. `deleteConversation`
5. `sendMessage`
6. `generateAIResponse`
7. `clearConversation`
8. `renameConversation`

## Possible Issues
1. **Migration Errors**: If some characters have invalid chat_history data, migration might fail. The migration function includes error handling to skip problematic characters.

2. **Backwards Compatibility**: Older frontend versions might still try to use the character name-based endpoints. Consider keeping legacy endpoints temporarily if needed.

3. **Frontend Integration**: The frontend's mock implementation might differ from the actual API response structure. Adjust as needed.

4. **Database Schema**: If the database already exists, ensure SQLAlchemy correctly detects the schema changes. Manual migration might be required in some cases.
