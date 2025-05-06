import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from utils.ai_service import AIService
from utils.config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P,
    MAX_HISTORY_MESSAGES
)
from mcp_server import get_default_server

class AgenticCharacter:
    """An agentic character that can take actions using MCP tools"""
    
    def __init__(self, character_data: Dict[str, Any]):
        """
        Initialize with character data from the JSON file.
        
        Args:
            character_data: Dictionary containing character data
        """
        self.name = character_data["name"]
        self.background = character_data.get("background", "")
        self.personality = character_data.get("personality", "")
        self.wiki_info = character_data.get("wiki_info", "")
        self.prompt = character_data.get("prompt", "")
        self.chat_history = character_data.get("chat_history", [])
        self.mcp_server = get_default_server()
        
        # Add agentic capabilities to the prompt
        self._enhance_prompt_with_capabilities()
    
    def _enhance_prompt_with_capabilities(self):
        """Add information about available tools to the character prompt"""
        tools_info = self.mcp_server.get_tools_info()
        
        tools_description = "\n\nTools You Can Use:\n"
        for tool in tools_info:
            tools_description += f"- {tool['name']}: {tool['description']}\n"
        
        tools_description += "\nWhen you want to use a tool, you should respond in this format:\n"
        tools_description += "<action>\n"
        tools_description += "  <tool>tool_name</tool>\n"
        tools_description += "  <args>{\"parameter1\": \"value1\", \"parameter2\": \"value2\"}</args>\n"
        tools_description += "  <reason>My reason for using this tool...</reason>\n"
        tools_description += "</action>\n\n"
        
        # Tool specific examples - make it clearer
        tools_description += "Example Uses:\n\n"
        
        # Weather example
        tools_description += "1. For weather information:\n"
        tools_description += "<action>\n"
        tools_description += "  <tool>get_weather</tool>\n"
        tools_description += "  <args>{\"location\": \"Istanbul\"}</args>\n"
        tools_description += "  <reason>I'm getting this information because the user asked about the weather.</reason>\n"
        tools_description += "</action>\n\n"
        
        # Wikipedia example
        tools_description += "2. For Wikipedia search:\n"
        tools_description += "<action>\n"
        tools_description += "  <tool>search_wikipedia</tool>\n"
        tools_description += "  <args>{\"query\": \"Albert Einstein\", \"language\": \"en\"}</args>\n"
        tools_description += "  <reason>The user requested information on this topic.</reason>\n"
        tools_description += "</action>\n\n"
        
        # Time example
        tools_description += "3. For time/date information:\n"
        tools_description += "<action>\n"
        tools_description += "  <tool>get_current_time</tool>\n"
        tools_description += "  <args>{}</args>\n"
        tools_description += "  <reason>I'm answering because the user asked for the time.</reason>\n"
        tools_description += "</action>\n\n"
        
        # Math example
        tools_description += "4. For mathematical calculations:\n"
        tools_description += "<action>\n"
        tools_description += "  <tool>calculate_math</tool>\n"
        tools_description += "  <args>{\"expression\": \"2+2*3\"}</args>\n"
        tools_description += "  <reason>I'm calculating the mathematical expression requested by the user.</reason>\n"
        tools_description += "</action>\n\n"
        
        tools_description += "IMPORTANT: Always use valid JSON format in the args section. Don't forget quotation marks and use escape characters correctly.\n\n"
        tools_description += "If you just want to chat, you can respond normally."
        
        self.prompt += tools_description
    
    def process_response(self, response: str) -> Dict[str, Any]:
        """
        Process the model's response to extract any actions
        Returns a dictionary with the processed response and action results
        """
        # Check if the response contains an action
        action_match = re.search(r'<action>(.*?)</action>', response, re.DOTALL)
        
        if not action_match:
            # No action, just a regular response
            return {
                "type": "text",
                "content": response
            }
        
        action_text = action_match.group(1)
        
        # Extract tool, args, and reason
        tool_match = re.search(r'<tool>(.*?)</tool>', action_text, re.DOTALL)
        args_match = re.search(r'<args>(.*?)</args>', action_text, re.DOTALL)
        reason_match = re.search(r'<reason>(.*?)</reason>', action_text, re.DOTALL)
        
        if not tool_match or not args_match:
            # Malformed action, return the original response
            return {
                "type": "text",
                "content": response
            }
        
        tool_name = tool_match.group(1).strip()
        args_text = args_match.group(1).strip()
        reason = reason_match.group(1).strip() if reason_match else "No reason provided"
        
        try:
            # Parse the args as JSON (handle empty args case)
            if args_text.strip() == '{}' or not args_text.strip():
                args = {}
            else:
                # Try to fix common JSON formatting issues
                # Replace single quotes with double quotes
                fixed_args_text = args_text.replace("'", "\"")
                # Fix unquoted keys
                fixed_args_text = re.sub(r'(\w+):', r'"\1":', fixed_args_text)
                
                try:
                    args = json.loads(fixed_args_text)
                except:
                    # If fixing didn't work, try the original
                    args = json.loads(args_text)
            
            # Execute the tool
            result = self.mcp_server.execute_tool(tool_name, args)
            
            # Remove the action from the response
            clean_response = response.replace(action_match.group(0), "").strip()
            
            return {
                "type": "action",
                "content": clean_response,
                "tool": tool_name,
                "args": args,
                "reason": reason,
                "result": result
            }
            
        except json.JSONDecodeError:
            # Malformed JSON in args
            return {
                "type": "error",
                "content": "The tool parameters are not in valid JSON format.",
                "original_response": response
            }
        except Exception as e:
            # Other errors
            return {
                "type": "error",
                "content": f"An error occurred while running the tool: {str(e)}",
                "original_response": response
            }
    
    def get_response(self, user_message: str) -> Dict[str, Any]:
        """
        Get a response from the character for the given user message
        The response may include actions that are executed using MCP tools
        """
        try:
            # Prepare conversation history context
            history_text = ""
            if self.chat_history:
                # Include configured number of messages for context
                for msg in self.chat_history[-MAX_HISTORY_MESSAGES:]:
                    if msg["role"] == "user":
                        history_text += f"User: {msg['content']}\n"
                    else:
                        history_text += f"{self.name}: {msg['content']}\n"
            
            # Create the full prompt for the model
            full_prompt = f"""{self.prompt}

Chat history:
{history_text}

User: {user_message}
{self.name}:"""
            
            # Generate the response using the AIService
            response_text = AIService.generate_response(
                prompt=full_prompt,
                model_name=DEFAULT_MODEL,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_MAX_TOKENS,
                top_p=DEFAULT_TOP_P
            )
            
            # Process the response to handle any actions
            processed_response = self.process_response(response_text)
            
            # Add to chat history
            self.chat_history.append({"role": "user", "content": user_message})
            
            if processed_response["type"] == "action":
                # For actions, first get the raw tool results
                action_result = processed_response["result"]
                tool_name = processed_response["tool"]
                
                # Convert the tool result to a human-readable format
                result_info = ""
                
                if tool_name == "get_weather":
                    location = action_result.get("location", "")
                    temp = action_result.get("temperature", "")
                    condition = action_result.get("condition", "")
                    humidity = action_result.get("humidity", "")
                    result_info = f"The weather in {location} is {temp} degrees, {condition}. Humidity: {humidity}%."
                
                elif tool_name == "search_wikipedia":
                    summary = action_result.get("summary", "")
                    result_info = summary
                
                elif tool_name == "get_current_time":
                    time = action_result.get("current_time", "")
                    result_info = f"The current time is {time}."
                
                elif tool_name == "calculate_math":
                    expression = action_result.get("expression", "")
                    result = action_result.get("result", "")
                    result_info = f"The result of {expression} is {result}."
                
                elif tool_name == "open_website":
                    status = action_result.get("status", "")
                    url = action_result.get("message", "").replace("Opened ", "").replace(" in browser", "")
                    if status == "success":
                        result_info = f"The website {url} has been opened."
                
                # For any other tools or as a fallback
                else:
                    result_info = json.dumps(action_result, ensure_ascii=False)
                
                # Now create a second prompt to get the character to respond in their own style
                character_context = f"""
Respond to the following information with your own personality and speaking style, as the character {self.name}.
This is information provided by a tool, but give your answer naturally.
Information you have: {result_info}

Convey this information to the user in a natural conversation, appropriate to your personality.
Don't add explanations like "I am" or "{self.name}" at the beginning of your answer, just respond as if in conversation.
"""
                
                # Create a new prompt for styled response
                styled_prompt = f"""{self.prompt}

User: {user_message}

{character_context}

{self.name}:"""
                
                try:
                    # Get a styled response from the model using AIService
                    formatted_result = AIService.generate_response(
                        prompt=styled_prompt,
                        model_name=DEFAULT_MODEL,
                        temperature=DEFAULT_TEMPERATURE,
                        max_tokens=DEFAULT_MAX_TOKENS,
                        top_p=DEFAULT_TOP_P
                    )
                except Exception as e:
                    # Fallback to a simple formatted response if there's an error
                    formatted_result = f"{processed_response['content']} {result_info}"
                
                self.chat_history.append({
                    "role": "assistant", 
                    "content": formatted_result,
                    "action": {
                        "tool": tool_name,
                        "args": processed_response["args"],
                        "result": action_result
                    }
                })
                
                processed_response["display_text"] = formatted_result
            else:
                # For regular text responses, just store the text
                self.chat_history.append({
                    "role": "assistant", 
                    "content": processed_response["content"]
                })
                
                processed_response["display_text"] = processed_response["content"]
            
            return processed_response
            
        except Exception as e:
            error_message = f"An error occurred while generating a response: {str(e)}"
            self.chat_history.append({
                "role": "assistant", 
                "content": error_message
            })
            return {
                "type": "error",
                "content": error_message,
                "display_text": error_message
            }
    
    def save(self, data_dir: Path) -> Path:
        """Save the character data to a JSON file"""
        character_data = {
            "name": self.name,
            "background": self.background,
            "personality": self.personality,
            "wiki_info": self.wiki_info,
            "prompt": self.prompt,
            "chat_history": self.chat_history
        }
        
        file_path = data_dir / f"{self.name.lower().replace(' ', '_')}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(character_data, f, ensure_ascii=False, indent=4)
        
        return file_path
    
    @classmethod
    def load(cls, file_path: Path) -> 'AgenticCharacter':
        """Load a character from a JSON file"""
        with open(file_path, "r", encoding="utf-8") as f:
            character_data = json.load(f)
        
        return cls(character_data)
    
    @classmethod
    def from_character_data(cls, data_dir: Path, character_name: str) -> Optional['AgenticCharacter']:
        """Create an AgenticCharacter from a stored character file"""
        file_path = data_dir / f"{character_name.lower().replace(' ', '_')}.json"
        if file_path.exists():
            return cls.load(file_path)
        return None
