# Web Components

This directory contains the Streamlit components used in the web interface of the Agentic Character Chatbot application. These components are modular UI elements that can be reused across different parts of the application.

## Component Structure

Each component is a Python module that defines a function or class that renders a specific part of the UI. Components should be self-contained and reusable, with clear interfaces for passing data and handling events.

## Available Components

The following components are planned for this directory:

1. **character_creation.py**: Component for creating new characters
2. **character_selection.py**: Component for selecting existing characters
3. **chat_interface.py**: Component for the chat interface
4. **tool_display.py**: Component for displaying available tools
5. **settings_panel.py**: Component for application settings

## Example Component

Here's an example of how a component should be structured:

```python
"""
Character creation component.

This module provides a component for creating new characters.
"""
import streamlit as st
import logging
from typing import Dict, Any, Optional, Callable

from src.utils.character_service import CharacterService
from src.api.wiki_service import WikiService

# Create a logger for this module
logger = logging.getLogger(__name__)

def character_creation_component(on_character_created: Optional[Callable[[str], None]] = None) -> None:
    """
    Render the character creation component.
    
    Args:
        on_character_created: Optional callback function to call when a character is created
    """
    st.subheader("Create a New Character")
    
    character_name = st.text_input("Character Name (e.g., Atatürk, Harry Potter, etc.)")
    
    use_wiki = st.checkbox("Get information from Wikipedia", value=True)
    wiki_info = None
    
    if use_wiki and character_name:
        wiki_button = st.button("Get Wikipedia Information")
        if wiki_button:
            with st.spinner(f"Getting information about {character_name}..."):
                # Use WikiService to get information
                wiki_info = WikiService.fetch_info(character_name)
                st.session_state.wiki_info = wiki_info
                st.success("Information retrieved!")
    
    if 'wiki_info' in st.session_state:
        st.text_area("Wikipedia Information", st.session_state.wiki_info, height=150)
    
    character_background = st.text_area(
        "Character Background", 
        placeholder="Write the character's background, history, and important events..."
    )
    
    character_personality = st.text_area(
        "Character Personality",
        placeholder="Write the character's personality traits, speaking style, and behaviors..."
    )
    
    use_agentic = st.checkbox("Enable Agentic Features", value=True, 
                             help="Allows the character to perform actions and use tools")
    
    if st.button("Create Character"):
        if character_name:
            wiki_data = st.session_state.get('wiki_info', None) if use_wiki else None
            
            # If no Wikipedia information, background and personality are required
            if not wiki_data and (not character_background or not character_personality):
                st.error("If not using Wikipedia information, please fill in both character background and personality.")
            else:
                try:
                    # Create and save the character
                    prompt = CharacterService.create_prompt(
                        character_name, 
                        character_background, 
                        character_personality, 
                        wiki_data
                    )
                    CharacterService.save_character(
                        character_name, 
                        character_background, 
                        character_personality, 
                        prompt, 
                        wiki_data, 
                        use_agentic
                    )
                    st.success(f"{character_name} character successfully created!")
                    
                    # Call the callback if provided
                    if on_character_created:
                        on_character_created(character_name)
                except Exception as e:
                    logger.error(f"Error creating character: {str(e)}", exc_info=True)
                    st.error(f"An error occurred while creating the character: {str(e)}")
        else:
            st.error("Please enter a character name.")
```

## Best Practices

When creating components, follow these best practices:

1. **Single Responsibility**: Each component should have a single responsibility
2. **Reusability**: Components should be reusable across different parts of the application
3. **Clear Interface**: Components should have clear interfaces for passing data and handling events
4. **Error Handling**: Components should handle errors gracefully
5. **Logging**: Use the logger to log important events and errors
6. **Documentation**: Include docstrings for all functions and classes
7. **Type Hints**: Use type hints to improve code readability and IDE support
8. **Session State**: Use Streamlit's session state for persistent data between reruns
9. **Callbacks**: Use callback functions for communication between components
10. **Responsive Design**: Ensure components work well on different screen sizes

## Integration with Main App

Components are imported and used in the main app (`src/web/app.py`). For example:

```python
from src.web.components.character_creation import character_creation_component
from src.web.components.chat_interface import chat_interface_component

def run_app():
    # ...
    if selected_option == "Create a new character":
        character_creation_component(on_character_created=lambda name: set_active_character(name))
    elif st.session_state.active_character:
        chat_interface_component(st.session_state.active_character)
    # ...