"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from pydantic import validator
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import os
import json

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "character_data"
DYNAMIC_TOOLS_DIR = BASE_DIR / "dynamic_tools"

# Ensure the data directories exist
DATA_DIR.mkdir(exist_ok=True)
DYNAMIC_TOOLS_DIR.mkdir(exist_ok=True)

class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # Application metadata
    PROJECT_NAME: str = "Agentic Character Chatbot"
    PROJECT_DESCRIPTION: str = "Chat with your favorite characters or create your own character that can perform actions!"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "development-secret-key-not-for-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URI: str = f"sqlite:///{BASE_DIR.joinpath('agentic.db')}"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # API keys and credentials
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    AI_API_KEY: Optional[str] = None
    
    # Model configuration
    DEFAULT_MODEL: str = "gemini-2.0-flash"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 800
    DEFAULT_TOP_P: float = 0.95
    DEFAULT_CHAT_TOKENS: int = 500  # Use fewer tokens for chat responses
    
    # Wikipedia configuration
    DEFAULT_WIKI_LANGUAGE: str = "en"
    DEFAULT_WIKI_RESULTS: int = 5
    
    # Chat history configuration
    MAX_HISTORY_MESSAGES: int = 10
    
    # Feature flags
    ENABLE_DYNAMIC_TOOLS: bool = True
    ENABLE_LOGGING: bool = True
    DEBUG_MODE: bool = False
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # File paths and directories
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    DYNAMIC_TOOLS_DIR: Path = DYNAMIC_TOOLS_DIR
    
    # Caching settings
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600  # 1 hour in seconds
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    def get_api_keys(self) -> Dict[str, Optional[str]]:
        """Get all API keys as a dictionary."""
        return {
            "gemini": self.GEMINI_API_KEY,
            "openai": self.OPENAI_API_KEY,
            "ai": self.AI_API_KEY
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary, handling Path objects."""
        result = {}
        for key, value in self.dict().items():
            if isinstance(value, Path):
                result[key] = str(value)
            else:
                result[key] = value
        return result
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True

# Load from environment variables or .env file
settings = Settings()

# Load environment-specific settings if available
env = os.getenv("ENVIRONMENT", "development")
env_settings_file = BASE_DIR / f"config.{env}.json"

if env_settings_file.exists():
    try:
        with open(env_settings_file, "r") as f:
            env_settings = json.load(f)
            
        # Update settings with environment-specific values
        for key, value in env_settings.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
                
        print(f"Loaded environment-specific settings from {env_settings_file}")
    except Exception as e:
        print(f"Error loading environment-specific settings: {e}")
