# Contributing to Agentic LLM

Thank you for considering contributing to the Agentic LLM project! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful, inclusive, and considerate in all interactions.

## How to Contribute

There are many ways to contribute to the project:

1. **Reporting Bugs**: If you find a bug, please create an issue with a detailed description.
2. **Suggesting Enhancements**: Have an idea for a new feature? Create an issue with the "enhancement" label.
3. **Submitting Pull Requests**: Code contributions are welcome! See the section below for details.
4. **Improving Documentation**: Help improve the documentation by fixing errors or adding missing information.
5. **Creating Tools**: Develop new tools that can be used by agentic characters.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```
   git clone https://github.com/yourusername/agentic_llm.git
   cd agentic_llm
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
5. Run the application:
   ```
   python main.py
   ```

## Pull Request Process

1. Create a new branch for your feature or bugfix:
   ```
   git checkout -b feature/your-feature-name
   ```
   or
   ```
   git checkout -b fix/your-bugfix-name
   ```

2. Make your changes, following the coding standards (see below)

3. Add tests for your changes if applicable

4. Run the tests to ensure they pass:
   ```
   pytest
   ```

5. Update the documentation if necessary

6. Commit your changes with a descriptive commit message:
   ```
   git commit -m "Add feature: your feature description"
   ```

7. Push your branch to your fork:
   ```
   git push origin feature/your-feature-name
   ```

8. Create a pull request from your branch to the main repository

9. Wait for review and address any feedback

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters
- Use docstrings for all modules, classes, and functions
- Use type hints where appropriate

### Documentation

- Update documentation for any changes to the API or functionality
- Document all new features, tools, or significant changes
- Keep the README.md up to date

### Testing

- Write tests for all new features or bug fixes
- Ensure all tests pass before submitting a pull request
- Aim for good test coverage

## Project Structure

The project follows a modular structure:

```
agentic_llm/
├── src/
│   ├── core/           # Core functionality
│   ├── api/            # API services
│   ├── tools/          # Tool implementations
│   │   ├── builtin/    # Built-in tools
│   │   ├── dynamic/    # Dynamically created tools
│   ├── utils/          # Utility functions
│   ├── web/            # Web interface
├── tests/              # Test suite
├── data/               # Data storage
├── docs/               # Documentation
```

## Adding New Tools

### Built-in Tools

To add a new built-in tool:

1. Create a new Python file in `src/tools/builtin/`
2. Define a class that inherits from `MCPTool`
3. Implement the required methods (`__init__` and `execute`)
4. Register the tool in `src/core/mcp_server.py`

Example:

```python
from src.tools.base import MCPTool
from typing import Dict, Any

class MyNewTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="my_new_tool",
            description="Description of what your tool does"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required arguments
        validation_error = self.validate_args(args, ["required_param"])
        if validation_error:
            return validation_error
            
        # Implement tool functionality
        try:
            # Your implementation here
            result = {"result": "operation result"}
            return result
        except Exception as e:
            return self.handle_error(e)
```

### Dynamic Tools

The system can create tools dynamically, but you can also:

1. Improve the tool generation logic in `src/tools/dynamic/tool_manager.py`
2. Add templates for common tool types
3. Enhance the validation and security of generated tools

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.