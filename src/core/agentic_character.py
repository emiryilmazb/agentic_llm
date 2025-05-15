"""
Agentic Character Implementation.

This module provides the implementation of an agentic character that can
take actions using MCP tools.
"""
import json
import re
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from src.api.ai_service import AIService
from src.utils.config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P,
    MAX_HISTORY_MESSAGES,
    ENABLE_DYNAMIC_TOOLS
)
from src.core.mcp_server import get_default_server
from src.tools.dynamic.tool_manager import DynamicToolManager

# Create a logger for this module
logger = logging.getLogger(__name__)

class AgenticCharacter:
    """
    An agentic character that can take actions using MCP tools.
    
    This class represents a character that can use tools to perform actions
    in response to user messages.
    """
    
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
        
        logger.info(f"Initialized agentic character: {self.name}")
        
        # Add agentic capabilities to the prompt
        self._enhance_prompt_with_capabilities()
    
    def _enhance_prompt_with_capabilities(self):
        """Add information about available tools to the character prompt."""
        logger.debug(f"Enhancing prompt with capabilities for: {self.name}")
        
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
        
        # Add information about dynamic tool creation if enabled
        if ENABLE_DYNAMIC_TOOLS:
            tools_description += "\n\nDYNAMIC TOOL CREATION:\n"
            tools_description += "If you need a tool that doesn't exist yet, you can indicate this in your response. "
            tools_description += "The system will attempt to create a new tool based on the user's needs. "
            tools_description += "For example, if the user asks about currency conversion and we don't have a tool for that, "
            tools_description += "you can respond with something like:\n\n"
            tools_description += "\"I don't have a tool for currency conversion yet, but I can create one for you. Let me do that...\"\n\n"
            tools_description += "The system will then try to create a new tool that can handle currency conversion. "
            tools_description += "Once the tool is created, you'll be informed and can use it like any other tool."
        
        self.prompt += tools_description
        logger.debug(f"Enhanced prompt for {self.name} (new length: {len(self.prompt)} characters)")
    
    def process_response(self, response: str) -> Dict[str, Any]:
        """
        Process the model's response to extract any actions.
        
        Args:
            response: The raw response from the AI model
            
        Returns:
            Dictionary with the processed response and action results
        """
        logger.debug(f"Processing response for {self.name}")
        
        # Check if the response contains an action
        action_match = re.search(r'<action>(.*?)</action>', response, re.DOTALL)
        
        if not action_match:
            # No action, just a regular response
            logger.debug("No action found in response")
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
            logger.warning("Malformed action in response")
            return {
                "type": "text",
                "content": response
            }
        
        tool_name = tool_match.group(1).strip()
        args_text = args_match.group(1).strip()
        reason = reason_match.group(1).strip() if reason_match else "No reason provided"
        
        logger.info(f"Found action: tool={tool_name}, reason={reason}")
        
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
                    logger.debug(f"Parsed args with fixes: {args}")
                except:
                    # If fixing didn't work, try the original
                    args = json.loads(args_text)
                    logger.debug(f"Parsed original args: {args}")
            
            # Check if the tool exists in the MCP server
            mcp_server = get_default_server()
            tools_info = mcp_server.get_tools_info()
            tool_exists = any(tool["name"] == tool_name for tool in tools_info)
            
            # Check if this tool was previously deleted
            deleted_tools = []
            deleted_tools_path = Path("src/tools/dynamic/deleted_tools.json")
            if deleted_tools_path.exists():
                try:
                    with open(deleted_tools_path, "r", encoding="utf-8") as f:
                        deleted_tools = json.load(f)
                except json.JSONDecodeError:
                    deleted_tools = []
            
            # If the tool was deleted or doesn't exist, try to create a new one
            if ENABLE_DYNAMIC_TOOLS and (tool_name in deleted_tools or not tool_exists):
                logger.info(f"Tool '{tool_name}' not found or was deleted, attempting to create a new one...")
                
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
                    logger.info(f"Successfully created new tool: {created_tool_name}")
                    tool_name = created_tool_name
                else:
                    logger.error(f"Failed to create tool for: {tool_name}")
                    return {
                        "type": "error",
                        "content": f"The tool '{tool_name}' is not available and could not be created.",
                        "original_response": response
                    }
            
            # If the tool is retrieve_first_message, pass the chat history
            if tool_name == "retrieve_first_message":
                # Get the tool
                tool = self.mcp_server.get_tool(tool_name)
                if tool and hasattr(tool, "set_conversation_history"):
                    # Pass the chat history
                    tool.set_conversation_history(self.chat_history)
                    logger.debug("Passed chat history to retrieve_first_message tool")
            
            # Execute the tool
            logger.info(f"Executing tool: {tool_name}")
            result = self.mcp_server.execute_tool(tool_name, args)
            
            # Check if there was an error in the result
            if "error" in result:
                logger.warning(f"Error executing tool: {result['error']}")
                
                # Try to fix common errors
                if "from_currency" in args and "to_currency" in args:
                    # Fix currency codes
                    if args["from_currency"].lower() == "dolar":
                        args["from_currency"] = "USD"
                    elif args["from_currency"].lower() == "euro":
                        args["from_currency"] = "EUR"
                    
                    if args["to_currency"].lower() in ["tl", "türk lirası", "lira"]:
                        args["to_currency"] = "TRY"
                    
                    # If the tool is retrieve_first_message, pass the chat history
                    if tool_name == "retrieve_first_message":
                        # Get the tool
                        tool = self.mcp_server.get_tool(tool_name)
                        if tool and hasattr(tool, "set_conversation_history"):
                            # Pass the chat history
                            tool.set_conversation_history(self.chat_history)
                    
                    # Try again with fixed args
                    logger.info(f"Retrying tool with fixed args: {args}")
                    result = self.mcp_server.execute_tool(tool_name, args)
            
            # Remove the action from the response
            clean_response = response.replace(action_match.group(0), "").strip()
            
            logger.debug(f"Tool execution successful: {tool_name}")
            return {
                "type": "action",
                "content": clean_response,
                "tool": tool_name,
                "args": args,
                "reason": reason,
                "result": result
            }
            
        except json.JSONDecodeError as e:
            # Malformed JSON in args
            logger.error(f"JSON decode error in args: {str(e)}")
            return {
                "type": "error",
                "content": "The tool parameters are not in valid JSON format.",
                "original_response": response
            }
        except Exception as e:
            # Other errors
            logger.error(f"Exception in process_response: {str(e)}", exc_info=True)
            return {
                "type": "error",
                "content": f"An error occurred while running the tool: {str(e)}",
                "original_response": response
            }
    
    def get_response(self, user_message: str) -> Dict[str, Any]:
        """
        Get a response from the character for the given user message.
        
        The response may include actions that are executed using MCP tools.
        If no existing tool can handle the request, a new tool may be dynamically created.
        
        Args:
            user_message: The user's message
            
        Returns:
            Dictionary containing the response and any action results
        """
        logger.info(f"Getting response for user message: {user_message[:50]}...")
        
        try:
            # Check if we need to create a new tool for this request
            created_tool = False
            tool_name = None
            tool_info = None
            
            if ENABLE_DYNAMIC_TOOLS:
                created_tool, tool_name, tool_info = self._check_and_create_tool(user_message)
                if created_tool:
                    logger.info(f"Created new tool for this request: {tool_name}")
            
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
            logger.debug("Generating AI response")
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
                result_info = self._format_tool_result(tool_name, action_result)
                
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
                    logger.debug("Generating styled response for tool result")
                    formatted_result = AIService.generate_response(
                        prompt=styled_prompt,
                        model_name=DEFAULT_MODEL,
                        temperature=DEFAULT_TEMPERATURE,
                        max_tokens=DEFAULT_MAX_TOKENS,
                        top_p=DEFAULT_TOP_P
                    )
                except Exception as e:
                    # Fallback to a simple formatted response if there's an error
                    logger.error(f"Error generating styled response: {str(e)}")
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
            
            logger.info(f"Generated response for user message (type: {processed_response['type']})")
            return processed_response
            
        except Exception as e:
            error_message = f"An error occurred while generating a response: {str(e)}"
            logger.error(error_message, exc_info=True)
            
            self.chat_history.append({
                "role": "assistant", 
                "content": error_message
            })
            
            return {
                "type": "error",
                "content": error_message,
                "display_text": error_message
            }
    
    def _format_tool_result(self, tool_name: str, action_result: Dict[str, Any]) -> str:
        """
        Format the tool result into a human-readable string.
        
        Args:
            tool_name: The name of the tool
            action_result: The result from the tool execution
            
        Returns:
            Formatted result string
        """
        logger.debug(f"Formatting result for tool: {tool_name}")
        
        # Handle error case
        if "error" in action_result:
            return f"Error: {action_result['error']}"
        
        # Format based on tool type
        if tool_name == "get_weather":
            location = action_result.get("location", "")
            temp = action_result.get("temperature", "")
            condition = action_result.get("condition", "")
            humidity = action_result.get("humidity", "")
            return f"The weather in {location} is {temp} degrees, {condition}. Humidity: {humidity}%."
        
        elif tool_name == "search_wikipedia":
            summary = action_result.get("summary", "")
            return summary
        
        elif tool_name == "get_current_time":
            time = action_result.get("current_time", "")
            return f"The current time is {time}."
        
        elif tool_name == "calculate_math":
            expression = action_result.get("expression", "")
            result = action_result.get("result", "")
            return f"The result of {expression} is {result}."
        
        elif tool_name == "open_website":
            status = action_result.get("status", "")
            url = action_result.get("message", "").replace("Opened ", "").replace(" in browser", "")
            if status == "success":
                return f"The website {url} has been opened."
        
        elif "currency" in tool_name.lower() or "exchange" in tool_name.lower():
            # Handle currency conversion results
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
            return result_info
        
        elif "weather" in tool_name.lower() or "forecast" in tool_name.lower():
            # Handle weather forecast results
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
            
            return result_info
        
        elif "location" in tool_name.lower():
            if "location" in action_result:
                loc = action_result["location"]
                return (
                    f"I've found a location: {loc.get('city', 'N/A')}, {loc.get('state', 'N/A')}, {loc.get('country', 'N/A')} "
                    f"(Lat: {loc.get('latitude', 'N/A')}, Lon: {loc.get('longitude', 'N/A')}). "
                    "Please note that this is a placeholder location as I cannot access your real-time GPS data for privacy reasons."
                )
        
        # For any other tools or as a fallback
        # Try to extract meaningful information from the result
        if isinstance(action_result, dict):
            # Try to create a readable summary
            readable_parts = []
            for key, value in action_result.items():
                if key not in ["status", "message", "error"]:  # Exclude common status keys
                    readable_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            
            if readable_parts:
                return ". ".join(readable_parts)
            else:  # If all keys were status keys
                return json.dumps(action_result, ensure_ascii=False, indent=2)
        else:  # If action_result is not a dict (e.g. a string or number)
            return str(action_result)
    
    def _check_and_create_tool(self, user_message: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Check if a new tool needs to be created for the user's message and create it if needed.
        
        Args:
            user_message: The user's message
            
        Returns:
            Tuple of (success, tool_name, tool_info)
        """
        if not ENABLE_DYNAMIC_TOOLS:
            logger.debug("Dynamic tool creation is disabled")
            return False, None, None
        
        logger.info("Checking if a new tool needs to be created")
        
        try:
            # Check for deleted tools to avoid recreating them with the same name
            deleted_tools = []
            deleted_tools_path = Path("src/tools/dynamic/deleted_tools.json")
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
                logger.debug("Detected potential currency conversion request")
                
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
                    logger.info(f"Created currency conversion tool: {tool_name}")
                    return success, tool_name, tool_info
            
            # Check if the message contains weather forecast request
            elif any(term in message_lower for term in ["hava", "weather", "forecast", "sıcaklık", "temperature"]):
                logger.debug("Detected potential weather forecast request")
                
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
                    logger.info(f"Created weather forecast tool: {tool_name}")
                    return success, tool_name, tool_info
            
            # For other types of requests, use the general approach
            return DynamicToolManager.create_and_register_tool(user_message)
        except Exception as e:
            logger.error(f"Error checking and creating tool: {str(e)}", exc_info=True)
            return False, None, None
    
    def save(self, data_dir: Path) -> Path:
        """
        Save the character data to a JSON file.
        
        Args:
            data_dir: Directory to save the character data
            
        Returns:
            Path to the saved file
        """
        logger.info(f"Saving character data for: {self.name}")
        
        character_data = {
            "name": self.name,
            "background": self.background,
            "personality": self.personality,
            "wiki_info": self.wiki_info,
            "prompt": self.prompt,
            "chat_history": self.chat_history,
            "modified_at": str(Path.ctime(Path.cwd()))
        }
        
        file_path = data_dir / f"{self.name.lower().replace(' ', '_')}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(character_data, f, ensure_ascii=False, indent=4)
        
        logger.debug(f"Character data saved to: {file_path}")
        return file_path
    
    @classmethod
    def load(cls, file_path: Path) -> 'AgenticCharacter':
        """
        Load a character from a JSON file.
        
        Args:
            file_path: Path to the character JSON file
            
        Returns:
            AgenticCharacter instance
        """
        logger.info(f"Loading character from file: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            character_data = json.load(f)
        
        return cls(character_data)
    
    @classmethod
    def from_character_data(cls, data_dir: Path, character_name: str) -> Optional['AgenticCharacter']:
        """
        Create an AgenticCharacter from a stored character file.
        
        Args:
            data_dir: Directory containing character data
            character_name: Name of the character to load
            
        Returns:
            AgenticCharacter instance or None if not found
        """
        logger.info(f"Creating AgenticCharacter from character data: {character_name}")
        
        file_path = data_dir / f"{character_name.lower().replace(' ', '_')}.json"
        if file_path.exists():
            return cls.load(file_path)
        
        logger.warning(f"Character file not found: {file_path}")
        return None