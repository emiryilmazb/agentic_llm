import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from utils.ai_service import AIService
from utils.config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P,
    MAX_HISTORY_MESSAGES
)
from mcp_server import get_default_server
from utils.dynamic_tool_manager import DynamicToolManager

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
        
        # Add information about dynamic tool creation
        tools_description += "\n\nDYNAMIC TOOL CREATION:\n"
        tools_description += "If you need a tool that doesn't exist yet, you can indicate this in your response. "
        tools_description += "The system will attempt to create a new tool based on the user's needs. "
        tools_description += "For example, if the user asks about currency conversion and we don't have a tool for that, "
        tools_description += "you can respond with something like:\n\n"
        tools_description += "\"I don't have a tool for currency conversion yet, but I can create one for you. Let me do that...\"\n\n"
        tools_description += "The system will then try to create a new tool that can handle currency conversion. "
        tools_description += "Once the tool is created, you'll be informed and can use it like any other tool."
        
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
            
            # Check if the tool exists in the MCP server
            mcp_server = get_default_server()
            tools_info = mcp_server.get_tools_info()
            tool_exists = any(tool["name"] == tool_name for tool in tools_info)
            
            # Check if this tool was previously deleted
            deleted_tools = []
            deleted_tools_path = Path("dynamic_tools/deleted_tools.json")
            if deleted_tools_path.exists():
                try:
                    with open(deleted_tools_path, "r", encoding="utf-8") as f:
                        deleted_tools = json.load(f)
                except json.JSONDecodeError:
                    deleted_tools = []
            
            # If the tool was deleted or doesn't exist, try to create a new one
            if tool_name in deleted_tools or not tool_exists:
                print(f"Tool '{tool_name}' not found or was deleted, attempting to create a new one...")
                
                # Determine the type of tool needed based on the name and args
                tool_type = None
                if "currency" in tool_name.lower() or "exchange" in tool_name.lower() or "döviz" in tool_name.lower():
                    tool_type = "currency"
                elif "weather" in tool_name.lower() or "forecast" in tool_name.lower() or "hava" in tool_name.lower():
                    tool_type = "weather"
                elif "location" in tool_name.lower() or "konum" in tool_name.lower():
                    tool_type = "location"
                
                # Create a message that would trigger the creation of this type of tool
                trigger_message = ""
                if tool_type == "currency":
                    from_currency = args.get("from_currency", "USD")
                    to_currency = args.get("to_currency", "TRY")
                    amount = args.get("amount", 1)
                    trigger_message = f"What is {amount} {from_currency} in {to_currency}?"
                elif tool_type == "weather":
                    location = args.get("location", "Istanbul")
                    days = args.get("days", 3)
                    trigger_message = f"What's the weather forecast for {location} for the next {days} days?"
                elif tool_type == "location":
                    trigger_message = "What is my current location?"
                else:
                    trigger_message = f"I need a tool for {tool_name}"
                
                # Try to create the tool
                success, created_tool_name, _ = DynamicToolManager.create_and_register_tool(trigger_message)
                
                if success and created_tool_name:
                    print(f"Successfully created new tool: {created_tool_name}")
                    tool_name = created_tool_name
                else:
                    return {
                        "type": "error",
                        "content": f"The tool '{tool_name}' is not available and could not be created.",
                        "original_response": response
                    }
            
            # Eğer araç retrieve_first_message ise, sohbet geçmişini aktar
            if tool_name == "retrieve_first_message":
                # Önce aracı al
                tool = self.mcp_server.tools.get(tool_name)
                if tool and hasattr(tool, "set_conversation_history"):
                    # Sohbet geçmişini aktar
                    tool.set_conversation_history(self.chat_history)
            
            # Execute the tool
            result = self.mcp_server.execute_tool(tool_name, args)
            
            # Check if there was an error in the result
            if "error" in result:
                print(f"Error executing tool: {result['error']}")
                
                # Try to fix common errors
                if "from_currency" in args and "to_currency" in args:
                    # Fix currency codes
                    if args["from_currency"].lower() == "dolar":
                        args["from_currency"] = "USD"
                    elif args["from_currency"].lower() == "euro":
                        args["from_currency"] = "EUR"
                    
                    if args["to_currency"].lower() in ["tl", "türk lirası", "lira"]:
                        args["to_currency"] = "TRY"
                    
                    # Eğer araç retrieve_first_message ise, sohbet geçmişini aktar
                    if tool_name == "retrieve_first_message":
                        # Önce aracı al
                        tool = self.mcp_server.tools.get(tool_name)
                        if tool and hasattr(tool, "set_conversation_history"):
                            # Sohbet geçmişini aktar
                            tool.set_conversation_history(self.chat_history)
                    
                    # Try again with fixed args
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
            print(f"Exception in process_response: {str(e)}")
            return {
                "type": "error",
                "content": f"An error occurred while running the tool: {str(e)}",
                "original_response": response
            }
    
    def get_response(self, user_message: str) -> Dict[str, Any]:
        """
        Get a response from the character for the given user message
        The response may include actions that are executed using MCP tools
        If no existing tool can handle the request, a new tool may be dynamically created
        """
        try:
            # Check if we need to create a new tool for this request
            created_tool, tool_name, tool_info = self._check_and_create_tool(user_message)
            
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

            # If a new tool was created, add information about it to the prompt
            # and provide a specific instruction to use it
            if created_tool and tool_name:
                # Determine what kind of tool was created and provide specific instructions
                tool_usage_example = ""
                if "currency" in tool_name.lower() or "döviz" in tool_name.lower():
                    tool_usage_example = f"""
<action>
  <tool>{tool_name}</tool>
  <args>{{"from_currency": "USD", "to_currency": "TRY", "amount": 1}}</args>
  <reason>The user asked about currency conversion between USD and TRY.</reason>
</action>
"""
                elif "weather" in tool_name.lower() or "hava" in tool_name.lower():
                    tool_usage_example = f"""
<action>
  <tool>{tool_name}</tool>
  <args>{{"location": "Istanbul", "days": 3}}</args>
  <reason>The user asked about the weather forecast for Istanbul.</reason>
</action>
"""
                
                elif "location" in tool_name.lower() or "konum" in tool_name.lower():
                    tool_usage_example = f"""
<action>
  <tool>{tool_name}</tool>
  <args>{{}}</args>
  <reason>The user asked for their current location.</reason>
</action>
"""
                
                full_prompt = f"""{self.prompt}

I just created a new tool called "{tool_name}" that can help with this request.
This tool was created specifically to handle the user's current request.
I MUST use this tool to provide the most accurate and up-to-date information.

Here's an example of how to use this tool:
{tool_usage_example}

I should respond with an action using this tool to answer the user's question.

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
                
                elif tool_name == "currency_converter":
                    # Handle currency conversion results
                    if "error" in action_result:
                        result_info = f"Error: {action_result['error']}"
                    else:
                        from_currency = action_result.get("from_currency", "")
                        to_currency = action_result.get("to_currency", "")
                        amount = action_result.get("amount", 1)
                        rate = action_result.get("rate", 0)
                        converted_amount = action_result.get("converted_amount", 0)
                        last_updated = action_result.get("last_updated", "")
                        
                        result_info = f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}. "
                        result_info += f"The exchange rate is 1 {from_currency} = {rate:.4f} {to_currency}. "
                        if last_updated:
                            result_info += f"Last updated: {last_updated}."
                
                elif tool_name == "weather_forecast":
                    # Handle weather forecast results
                    if "error" in action_result:
                        result_info = f"Error: {action_result['error']}"
                    else:
                        location = action_result.get("location", "")
                        forecast = action_result.get("forecast", [])
                        units = action_result.get("units", {})
                        
                        result_info = f"Weather forecast for {location}:\n\n"
                        
                        for day in forecast:
                            date = day.get("date", "")
                            max_temp = day.get("max_temp", "")
                            min_temp = day.get("min_temp", "")
                            weather = day.get("weather", "")
                            precipitation = day.get("precipitation", "")
                            
                            result_info += f"Date: {date}\n"
                            result_info += f"Temperature: {min_temp}-{max_temp}{units.get('temperature', '°C')}\n"
                            result_info += f"Weather: {weather}\n"
                            result_info += f"Precipitation: {precipitation}{units.get('precipitation', 'mm')}\n\n"
                
                elif tool_name == "get_current_location":
                    if "error" in action_result:
                        result_info = f"Error: {action_result['error']}"
                    elif action_result.get("status") == "success" and "location" in action_result:
                        loc = action_result["location"]
                        result_info = (
                            f"I've found a location: {loc.get('city', 'N/A')}, {loc.get('state', 'N/A')}, {loc.get('country', 'N/A')} "
                            f"(Lat: {loc.get('latitude', 'N/A')}, Lon: {loc.get('longitude', 'N/A')}). "
                            "Please note that this is a placeholder location as I cannot access your real-time GPS data for privacy reasons."
                        )
                    else:
                        result_info = "I couldn't determine the location information from the tool's response."
                
                # For any other tools or as a fallback
                else:
                    # Try to extract meaningful information from the result
                    if isinstance(action_result, dict):
                        # Filter out error messages
                        if "error" in action_result:
                            result_info = f"Error: {action_result['error']}"
                        else:
                            # Try to create a readable summary
                            readable_parts = []
                            for key, value in action_result.items():
                                if key not in ["status", "message", "error"]: # Exclude common status keys
                                    readable_parts.append(f"{key.replace('_', ' ').title()}: {value}")
                            
                            if readable_parts:
                                result_info = ". ".join(readable_parts)
                                if not result_info: # If all keys were status keys
                                     result_info = json.dumps(action_result, ensure_ascii=False, indent=2)
                            else: # Should not happen if action_result is not empty and not an error
                                result_info = json.dumps(action_result, ensure_ascii=False, indent=2)
                    else: # If action_result is not a dict (e.g. a string or number)
                        result_info = str(action_result)
                
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
    
    def _check_and_create_tool(self, user_message: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Check if a new tool needs to be created for the user's message and create it if needed.
        
        Args:
            user_message: The user's message
            
        Returns:
            Tuple of (success, tool_name, tool_info)
        """
        try:
            # Check for deleted tools to avoid recreating them with the same name
            deleted_tools = []
            deleted_tools_path = Path("dynamic_tools/deleted_tools.json")
            if deleted_tools_path.exists():
                try:
                    with open(deleted_tools_path, "r", encoding="utf-8") as f:
                        deleted_tools = json.load(f)
                except json.JSONDecodeError:
                    deleted_tools = []
            
            # Extract key information from the user message to help with tool creation
            message_lower = user_message.lower()
            
            # Currency conversion patterns
            currency_patterns = {
                "from_currency": ["dolar", "dollar", "usd", "euro", "eur", "pound", "gbp", "yen", "jpy"],
                "to_currency": ["tl", "türk lirası", "lira", "try"]
            }
            
            # Weather forecast patterns
            weather_patterns = {
                "location": ["istanbul", "ankara", "izmir", "tokyo", "new york", "london", "paris"],
                "days": ["bugün", "yarın", "hafta", "week", "gün", "day"]
            }
            
            # Check if the message contains currency conversion request
            if any(term in message_lower for term in ["dolar", "euro", "tl", "kur", "döviz", "para birimi", "currency", "exchange"]):
                # Extract potential currency information to help with tool creation
                extracted_info = {"type": "currency"}
                for currency in currency_patterns["from_currency"]:
                    if currency in message_lower:
                        extracted_info["from_currency"] = currency.upper()
                        if currency == "dolar" or currency == "dollar":
                            extracted_info["from_currency"] = "USD"
                        break
                
                for currency in currency_patterns["to_currency"]:
                    if currency in message_lower:
                        extracted_info["to_currency"] = currency.upper()
                        if currency == "tl" or "lira" in currency:
                            extracted_info["to_currency"] = "TRY"
                        break
                
                # Use the DynamicToolManager to create and register a currency tool
                success, tool_name, tool_info = DynamicToolManager.create_and_register_tool(user_message)
                
                # If successful, return the result
                if success and tool_name:
                    return success, tool_name, tool_info
            
            # Check if the message contains weather forecast request
            elif any(term in message_lower for term in ["hava", "weather", "forecast", "sıcaklık", "temperature"]):
                # Extract potential location information to help with tool creation
                extracted_info = {"type": "weather"}
                for location in weather_patterns["location"]:
                    if location in message_lower:
                        extracted_info["location"] = location
                        break
                
                # Use the DynamicToolManager to create and register a weather tool
                success, tool_name, tool_info = DynamicToolManager.create_and_register_tool(user_message)
                
                # If successful, return the result
                if success and tool_name:
                    return success, tool_name, tool_info
            
            # For other types of requests, use the general approach
            return DynamicToolManager.create_and_register_tool(user_message)
        except Exception as e:
            print(f"Error checking and creating tool: {str(e)}")
            return False, None, None
    
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
