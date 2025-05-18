"""
Launcher for the Agentic Character Chatbot backend API.
This serves as the entry point to run the FastAPI application.
"""
import sys
import os
import uvicorn
from pathlib import Path
from sqlalchemy.orm import Session

# Ensure the current directory is in path for imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir.parent))  # Also add parent for any legacy imports

# Environment setup
from dotenv import load_dotenv
load_dotenv()

def init_database():
    """
    Initialize and migrate the database.
    """
    from app.db.init_db import create_tables, migrate_character_data, migrate_chat_history
    from app.db.base import SessionLocal
    
    print("Initializing database...")
    # Create tables
    create_tables()
    
    # Migrate existing character data
    print("Checking for character data to migrate...")
    db = SessionLocal()
    try:
        # Migrate character data from JSON files
        migrated_chars = migrate_character_data(db)
        
        # Migrate existing chat history to conversations
        print("Migrating existing chat history to conversations...")
        migrated_convs = migrate_chat_history(db)
        
        print(f"Database initialization complete. Migrated {migrated_chars} characters and {migrated_convs} conversations.")
    except Exception as e:
        print(f"Error during database migration: {e}")
    finally:
        db.close()

def main():
    """
    Launch the FastAPI backend application.
    """
    print("Starting Agentic Character Chatbot Backend API...")
    
    # Initialize the database
    init_database()
    
    # Create necessary directories if they don't exist
    # Keep character_data directory for backward compatibility
    data_dir = current_dir / "character_data" 
    data_dir.mkdir(exist_ok=True)

    # Make sure dynamic tools directory exists
    dynamic_tools_dir = current_dir / "tools" / "dynamic"
    dynamic_tools_dir.mkdir(exist_ok=True)

    # Ensure dynamic tools has an __init__.py file
    init_file = dynamic_tools_dir / "__init__.py"
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write("# Dynamic tools package\n")
    
    # Start the FastAPI server
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",  # Accessible from any network interface
        port=8000,       # Standard port for API services
        reload=True,     # Auto-reload on code changes - useful for development
        app_dir=current_dir  # Set the application directory to the current directory
    )

if __name__ == "__main__":
    main()
