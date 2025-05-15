#!/usr/bin/env python
"""
Agentic LLM - Main Application Entry Point

This script serves as the main entry point for the Agentic LLM application.
It initializes the necessary components and starts the Streamlit web interface.
"""
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the Streamlit app
from src.web.app import run_app

if __name__ == "__main__":
    # Run the Streamlit application
    run_app()