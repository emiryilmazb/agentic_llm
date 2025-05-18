# Active Context

## Current Focus
Separating character definitions from conversation history to allow multiple conversations with the same character.

## Recent Changes
- Analyzed the existing codebase to understand current implementation
- Identified that chat history is currently stored directly in the Character model
- Found that the current architecture only allows for one conversation per character

## Next Steps
1. Create a new Conversation database model to store:
   - An ID field
   - Reference to a character
   - Title for the conversation
   - Chat history as a JSON field 
   - Timestamps for creation and updates

2. Create a ConversationService with methods to:
   - Create new conversations
   - List conversations for a character
   - Get conversation by ID
   - Update conversation chat history
   - Delete conversations

3. Create a ConversationRouter with endpoints for:
   - `POST /conversations/` - Create a new conversation
   - `GET /conversations/` - List all conversations (with option to filter by character)
   - `GET /conversations/{conversation_id}` - Get a specific conversation
   - `DELETE /conversations/{conversation_id}` - Delete a conversation

4. Update ChatRouter to use conversation_id:
   - `POST /chat/{conversation_id}` - Chat with a character in a specific conversation
   - `GET /chat/{conversation_id}/history` - Get history for a specific conversation
   - `DELETE /chat/{conversation_id}/history` - Clear history for a specific conversation

5. Modify ChatService to work with the Conversation model instead of the Character's chat_history

## Active Decisions and Considerations
- Need to consider how to handle existing chat histories - may need a migration script
- Need to decide on default conversation titles (could be timestamp-based or "New conversation")
- Consider adding a field for conversation context or topic

## Implementation Patterns
- Follow the existing service-based pattern where business logic is in services
- Maintain RESTful API design patterns
- Use SQLAlchemy relationship mechanisms for the Character-Conversation relationship
- Keep existing chat message format in the JSON field for backward compatibility
