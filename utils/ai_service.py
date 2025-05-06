"""
AI API service utilities for handling interactions with Gemini AI.
"""
from typing import Dict, Any, Optional, List
import google.generativeai as genai

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
            # Log the error and re-raise or handle appropriately
            print(f"Error generating AI response: {str(e)}")
            raise
