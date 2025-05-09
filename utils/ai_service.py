"""
AI API service utilities for handling interactions with Gemini AI.
"""
from typing import Dict, Any, Optional, List
import google.generativeai as genai
import time # Added for retry logic
import random # Added for jitter in retry logic

from utils.config import (
    GEMINI_API_KEY,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P
)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

class AIService:
    """Service class for handling interactions with AI models."""
    
    MAX_RETRIES = 3 # Maximum number of retries for API calls
    INITIAL_BACKOFF = 1  # Initial backoff time in seconds

    @staticmethod
    def get_gemini_model(model_name: str = DEFAULT_MODEL,
                       temperature: float = DEFAULT_TEMPERATURE,
                       max_tokens: int = DEFAULT_MAX_TOKENS,
                       top_p: float = DEFAULT_TOP_P) -> genai.GenerativeModel:
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
        return genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": top_p,
            }
        )
    
    @staticmethod
    def generate_response(prompt: str, 
                        model_name: str = DEFAULT_MODEL, 
                        temperature: float = DEFAULT_TEMPERATURE,
                        max_tokens: int = DEFAULT_MAX_TOKENS,
                        top_p: float = DEFAULT_TOP_P) -> str:
        """
        Generate a response from the AI model.
        
        Args:
            prompt: The prompt to send to the model
            model_name: Name of the Gemini model to use
            temperature: Controls randomness (higher = more random)
            max_tokens: Maximum number of tokens to generate
            top_p: Nucleus sampling parameter
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If there's an error in generating the response
        """
        retries = 0
        backoff_time = AIService.INITIAL_BACKOFF
        
        while retries < AIService.MAX_RETRIES:
            try:
                model = AIService.get_gemini_model(
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p
                )
                
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                retries += 1
                print(f"Error generating AI response (attempt {retries}/{AIService.MAX_RETRIES}): {str(e)}")
                if retries >= AIService.MAX_RETRIES:
                    print("Max retries reached. Raising exception.")
                    raise
                
                # Exponential backoff with jitter
                sleep_time = backoff_time + random.uniform(0, 1)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                backoff_time *= 2 # Double the backoff time for the next retry
        
        # This part should ideally not be reached if MAX_RETRIES is handled correctly above
        print("Error generating AI response after multiple retries.")
        raise Exception("Failed to generate AI response after multiple retries.")
