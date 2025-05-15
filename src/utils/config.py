"""
Configuration settings for the application.

This module centralizes all configuration parameters to avoid hardcoding values
throughout the application. It loads settings from environment variables and
provides default values when necessary.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data" / "character_data"
LOGS_DIR = BASE_DIR / "logs"

# Create necessary directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model Configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "800"))
DEFAULT_TOP_P = float(os.getenv("DEFAULT_TOP_P", "0.95"))
DEFAULT_CHAT_TOKENS = int(os.getenv("DEFAULT_CHAT_TOKENS", "500"))

# Wikipedia Configuration
DEFAULT_WIKI_LANGUAGE = os.getenv("DEFAULT_WIKI_LANGUAGE", "en")
DEFAULT_WIKI_RESULTS = int(os.getenv("DEFAULT_WIKI_RESULTS", "5"))

# Chat History Configuration
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))

# Application settings
APPLICATION_TITLE = os.getenv("APPLICATION_TITLE", "Agentic Character.ai Clone")
APPLICATION_ICON = os.getenv("APPLICATION_ICON", "🤖")
APPLICATION_DESCRIPTION = os.getenv(
    "APPLICATION_DESCRIPTION", 
    "Chat with your favorite characters or create your own character that can perform actions!"
)

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "app.log"))

# Security Configuration
ENABLE_DYNAMIC_TOOLS = os.getenv("ENABLE_DYNAMIC_TOOLS", "true").lower() == "true"
SANDBOX_DYNAMIC_TOOLS = os.getenv("SANDBOX_DYNAMIC_TOOLS", "false").lower() == "true"

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Create a logger for this module
logger = logging.getLogger(__name__)

# Validate critical configuration
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY is not set. API calls will fail.")

def get_config() -> Dict[str, Any]:
    """
    Get the complete configuration as a dictionary.
    
    Returns:
        Dict[str, Any]: Dictionary containing all configuration parameters
    """
    return {
        "BASE_DIR": BASE_DIR,
        "SRC_DIR": SRC_DIR,
        "DATA_DIR": DATA_DIR,
        "LOGS_DIR": LOGS_DIR,
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "DEFAULT_MODEL": DEFAULT_MODEL,
        "DEFAULT_TEMPERATURE": DEFAULT_TEMPERATURE,
        "DEFAULT_MAX_TOKENS": DEFAULT_MAX_TOKENS,
        "DEFAULT_TOP_P": DEFAULT_TOP_P,
        "DEFAULT_CHAT_TOKENS": DEFAULT_CHAT_TOKENS,
        "DEFAULT_WIKI_LANGUAGE": DEFAULT_WIKI_LANGUAGE,
        "DEFAULT_WIKI_RESULTS": DEFAULT_WIKI_RESULTS,
        "MAX_HISTORY_MESSAGES": MAX_HISTORY_MESSAGES,
        "APPLICATION_TITLE": APPLICATION_TITLE,
        "APPLICATION_ICON": APPLICATION_ICON,
        "APPLICATION_DESCRIPTION": APPLICATION_DESCRIPTION,
        "LOG_LEVEL": LOG_LEVEL,
        "LOG_FILE": LOG_FILE,
        "ENABLE_DYNAMIC_TOOLS": ENABLE_DYNAMIC_TOOLS,
        "SANDBOX_DYNAMIC_TOOLS": SANDBOX_DYNAMIC_TOOLS,
    }