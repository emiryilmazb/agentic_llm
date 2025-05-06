import streamlit as st
import json
import os
from pathlib import Path

from agentic_character import AgenticCharacter
from mcp_server import get_default_server
from utils.ai_service import AIService
from utils.character_service import CharacterService
from utils.wiki_service import WikiService
from utils.suggestion_service import SuggestionService
from utils.config import (
    DATA_DIR,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_CHAT_TOKENS,
    APPLICATION_TITLE,
    APPLICATION_ICON,
    APPLICATION_DESCRIPTION
)

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

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
    try:
        if use_agentic:
            # Create agentic character and get response
            character = AgenticCharacter(character_data)
            response = character.get_response(user_message)
            
            # Save character data with updated chat history
            character_data["chat_history"] = character.chat_history
            character_data["prompt"] = character.prompt
            
            # Return the response
            return response["display_text"], response
        else:
            # Normal mode - use CharacterService and AIService
            prompt = character_data["prompt"]
            
            # Create text containing the last 10 conversations
            history_text = CharacterService.format_chat_history(
                character_data["chat_history"], 
                character_data["name"]
            )
            
            # Create the full prompt
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
    # Update history using CharacterService
    CharacterService.update_chat_history(
        character_name, 
        user_message, 
        character_response, 
        response_data
    )

def main():
    st.set_page_config(page_title=APPLICATION_TITLE, page_icon=APPLICATION_ICON, layout="wide")
    
    st.title(f"{APPLICATION_ICON} {APPLICATION_TITLE}")
    st.markdown(APPLICATION_DESCRIPTION)
    
    # Sidebar with improved organization
    with st.sidebar:
        st.subheader("📱 Navigation")
        # Sidebar tab selection with improved design
        sidebar_tabs = ["👤 Characters", "🛠️ Tools"]
        selected_tab = st.radio("Navigation", sidebar_tabs, label_visibility="collapsed")
        
        # Visual separator
        st.divider()
        
        if selected_tab == "👤 Characters":
            characters = CharacterService.get_all_characters()
            
            # Sub-options in Characters tab
            character_options = ["Character List", "Add New Character"]
            selected_character_option = st.radio("Character Options", character_options, label_visibility="collapsed")
            
            if selected_character_option == "Character List":
                st.subheader("Available Characters")
                
                if characters:
                    # Character selection area
                    st.markdown("**Select a character you want to chat with:**")
                    
                    for character in characters:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{character}**")
                        with col2:
                            if st.button("Select", key=f"select_{character}"):
                                st.session_state.active_character = character
                                st.session_state.chat_started = True
                                st.rerun()
                else:
                    st.info("No saved characters yet. Please use the 'Add New Character' option to create a character.")
            
            elif selected_character_option == "Add New Character":
                st.subheader("Create New Character")
                
                # Callback function for character name input
                def update_name_suggestions():
                    import time
                    
                    current_input = st.session_state.character_name_input
                    
                    # Track the last input and time in session state
                    if 'last_input' not in st.session_state:
                        st.session_state.last_input = ""
                    
                    # Only process if the input has changed
                    if current_input != st.session_state.last_input:
                        st.session_state.last_input = current_input
                        
                        # Get suggestions if there are at least 2 characters
                        if current_input and len(current_input) >= 2:
                            with st.spinner("Loading suggestions..."):
                                suggestions = SuggestionService.get_character_name_suggestions(current_input)
                                st.session_state.name_suggestions = suggestions
                        else:
                            st.session_state.name_suggestions = []

                # Initialize session state variables
                if 'name_suggestions' not in st.session_state:
                    st.session_state.name_suggestions = []
                if 'character_name_input' not in st.session_state:
                    st.session_state.character_name_input = ""

                # Character name input
                character_name = st.text_input(
                    "Character Name", 
                    placeholder="e.g., Einstein, Harry Potter, etc.", 
                    help="Enter the name of the character you want to create",
                    key="character_name_input",
                    on_change=update_name_suggestions
                )
                
                # Show suggestions if available
                if st.session_state.name_suggestions:
                    st.write("**Suggested characters:**")
                    selected_suggestion = st.radio(
                        "Character suggestions",
                        [""] + st.session_state.name_suggestions,
                        label_visibility="collapsed"
                    )
                    
                    # Update text_input if user selects a suggestion
                    if selected_suggestion and selected_suggestion != character_name:
                        st.session_state.character_name_input = selected_suggestion
                        character_name = selected_suggestion
                        # Refresh the page
                        st.rerun()
                
                # Option to fetch Wikipedia information
                use_wiki = st.checkbox("Get information from Wikipedia", value=True)
                wiki_info = None
                
                if use_wiki:
                    # Clear wiki_info when character name changes
                    if character_name and ('last_character_name' not in st.session_state or st.session_state.last_character_name != character_name):
                        if 'wiki_info' in st.session_state:
                            del st.session_state.wiki_info
                        st.session_state.last_character_name = character_name
                    
                    wiki_col1, wiki_col2 = st.columns([3, 1])
                    with wiki_col2:
                        wiki_button = st.button("Get Info", key="wiki_search")
                    
                    if wiki_button:
                        if not character_name:
                            st.error("Character name cannot be empty! Please enter a character name.")
                        else:
                            with st.spinner(f"Getting information about {character_name}..."):
                                # Fetch info using WikiService
                                wiki_info = WikiService.fetch_info(character_name)
                                st.session_state.wiki_info = wiki_info
                                st.success("Information retrieved!")
                
                # Show wiki information if available
                if 'wiki_info' in st.session_state:
                    st.text_area("Wikipedia Information", st.session_state.wiki_info, height=150)
                
                with st.container():
                    st.markdown("**Character Details**")
                    
                    character_background = st.text_area(
                        "Character Background", 
                        placeholder="Write about the character's background, story, and important events...",
                        height=120
                    )
                    
                    character_personality = st.text_area(
                        "Character Personality",
                        placeholder="Write about the character's personality traits, speaking style, and behaviors...",
                        height=120
                    )
                    
                    use_agentic = st.checkbox("Enable Agentic Features", value=True, 
                                          help="Allows the character to perform actions and use tools")
                
                # Create button
                create_col1, create_col2 = st.columns([3, 1])
                with create_col2:
                    create_button = st.button("Create Character", type="primary")
                
                if create_button:
                    if character_name:
                        wiki_data = st.session_state.get('wiki_info', None) if use_wiki else None
                        
                        # Background and personality are required if no wiki info is fetched
                        if not wiki_data and (not character_background or not character_personality):
                            st.error("If information is not fetched from Wikipedia, please fill in both character background and personality.")
                        else:
                            # Create and save character using CharacterService
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
                            st.success(f"Character {character_name} successfully created!")
                            
                            # Update session state
                            st.session_state.active_character = character_name
                            st.session_state.chat_started = True
                            
                            # Return to character list
                            st.session_state.character_option = "Character List"
                            st.rerun()
                    else:
                        st.error("Please fill in the character name.")
        
        elif selected_tab == "🛠️ Tools":
            st.subheader("Available Tools")
            
            # MCP server info
            mcp_server = get_default_server()
            tools_info = mcp_server.get_tools_info()
            
            if tools_info:
                for i, tool in enumerate(tools_info):
                    with st.expander(f"**{tool['name']}**", expanded=False):
                        st.markdown(f"{tool['description']}")
                        st.markdown("---")
                        st.markdown("**Usage Examples:**")
                        st.code(f"Example: \"Using the {tool['name']} tool...\"")
            else:
                st.info("No available tools yet.")
            
            # Placeholder for dynamic tool addition area (to be added in the future)
            with st.expander("Add New Tool (Coming Soon)", expanded=False):
                st.info("This feature will be added soon.")

    
    # Session state management
    if 'chat_started' not in st.session_state:
        st.session_state.chat_started = False
        
    if 'active_character' not in st.session_state:
        st.session_state.active_character = None
        
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Main content area
    main_container = st.container()
    
    with main_container:
        # Show chat area if there is an active character
        if st.session_state.chat_started and st.session_state.active_character:
            character_data = CharacterService.load_character(st.session_state.active_character)
            
            if character_data:
                # Chat header and character information
                chat_header_col1, chat_header_col2 = st.columns([3, 1])
                
                with chat_header_col1:
                    st.subheader(f"💬 Chat with {character_data['name']}")
                    
                with chat_header_col2:
                    # Show agentic feature status
                    use_agentic = character_data.get("use_agentic", False)
                    if use_agentic:
                        st.success("🤖 Agentic: Active", icon="✅")
                    else:
                        st.info("🤖 Agentic: Inactive", icon="ℹ️")
                
                st.divider()
                
                # Enhanced character information panel
                with st.expander("📝 Character Profile", expanded=False):
                    # Use columns for better organization
                    info_col1, info_col2 = st.columns(2)
                    
                    with info_col1:
                        st.markdown("### Basic Information")
                        st.markdown(f"**Name:** {character_data['name']}")
                        
                        if character_data.get('personality'):
                            st.markdown("### Personality")
                            st.markdown(character_data['personality'])
                    
                    with info_col2:
                        if character_data.get('background'):
                            st.markdown("### Background")
                            st.markdown(character_data['background'])
                    
                    # Wikipedia information in a separate section if available
                    if character_data.get('wiki_info'):
                        st.markdown("---")
                        st.markdown("### Wikipedia Information")
                        st.markdown(character_data['wiki_info'])
                
                # Create a clean, professional chat interface using native Streamlit components
                
                # Messages area container 
                messages_container = st.container()
                
                # Chat controls area
                control_container = st.container()
                
                # Put the chat input at the bottom visually but process it first in code
                with control_container:
                    # Add a horizontal divider to separate chat messages from input area
                    st.divider()
                    
                    # Create two columns for chat input and optional buttons
                    input_col, button_col = st.columns([5, 1])
                    
                    with input_col:
                        user_message = st.chat_input("Type your message to engage with the character...", key="chat_input")
                    
                    # Optional: Clear chat button in the second column
                    with button_col:
                        if st.button("Clear Chat", key="clear_chat"):
                            st.session_state.messages = []
                            st.rerun()
                
                # Message display area (located above the input visually)
                with messages_container:
                    # Welcome message for new chats
                    if len(st.session_state.messages) == 0:
                        st.info(f"👋 Welcome to your conversation with **{character_data['name']}**! Type a message below to start chatting.")
                    
                    # Display message history
                    for msg in st.session_state.messages:
                        # User messages
                        if msg["role"] == "user":
                            with st.chat_message("user", avatar="👤"):
                                st.write(msg["content"])
                        # Character/assistant messages
                        else:
                            with st.chat_message("assistant", avatar=f"🤖"):
                                st.write(msg["content"])
                
                if user_message:
                    # Add user message to session state
                    st.session_state.messages.append({"role": "user", "content": user_message})
                    
                    # Check character's agentic feature
                    use_agentic = character_data.get("use_agentic", False)
                    
                    # Create a placeholder for the assistant's message
                    with st.spinner(f"{character_data['name']} is typing a response..."):
                        # Get character's response
                        character_response, response_data = get_character_response(character_data, user_message, use_agentic)
                        
                        # Add character's response to session state
                        st.session_state.messages.append({"role": "assistant", "content": character_response})
                        
                        # Update chat history
                        update_character_history(st.session_state.active_character, user_message, character_response, response_data)
                    
                    # Rerun the app to display the updated messages
                    st.rerun()
            else:
                st.error("Character not found. Please select another character from the sidebar.")
        else:
            # Main screen if no character is selected
            st.markdown("## 🤖 Chat with Agentic Characters")
            
            # Info cards
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(
                    """
                    **Character Selection**
                    
                    👈 To start chatting, select a character from the sidebar or create a new one.
                    
                    * You can see available characters in the **Characters** tab.
                    * Use the **Add New Character** option to create your own character.
                    """
                )
            
            with col2:
                st.success(
                    """
                    **Agentic Features**
                    
                    🛠️ Characters with agentic features enabled can provide more interactive responses using various tools.
                    
                    * You can see available tools in the **Tools** tab.
                    * Tools allow characters to search for information, make calculations, and more.
                    """
                )

if __name__ == "__main__":
    main()
