# Streamlit to FastAPI Migration

## Migration Overview

This project has been migrated from a Streamlit web application to a standalone FastAPI backend. The migration preserves all existing functionality while providing a more professional, state-of-the-art architecture that follows best practices for modern web applications.

## Key Changes

1. **Architecture Transformation**:
   - Converted from a monolithic Streamlit app to a RESTful API backend
   - Implemented proper separation of concerns (models, services, API endpoints)
   - Organized code into a clean, modular structure

2. **New Project Structure**:
   ```
   app/
   ├── __init__.py
   ├── main.py                # Main FastAPI application
   ├── core/                  # Core configuration and settings
   │   ├── __init__.py
   │   └── config.py
   ├── models/                # Pydantic data models
   │   ├── __init__.py
   │   ├── character.py
   │   └── chat.py
   ├── services/              # Business logic services
   │   ├── __init__.py
   │   ├── character_service.py
   │   ├── chat_service.py
   │   └── tool_service.py
   │   
   app_backend.py            # App launcher script
   ```

3. **Added Features**:
   - RESTful API with comprehensive endpoints
   - Proper error handling and HTTP status codes
   - API documentation via Swagger UI
   - Enhanced performance through asynchronous request handling

## Running the Application

### Prerequisites

Make sure you have installed all the required packages:

```bash
pip install -r requirements.txt
```

### Starting the Backend

Run the backend API server:

```bash
python app_backend.py
```

The API server will start at http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

## API Endpoints

The following API endpoints are available:

### Character Management

- `GET /api/characters` - Get a list of all characters
- `POST /api/characters` - Create a new character
- `GET /api/characters/{character_name}` - Get a specific character
- `DELETE /api/characters/{character_name}` - Delete a character

### Chat

- `POST /api/chat/{character_name}` - Send a message to a character
- `GET /api/chat/{character_name}/history` - Get chat history
- `DELETE /api/chat/{character_name}/history` - Clear chat history

### Tools

- `GET /api/tools` - Get a list of all available tools
- `DELETE /api/tools/{tool_name}` - Delete a dynamic tool

## Frontend Integration

This backend API can be integrated with any frontend technology. You can:

1. Build a dedicated frontend using frameworks like React, Vue, or Angular
2. Create a mobile app that connects to this API
3. Use the API directly through tools like Postman or curl

## Benefits of This Migration

1. **Scalability**: The application can now handle more users and be deployed in a distributed manner.
2. **Maintainability**: The code is now more organized and follows established patterns.
3. **Flexibility**: The backend can be consumed by multiple clients (web, mobile, desktop).
4. **Testability**: The code is now easier to test due to separation of concerns.
5. **Documentation**: The API is self-documenting via Swagger UI.

## Original Functionality

All functionality from the original Streamlit application has been preserved:

- Character creation and management
- Chat with characters in normal or agentic mode
- Wikipedia information fetching
- Dynamic tool creation and management
- Agentic capabilities for characters to use tools

This migration enhances the application while retaining all the features that made the original version valuable.
