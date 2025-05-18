# Agentic Character Chatbot Backend

This directory contains a complete backend implementation of the Agentic Character Chatbot, built with FastAPI. This is a migration of the original Streamlit application to a more robust, scalable, and maintainable architecture.

## Directory Structure

```
app/
├── api/                  # API routes and controllers (optional extension)
├── core/                 # Core configuration and settings
├── models/               # Pydantic data models
├── services/             # Business logic services
├── tools/                # MCP tools implementation
│   ├── builtin/          # Built-in MCP tools
│   └── dynamic/          # Dynamically created MCP tools
├── utils/                # Utility functions and helpers
├── .env                  # Environment variables
├── agentic_character.py  # Agentic character implementation
├── backend.py            # Backend launcher
├── main.py               # FastAPI application
├── mcp_server.py         # MCP server implementation
```

## How to Run the Backend

### Prerequisites

Make sure you have installed all the required dependencies:

```bash
pip install -r requirements.txt
```

### Starting the Backend

Run the backend API server:

```bash
cd app
python backend.py
```

The API server will start at http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

## API Endpoints

The backend exposes the following RESTful API endpoints:

### Character Management

- `GET /api/characters` - Get a list of all characters
- `POST /api/characters` - Create a new character
- `GET /api/characters/{character_name}` - Get details for a specific character
- `DELETE /api/characters/{character_name}` - Delete a character

### Chat

- `POST /api/chat/{character_name}` - Send a message to a character
- `GET /api/chat/{character_name}/history` - Get chat history
- `DELETE /api/chat/{character_name}/history` - Clear chat history

### Tools

- `GET /api/tools` - Get a list of all available tools
- `DELETE /api/tools/{tool_name}` - Delete a dynamic tool

## Configuration

Configuration settings are stored in `.env` file and managed via the `app/core/config.py` module. The important settings include:

- API keys for generative AI models
- Database connection information
- Feature flags and toggle switches
- Application metadata

## Components

### Agentic Character

The agentic character module (`agentic_character.py`) provides functionality for characters to perform actions like searching Wikipedia, checking the weather, or calculating math expressions.

### MCP Server

The Model Context Protocol (MCP) server (`mcp_server.py`) manages tools that characters can use to perform actions. These tools can be either built-in or dynamically created based on user needs.

### Dynamic Tools

The system supports dynamically creating tools when a character encounters a request it doesn't have a built-in tool for. These tools are stored in the `app/tools/dynamic` directory.

## Services

The application is organized around service modules that implement specific business functions:

- `CharacterService` - Create, read, update, delete character data
- `ChatService` - Generate chat responses and manage chat history
- `AIService` - Interface with generative AI models
- `WikiService` - Search and retrieve information from Wikipedia
- `ToolService` - Manage MCP tools

## Data Storage

Character data is stored as JSON files in the `character_data` directory, which is created automatically if it doesn't exist.
