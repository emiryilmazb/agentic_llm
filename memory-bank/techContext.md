# Technical Context

## Technologies Used

### Backend
- **Python**: Core programming language
- **FastAPI**: Web framework for building the API
- **SQLAlchemy**: ORM for database interactions
- **Pydantic**: Data validation and settings management
- **SQLite**: Database (agentic.db)

### Frontend
- **React**: JavaScript library for building the UI
- **Tailwind CSS**: Utility-first CSS framework for styling
- **JavaScript/JSX**: Programming language for frontend logic

## Development Setup
- Docker containers available for both frontend and backend
- Development can be started using scripts in the `scripts` directory

## Dependencies
- AI model integration (appears to be using a configuration-based approach)
- MCP server for dynamic tools
- Wiki service integration

## Database Structure
- SQLAlchemy models define the database schema
- The primary database file is `backend/agentic.db`
- JSON is stored in specialized column types (JSONEncodedDict)

## API Patterns
- RESTful API design
- Endpoint structure follows FastAPI conventions
- Services layer abstracts business logic

## Technical Constraints
- Chat history is currently tied directly to characters, limiting the ability to have multiple conversations
- The system appears to support both regular and "agentic" character modes
- System is designed for Turkish language responses (based on prompts)

## Frontend Components
- Character management UI
- Chat interface with message history
- Conversation management (currently limited by backend design)
- Tool management interface
