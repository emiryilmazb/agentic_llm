from mcp_server import MCPTool
import requests
import json
import datetime
import re
from typing import Dict, Any, Optional, List
import os

class GetUserChildrenCountTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="get_user_children_count",
            description="Retrieves the number of children the user has. This requires storing and retrieving personal information about the user."
        )
        self.data_file = "user_children_data.json"
        self.user_data = self._load_data()

    def _load_data(self) -> Dict[str, int]:
        """Loads user data from the JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        else:
            return {}

    def _save_data(self) -> None:
        """Saves user data to the JSON file."""
        with open(self.data_file, "w") as f:
            json.dump(self.user_data, f)

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves or prompts for the number of children a user has."""
        user_id = args.get("user_id")  # Assuming user_id is passed in the arguments
        if not user_id:
            return {"error": "User ID is required."}

        if user_id in self.user_data:
            children_count = self.user_data[user_id]
            return {"children_count": children_count}
        else:
            return {"prompt_for_children": True, "user_id": user_id}

    def store_children_count(self, user_id: str, children_count: int) -> None:
        """Stores the number of children for a given user."""
        self.user_data[user_id] = children_count
        self._save_data()

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    tool = GetUserChildrenCountTool()

    # Simulate a user asking for their children count for the first time
    args1 = {"user_id": "user123"}
    result1 = tool.execute(args1)
    print(f"First request: {result1}")

    # Simulate the user providing the number of children
    if "prompt_for_children" in result1 and result1["prompt_for_children"]:
        children_count = 2  # Simulate user saying they have 2 children
        tool.store_children_count(result1["user_id"], children_count)
        print(f"Stored children count for user {result1['user_id']}: {children_count}")

    # Simulate the user asking again
    args2 = {"user_id": "user123"}
    result2 = tool.execute(args2)
    print(f"Second request: {result2}")

    # Simulate a different user asking for their children count for the first time
    args3 = {"user_id": "user456"}
    result3 = tool.execute(args3)
    print(f"Third request (new user): {result3}")