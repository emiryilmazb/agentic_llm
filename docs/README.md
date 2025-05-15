# Agentic Character.ai Clone

This project is an advanced version of a Character.ai-like chatbot platform with agentic capabilities and Model Context Protocol (MCP) features.

## Features

### Core Chatbot Features
- Create customizable characters
- Automatically fetch character information from Wikipedia
- Define character personality and background
- Save chat history

### Agentic Architecture
- Enable characters to perform actions
- Use tools based on user requests
- Execute real actions alongside intelligent responses
- **Dynamic Tool Creation**: Automatically create tools as needed

### MCP (Model Context Protocol) Tools
#### Built-in Tools
- **search_wikipedia**: Search Wikipedia for information
- **get_current_time**: Get current date/time information
- **get_weather**: Get weather information (demo)
- **open_website**: Open websites
- **calculate_math**: Perform mathematical calculations

#### Dynamic Tools
- **currency_converter**: Currency exchange rates and conversions (example)
- *and more*: The system can create new tools based on user needs

## Installation

1. Clone the repository:
```
git clone https://github.com/emiryilmazb/agentic_llm.git
cd agentic_llm
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up API key:
Create a `.env` file with your Google Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Run the application:
```
python main.py
```

## Usage

### Creating a Character
1. Select "Create a new character" from the sidebar
2. Enter the character name
3. Optionally fetch information from Wikipedia
4. Define the character's background and personality
5. Enable "Agentic Features" to allow the character to use tools
6. Click "Create Character"

### Chatting with a Character
1. Select "Chat with an existing character" from the sidebar
2. Choose a character
3. Click "Chat with this character"
4. Type messages in the chat input

### Agentic Character Interaction
Agentic-enabled characters can respond to requests like:

- "What's the weather like today?"
- "Can you tell me about Albert Einstein?"
- "What time is it?"
- "Calculate 2+2*3 for me"
- "Open example.com"
- "What's 1 USD in Turkish Lira?" (dynamic tool creation example)
- "What's the weather forecast for Tokyo?" (dynamic tool creation example)

## Architecture

The project consists of several key components:

1. **Core Modules**:
   - `agentic_character.py`: Handles character actions and tool usage
   - `mcp_server.py`: Provides tools for characters to use

2. **API Services**:
   - `ai_service.py`: Interfaces with the Gemini AI API
   - `wiki_service.py`: Handles Wikipedia interactions

3. **Tool System**:
   - `tools/base.py`: Base classes for all tools
   - `tools/builtin/`: Built-in tool implementations
   - `tools/dynamic/`: Dynamically created tools

4. **Web Interface**:
   - `web/app.py`: Streamlit web application

5. **Utilities**:
   - `utils/config.py`: Configuration management
   - `utils/character_service.py`: Character data operations

## Development

### Adding New Tools

To add a new built-in tool:

1. Create a new Python file in the `src/tools/builtin/` directory
2. Define a class that inherits from `MCPTool`
3. Implement the required methods (`__init__` and `execute`)
4. Register the tool in `src/core/mcp_server.py`

```python
from src.tools.base import MCPTool

class NewTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="new_tool",
            description="Description of what your tool does"
        )
    
    def execute(self, args):
        # Implement tool functionality
        return {"result": "operation result"}
```

### Dynamic Tool Creation System

The system can automatically create new tools based on user needs:

1. User sends a request that requires a tool not currently available
2. System analyzes the request and determines what kind of tool is needed
3. AI model generates code for the new tool
4. Generated tool is saved to the `src/tools/dynamic/` directory and registered with the MCP server
5. Character uses the new tool to respond to the user's request

## Security Considerations

The dynamic tool creation system has security implications:

1. Generated code is executed in the application's environment
2. External API calls may expose sensitive information
3. Resource usage may be unpredictable

In a production environment, additional safeguards should be implemented:

1. Code sandboxing
2. Rate limiting
3. API key management
4. Resource usage monitoring

## License

This project is licensed under the MIT License - see the LICENSE file for details.