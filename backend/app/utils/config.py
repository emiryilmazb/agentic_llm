"""
Configuration settings for the application.
All configuration parameters are centralized here to avoid hardcoding values.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "character_data"

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model Configuration
DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 800
DEFAULT_TOP_P = 0.95
DEFAULT_CHAT_TOKENS = 500  # Use fewer tokens for chat responses

# Wikipedia Configuration
DEFAULT_WIKI_LANGUAGE = "en"
DEFAULT_WIKI_RESULTS = 5

# Chat History Configuration
MAX_HISTORY_MESSAGES = 10

# Application settings
APPLICATION_TITLE = "Agentic Character.ai Clone"
APPLICATION_ICON = "🤖"
APPLICATION_DESCRIPTION = "Chat with your favorite characters or create your own character that can perform actions!"
