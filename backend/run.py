"""
Simple launcher script to run the FastAPI backend.
"""
import os
import sys
from pathlib import Path

def main():
    """
    Run the backend FastAPI application
    """
    print("Starting Agentic Character Chatbot Backend...")
    
    # Get the current directory (backend/)
    current_dir = Path(__file__).parent
    
    # Add app to path for imports
    app_dir = current_dir / "app"
    sys.path.append(str(app_dir))
    
    # Change to app directory
    os.chdir(app_dir)
    
    # Execute the backend.py script
    os.system("python backend.py")

if __name__ == "__main__":
    main()
