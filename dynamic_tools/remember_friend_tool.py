from mcp_server import MCPTool
import requests
import json
import datetime
import re
from typing import Dict, Any, Optional, List
import sqlite3

class RememberFriendTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="remember_friend",
            description="Remembers the user's best friend's name and stores it for future use."
        )
        self.db_path = "friend_data.db"
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS friends (
                user_id TEXT PRIMARY KEY,
                friend_name TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _store_friend(self, user_id: str, friend_name: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR REPLACE INTO friends (user_id, friend_name) VALUES (?, ?)", (user_id, friend_name))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error storing friend: {e}")
            return False
        finally:
            conn.close()

    def _retrieve_friend(self, user_id: str) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT friend_name FROM friends WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Error retrieving friend: {e}")
            return None
        finally:
            conn.close()

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if "friend_name" not in args:
            return {"status": "error", "message": "Missing required parameter: friend_name"}

        friend_name = args["friend_name"]

        # Assuming there's a way to get a user ID or session ID from the MCP server context.
        # For this example, we'll use a hardcoded user ID.  In a real implementation,
        # this would come from the server's user management system.
        user_id = "default_user"  # Replace with actual user ID retrieval logic

        if self._store_friend(user_id, friend_name):
            return {"status": "success", "message": f"Friend's name ({friend_name}) stored for user {user_id}."}
        else:
            return {"status": "error", "message": "Failed to store friend's name."}