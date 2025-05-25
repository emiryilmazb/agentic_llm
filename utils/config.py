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
# SQLite veritabanı yolu
DB_PATH = BASE_DIR / "agentic_llm.db"

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

# Session Configuration
DEFAULT_SESSION_TIMEOUT = 60 * 60 * 24  # 24 saat (saniye cinsinden)

# Application settings
APPLICATION_TITLE = "Agentic LLM"
APPLICATION_ICON = "🤖"
APPLICATION_DESCRIPTION = "Yapay zeka ile sohbet edin ve araçları kullanarak işlemler gerçekleştirin!"
