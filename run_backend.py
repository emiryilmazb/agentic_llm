"""
Compatibility script to maintain backward compatibility with existing workflows.
This script now redirects to the backend/run.py implementation.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """
    Redirect to the new backend/run.py script
    """
    print("Note: Using the new project structure. Running backend/run.py...")
    print("For future use, please run: 'python backend/run.py' directly")
    
    # Get the path to the backend run.py
    backend_run_path = Path(__file__).parent / "backend" / "run.py"
    
    # Execute the backend run.py script using subprocess
    # This approach is more reliable across different environments
    result = subprocess.run([sys.executable, str(backend_run_path)], check=True)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
