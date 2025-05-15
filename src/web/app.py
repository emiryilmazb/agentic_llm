"""
Agentic Character Chatbot Web Application.

This module provides the Streamlit web interface for the Agentic Character Chatbot.
"""
import streamlit as st
import json
import logging
from pathlib import Path

from src.core.agentic_character import AgenticCharacter
from src.core.mcp_server import get_default_server
from src.api.ai_service import AIService
from src.utils.character_service import CharacterService
from src.api.wiki_service import WikiService
from src.tools.dynamic.tool_manager import DynamicToolManager
from src.utils.config import (
    DATA_DIR,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_CHAT_TOKENS,
    APPLICATION_TITLE,
    APPLICATION_ICON,
    APPLICATION_DESCRIPTION,
    ENABLE_DYNAMIC_TOOLS
)

# Create a logger for this module
logger = logging.getLogger(__name__)

def get_character_response(character_data, user_message, use_agentic=False):
    """
    Get character response in normal or agentic mode.
    
    Args:
        character_data: Character data
        user_message: User message
        use_agentic: Whether to use agentic mode
        
    Returns:
        Tuple of (character_response, response_data)
    """
    logger.info(f"Getting response for character: {character_data['name']}")
    
    try:
        if use_agentic:
            # Create agentic character and get response
            logger.debug("Using agentic mode")
            character = AgenticCharacter(character_data)
            response = character.get_response(user_message)
            
            # Update character data with updated chat history
            character_data["chat_history"] = character.chat_history
            character_data["prompt"] = character.prompt
            
            # Save updated character data immediately
            CharacterService.save_character_data(character_data["name"], character_data)
            
            # Return response
            return response["display_text"], response
        else:
            # Normal mode - Use CharacterService and AIService
            logger.debug("Using normal mode")
            prompt = character_data["prompt"]
            
            # Create text with last 10 conversations
            history_text = CharacterService.format_chat_history(
                character_data["chat_history"], 
                character_data["name"]
            )
            
            # Create full prompt
            full_prompt = f"""{prompt}

Chat history:
{history_text}

User: {user_message}
{character_data['name']}:"""
            
            # Get response using AIService
            response_text = AIService.generate_response(
                prompt=full_prompt,
                model_name=DEFAULT_MODEL,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_CHAT_TOKENS,
                top_p=DEFAULT_TOP_P
            )
            
            return response_text, None
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg, None

def update_character_history(character_name, user_message, character_response, response_data=None):
    """
    Update chat history.
    
    Args:
        character_name: Character name
        user_message: User message
        character_response: Character response
        response_data: Extra response data (for agentic mode)
    """
    logger.debug(f"Updating chat history for: {character_name}")
    
    # Use CharacterService to update history
    CharacterService.update_chat_history(
        character_name, 
        user_message, 
        character_response, 
        response_data
    )

def delete_dynamic_tool(tool_name):
    """
    Delete a dynamic tool.
    
    Args:
        tool_name: Name of the tool to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Deleting dynamic tool: {tool_name}")
    
    if not ENABLE_DYNAMIC_TOOLS:
        logger.warning("Dynamic tools are disabled")
        return False
    
    try:
        # Use DynamicToolManager to delete the tool
        success = DynamicToolManager.delete_tool(tool_name)
        return success
    except Exception as e:
        logger.error(f"Error deleting tool: {str(e)}", exc_info=True)
        return False

def run_app():
    """Run the Streamlit application."""
    logger.info("Starting Streamlit application")
    
    st.set_page_config(page_title=APPLICATION_TITLE, page_icon=APPLICATION_ICON, layout="wide")
    
    st.title(f"{APPLICATION_ICON} Agentic Character Chatbot")
    st.markdown(APPLICATION_DESCRIPTION)
    
    # Sidebar
    with st.sidebar:
        st.header("Character Management")
        
        # Character selection
        characters = CharacterService.get_all_characters()
        selected_option = st.radio(
            "What would you like to do?",
            ["Chat with an existing character", "Create a new character"]
        )
        
        # MCP server info
        with st.expander("🛠️ Available Tools"):
            mcp_server = get_default_server()
            tools_info = mcp_server.get_tools_info()
            
            # Separate built-in and dynamic tools
            built_in_tools = []
            dynamic_tools = []
            
            for tool in tools_info:
                if "dynamic" in tool and tool["dynamic"]:
                    dynamic_tools.append(tool)
                else:
                    built_in_tools.append(tool)
            
            # Show built-in tools
            st.subheader("Built-in Tools")
            for tool in built_in_tools:
                st.markdown(f"**{tool['name']}**: {tool['description']}")
            
            # Show dynamic tools (if any)
            if dynamic_tools:
                st.subheader("Dynamically Created Tools")
                for tool in dynamic_tools:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"**{tool['name']}**: {tool['description']}")
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{tool['name']}"):
                            if delete_dynamic_tool(tool['name']):
                                st.success(f"{tool['name']} tool successfully deleted!")
                                st.rerun()  # Refresh the page
                            else:
                                st.error(f"Error deleting {tool['name']} tool.")
                st.info("Dynamic tools are automatically created based on user needs.")
        
        if selected_option == "Chat with an existing character":
            if characters:
                selected_character = st.selectbox("Select a character", characters)
                if st.button("Chat with this character"):
                    st.session_state.active_character = selected_character
                    st.session_state.chat_started = True
            else:
                st.warning("No saved characters found. Please create a character first.")
        
        elif selected_option == "Create a new character":
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
                        
                        # Update session state
                        st.session_state.active_character = character_name
                        st.session_state.chat_started = True
                        st.rerun()
                else:
                    st.error("Please enter a character name.")
    
    
    # Main chat area
    if 'chat_started' not in st.session_state:
        st.session_state.chat_started = False
        
    if 'active_character' not in st.session_state:
        st.session_state.active_character = None
        
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Show chat area if active character exists
    if st.session_state.chat_started and st.session_state.active_character:
        character_data = CharacterService.load_character(st.session_state.active_character)
        
        if character_data:
            st.subheader(f"Chat with {character_data['name']}")
            
            # Show character information
            with st.expander("About this Character"):
                st.write(f"**Personality:** {character_data['personality']}")
                if character_data.get('background'):
                    st.write(f"**Background:** {character_data['background']}")
                if character_data.get('wiki_info'):
                    st.write(f"**Wikipedia Information:** {character_data['wiki_info']}")
            
            # Clear chat button
            col1, col2 = st.columns([6, 1])
            with col2:
                if st.button("🗑️ Clear Chat"):
                    # Clear messages in session state
                    st.session_state.messages = []
                    # Clear character chat history
                    character_data["chat_history"] = []
                    # Save updated character
                    CharacterService.save_character_data(st.session_state.active_character, character_data)
                    st.rerun()
            
            # Show chat history
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
            
            # User message input
            user_message = st.chat_input("Type your message...")
            
            if user_message:
                # Show user message
                with st.chat_message("user"):
                    st.write(user_message)
                
                # Add user message to session state
                st.session_state.messages.append({"role": "user", "content": user_message})
                
                # Check if character uses agentic features
                use_agentic = character_data.get("use_agentic", False)
                
                # Get character response
                with st.chat_message("assistant"):
                    with st.spinner(f"{character_data['name']} is typing..."):
                        character_response, response_data = get_character_response(character_data, user_message, use_agentic)
                        st.write(character_response)
                
                # Add character response to session state
                st.session_state.messages.append({"role": "assistant", "content": character_response})
                
                # Update chat history
                update_character_history(st.session_state.active_character, user_message, character_response, response_data)
        else:
            st.error("Character not found. Please select another character.")
    else:
        st.info("👈 Select a character from the sidebar or create a new one to start chatting.")

if __name__ == "__main__":
    run_app()