# System Patterns

## Current Architecture

### Database Models
1. **Character Model**: 
   - Stores character information, personality, and prompt
   - Currently also stores chat_history directly in the Character model as a JSON field
   - This creates a limitation where a character can only have one conversation thread

### API Structure
1. **Character Router** - manages character creation, retrieval, updating
2. **Chat Router** - handles sending messages to characters and retrieving chat history
3. **Tool Router** - manages dynamic tools for agentic characters

### Service Layer
1. **Character Service** - handles character data operations, saving/loading, etc.
2. **Chat Service** - processes chat messages and responses, updates chat history
3. **AI Service** - generates responses from AI models

### Current Limitations
The current design ties conversation history directly to characters, which prevents having multiple separate conversations with the same character.

## Proposed Changes

### New Database Models
1. **Character Model**: Remove chat_history field
2. **Conversation Model**: New model to store:
   - ID field
   - Reference to character (foreign key to Character)
   - Title for the conversation
   - Chat history as a JSON field
   - Creation timestamp and update timestamp

### Updated API Structure
1. **Add Conversation Router**: 
   - Create a new conversation with a character
   - List all conversations for a character
   - Get a specific conversation
   - Delete a conversation

2. **Update Chat Router**:
   - Modify to work with conversation_id instead of just character_name
   - Update to store chat history in the conversation, not the character

### Updated Service Flow
1. **Character Service**: No longer manages chat history
2. **New Conversation Service**: Manages conversations and their chat histories
3. **Chat Service**: Updated to work with conversations, not character's chat history

## Component Relationships
```
User → Frontend → API Endpoints → Services → Database Models
```

## Critical Implementation Paths
1. Create a new Conversation model
2. Create a new ConversationService
3. Create a ConversationRouter with CRUD endpoints
4. Update the ChatRouter to work with conversations
5. Update the ChatService to store history in conversations
6. Update the frontend to support multiple conversations per character
