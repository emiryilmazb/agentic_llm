# Agentic Character Chatbot Backend

This is the backend API for the Agentic Character Chatbot application. It is built using FastAPI and provides a RESTful API for creating and interacting with AI characters.

## Features

- **Character Management**: Create, retrieve, update, and delete characters
- **Chat Functionality**: Interact with characters through a chat interface
- **Dynamic Tools**: Automatically create and manage tools that characters can use
- **API Documentation**: Auto-generated OpenAPI documentation
- **Testing Suite**: Comprehensive test coverage with pytest
- **Rate Limiting**: Protect the API from abuse
- **Logging**: Detailed logging for debugging and monitoring
- **Caching**: Improve performance with in-memory caching
- **Docker Support**: Containerized deployment

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/              # API version 1 endpoints
│   │       ├── character_router.py
│   │       ├── chat_router.py
│   │       ├── tool_router.py
│   │       └── api.py       # Main API router
│   ├── core/                # Core modules
│   │   ├── api_docs.py      # OpenAPI documentation enhancements
│   │   ├── cache.py         # Caching utilities
│   │   ├── config.py        # Application configuration
│   │   ├── error_models.py  # Error response models
│   │   └── middleware.py    # Middleware components
│   ├── models/              # Pydantic models
│   │   ├── character.py     # Character models
│   │   └── chat.py          # Chat models
│   ├── services/            # Business logic
│   │   ├── ai_service.py    # AI interaction service
│   │   ├── character_service.py  # Character management
│   │   ├── chat_service.py  # Chat functionality
│   │   ├── tool_service.py  # Tool management
│   │   └── wiki_service.py  # Wikipedia interaction
│   ├── tools/               # Tool implementations
│   │   ├── builtin/         # Built-in tools
│   │   └── dynamic/         # Dynamically created tools
│   ├── utils/               # Utility functions
│   ├── agentic_character.py # Agentic character implementation
│   ├── backend.py           # Backend launcher
│   ├── main.py              # FastAPI app initialization
│   └── mcp_server.py        # MCP server implementation
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest configuration and fixtures
│   ├── test_api_character.py  # Character API tests
│   └── test_api_chat.py     # Chat API tests
├── character_data/          # Character data storage
├── dynamic_tools/           # Dynamic tool storage
├── Dockerfile               # Container definition
├── pytest.ini               # Pytest configuration
├── requirements.txt         # Python dependencies
└── run.py                   # Main entry point
```

## API Endpoints

### Characters

- `GET /api/v1/characters` - Get all characters
- `POST /api/v1/characters` - Create a new character
- `GET /api/v1/characters/{character_name}` - Get a specific character
- `DELETE /api/v1/characters/{character_name}` - Delete a character

### Chat

- `POST /api/v1/chat/{character_name}` - Send a message to a character
- `GET /api/v1/chat/{character_name}/history` - Get chat history
- `DELETE /api/v1/chat/{character_name}/history` - Clear chat history

### Tools

- `GET /api/v1/tools` - Get all available tools
- `GET /api/v1/tools/{tool_name}` - Get details about a specific tool
- `DELETE /api/v1/tools/{tool_name}` - Delete a tool

## Installation and Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python run.py
   ```
5. Access the API at http://localhost:8000
6. View the API documentation at http://localhost:8000/docs

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t agentic-character-chatbot-backend .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 agentic-character-chatbot-backend
   ```

## Testing

Run tests using pytest:

```bash
pytest
```

For test coverage:

```bash
pytest --cov=app --cov-report=html
```

## Configuration

The application is configured using environment variables or a `.env` file:

```
ENVIRONMENT=development
SECRET_KEY=yoursecretkey
GEMINI_API_KEY=yourgeminiapikey
OPENAI_API_KEY=youropenaikey
DEBUG_MODE=true
ENABLE_LOGGING=true
RATE_LIMIT_PER_MINUTE=60
```

## REST API Best Practices Implemented

The backend follows these REST API best practices:

1. **Consistent RESTful Resource URLs**: Using logical resource-based URL structure
2. **Proper HTTP Methods**: Using GET, POST, DELETE for their intended purposes
3. **HTTP Status Codes**: Using appropriate status codes (200, 201, 204, 404, 422, 500)
4. **Error Handling**: Standardized error responses with detailed information
5. **Versioning**: API versioning via URL path (/api/v1/...)
6. **Documentation**: OpenAPI/Swagger documentation for all endpoints
7. **Security**: Rate limiting to prevent abuse
8. **Pagination**: Support for limiting results with queries
9. **Data Validation**: Request and response validation using Pydantic models
10. **CORS Support**: Configurable Cross-Origin Resource Sharing
11. **Health Checks**: Dedicated health check endpoint
12. **Testing**: Comprehensive test suite for all endpoints

## License

MIT
