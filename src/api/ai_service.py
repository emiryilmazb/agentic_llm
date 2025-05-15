"""
AI API service utilities for handling interactions with Gemini AI.

This module provides a service class for interacting with the Google Generative AI API.
It handles API calls, error handling, and retry logic.
"""
from typing import Dict, Any, Optional, List, Union
import logging
import time
import random
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

from src.utils.config import (
    GEMINI_API_KEY,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P
)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Create a logger for this module
logger = logging.getLogger(__name__)

class AIService:
    """
    Service class for handling interactions with AI models.
    
    This class provides methods for generating responses from the Gemini AI model,
    with built-in error handling and retry logic.
    """
    
    MAX_RETRIES = 3  # Maximum number of retries for API calls
    INITIAL_BACKOFF = 1  # Initial backoff time in seconds
    MAX_BACKOFF = 32  # Maximum backoff time in seconds

    @staticmethod
    def get_gemini_model(
        model_name: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        top_p: float = DEFAULT_TOP_P
    ) -> genai.GenerativeModel:
        """
        Get a configured instance of the Gemini generative model.
        
        Args:
            model_name: Name of the Gemini model to use
            temperature: Controls randomness (higher = more random)
            max_tokens: Maximum number of tokens to generate
            top_p: Nucleus sampling parameter
            
        Returns:
            Configured GenerativeModel instance
        """
        logger.debug(f"Creating Gemini model instance: {model_name}")
        return genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": top_p,
            }
        )
    
    @staticmethod
    def generate_response(
        prompt: str, 
        model_name: str = DEFAULT_MODEL, 
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        top_p: float = DEFAULT_TOP_P
    ) -> str:
        """
        Generate a response from the AI model with retry logic.
        
        Args:
            prompt: The prompt to send to the model
            model_name: Name of the Gemini model to use
            temperature: Controls randomness (higher = more random)
            max_tokens: Maximum number of tokens to generate
            top_p: Nucleus sampling parameter
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If there's an error in generating the response after all retries
        """
        retries = 0
        backoff_time = AIService.INITIAL_BACKOFF
        
        while retries < AIService.MAX_RETRIES:
            try:
                logger.debug(f"Generating AI response (attempt {retries+1}/{AIService.MAX_RETRIES})")
                
                model = AIService.get_gemini_model(
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p
                )
                
                response = model.generate_content(prompt)
                logger.debug("Successfully generated AI response")
                return response.text
                
            except GoogleAPIError as e:
                retries += 1
                logger.warning(
                    f"Google API error generating AI response (attempt {retries}/{AIService.MAX_RETRIES}): {str(e)}"
                )
                
                if retries >= AIService.MAX_RETRIES:
                    logger.error("Max retries reached. Raising exception.")
                    raise
                
                # Exponential backoff with jitter
                jitter = random.uniform(0, 1)
                sleep_time = min(backoff_time + jitter, AIService.MAX_BACKOFF)
                logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                backoff_time *= 2  # Double the backoff time for the next retry
                
            except Exception as e:
                retries += 1
                logger.error(
                    f"Unexpected error generating AI response (attempt {retries}/{AIService.MAX_RETRIES}): {str(e)}"
                )
                
                if retries >= AIService.MAX_RETRIES:
                    logger.error("Max retries reached. Raising exception.")
                    raise
                
                # Exponential backoff with jitter for other errors too
                jitter = random.uniform(0, 1)
                sleep_time = min(backoff_time + jitter, AIService.MAX_BACKOFF)
                logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                backoff_time *= 2
        
        # This part should ideally not be reached if MAX_RETRIES is handled correctly above
        error_msg = "Failed to generate AI response after multiple retries."
        logger.critical(error_msg)
        raise Exception(error_msg)
    
    @staticmethod
    def generate_structured_response(
        prompt: str,
        response_format: Dict[str, Any],
        model_name: str = DEFAULT_MODEL,
        temperature: float = 0.2,  # Lower temperature for more deterministic structured responses
        max_tokens: int = DEFAULT_MAX_TOKENS,
        top_p: float = DEFAULT_TOP_P
    ) -> Dict[str, Any]:
        """
        Generate a structured response (e.g., JSON) from the AI model.
        
        Args:
            prompt: The prompt to send to the model
            response_format: Dictionary describing the expected response structure
            model_name: Name of the Gemini model to use
            temperature: Controls randomness (lower for structured responses)
            max_tokens: Maximum number of tokens to generate
            top_p: Nucleus sampling parameter
            
        Returns:
            Dictionary containing the structured response
            
        Raises:
            Exception: If there's an error in generating or parsing the response
        """
        # Add instructions for structured output to the prompt
        structured_prompt = f"""{prompt}

Please provide your response in the following JSON format:
{response_format}

Only respond with the JSON object, nothing else."""

        try:
            # Generate the response
            response_text = AIService.generate_response(
                prompt=structured_prompt,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p
            )
            
            # Extract and parse the JSON
            import re
            import json
            
            # Find JSON in the response
            json_match = re.search(r'({.*})', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON response: {str(e)}")
                    logger.debug(f"Response text: {response_text}")
                    raise Exception(f"Failed to parse structured response: {str(e)}")
            else:
                logger.error("No JSON found in the response")
                logger.debug(f"Response text: {response_text}")
                raise Exception("No structured data found in the response")
                
        except Exception as e:
            logger.error(f"Error generating structured response: {str(e)}")
            raise