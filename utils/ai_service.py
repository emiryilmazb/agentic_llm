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
    
    # Thinking modeli için prompt şablonu
    THINKING_PROMPT_TEMPLATE = """
    Lütfen aşağıdaki soruyu yanıtlarken düşünce sürecini adım adım göster.
    
    Önce sorunu analiz et, ardından olası çözümleri düşün ve en iyi çözümü seç.
    Her adımı "Düşünce:" başlığı altında açıkla, sonra "Yanıt:" başlığı altında final yanıtını ver.
    
    Soru: {question}
    
    Düşünce:
    """

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
    
    @staticmethod
    def generate_thinking_response(question: str,
                                model_name: str = DEFAULT_MODEL,
                                temperature: float = 0.2,  # Düşük sıcaklık değeri daha tutarlı sonuçlar için
                                max_tokens: int = DEFAULT_MAX_TOKENS * 2,  # Düşünce süreci daha uzun olabilir
                                top_p: float = DEFAULT_TOP_P) -> Dict[str, str]:
        """
        Gemini modelini kullanarak düşünce sürecini gösteren bir yanıt üretir.
        
        Args:
            question: Yanıtlanacak soru
            model_name: Kullanılacak Gemini modeli
            temperature: Rastgeleliği kontrol eder (yüksek = daha rastgele)
            max_tokens: Üretilecek maksimum token sayısı
            top_p: Nucleus sampling parametresi
            
        Returns:
            Dict containing 'thinking' and 'answer' parts of the response
        """
        # Thinking prompt şablonunu kullanarak prompt oluştur
        prompt = AIService.THINKING_PROMPT_TEMPLATE.format(question=question)
        
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
                
                # Yanıt al
                response = model.generate_content(prompt)
                full_text = response.text
                
                # Yanıtı düşünce ve cevap kısımlarına ayır
                parts = {}
                
                # Düşünce kısmını çıkar
                thinking_part = full_text
                answer_part = ""
                
                # Eğer "Yanıt:" bölümü varsa, ayır
                if "Yanıt:" in full_text:
                    parts = full_text.split("Yanıt:", 1)
                    thinking_part = parts[0].strip()
                    if len(parts) > 1:
                        answer_part = parts[1].strip()
                
                return {
                    "thinking": thinking_part,
                    "answer": answer_part,
                    "full_response": full_text
                }
                
            except Exception as e:
                retries += 1
                print(f"Error generating thinking response (attempt {retries}/{AIService.MAX_RETRIES}): {str(e)}")
                if retries >= AIService.MAX_RETRIES:
                    print("Max retries reached. Raising exception.")
                    raise
                
                # Exponential backoff with jitter
                sleep_time = backoff_time + random.uniform(0, 1)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                backoff_time *= 2
        
        print("Error generating thinking response after multiple retries.")
        raise Exception("Failed to generate thinking response after multiple retries.")
