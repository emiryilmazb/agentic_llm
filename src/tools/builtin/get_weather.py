"""
Weather information tool implementation.

This module provides a tool for getting weather information for a location.
"""
import logging
import requests
from typing import Dict, Any, Optional, List

from src.tools.base import MCPTool

# Create a logger for this module
logger = logging.getLogger(__name__)

class GetWeather(MCPTool):
    """
    Tool to get weather information for a location.
    
    This tool allows characters to get current weather information
    for a specified location.
    """
    
    def __init__(self):
        """Initialize the weather tool."""
        super().__init__(
            name="get_weather",
            description="Gets weather information for a specified location"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the weather tool.
        
        Args:
            args: Dictionary containing the following keys:
                - location: The location to get weather for (required)
        
        Returns:
            Dictionary containing weather information
        """
        # Validate required arguments
        validation_error = self.validate_args(args, ["location"])
        if validation_error:
            return validation_error
        
        # Extract arguments
        location = args.get("location", "")
        
        logger.info(f"Getting weather for location: {location}")
        
        try:
            # Get coordinates for the location
            geocode_result = self._geocode_location(location)
            
            if "warning" in geocode_result:
                logger.warning(f"Geocoding warning: {geocode_result['warning']}")
            
            latitude = geocode_result["latitude"]
            longitude = geocode_result["longitude"]
            
            # Use Open-Meteo API
            logger.debug(f"Fetching weather data for coordinates: {latitude}, {longitude}")
            
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": ["temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m"],
                    "timezone": "auto"
                }
            )
            
            if response.status_code != 200:
                error_msg = f"API request failed with status code {response.status_code}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            data = response.json()
            
            # Convert weather codes to descriptions
            weather_descriptions = self._get_weather_descriptions()
            
            current = data.get("current", {})
            
            if not current:
                error_msg = "Failed to get current weather data from API response"
                logger.error(error_msg)
                return {"error": error_msg}
            
            temperature = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            weather_code = current.get("weather_code")
            wind_speed = current.get("wind_speed_10m")
            
            # Check for missing data
            if temperature is None or humidity is None or weather_code is None or wind_speed is None:
                missing_fields = []
                if temperature is None: missing_fields.append("temperature")
                if humidity is None: missing_fields.append("humidity")
                if weather_code is None: missing_fields.append("weather_code")
                if wind_speed is None: missing_fields.append("wind_speed")
                
                error_msg = f"Missing data fields in API response: {', '.join(missing_fields)}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            weather_condition = weather_descriptions.get(weather_code, "Unknown")
            
            logger.info(f"Successfully retrieved weather for {location}")
            
            return {
                "location": location,
                "temperature": temperature,
                "condition": weather_condition,
                "humidity": humidity,
                "wind": f"{wind_speed} km/h",
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "status": "success"
            }
        except requests.RequestException as e:
            error_msg = f"Error making API request: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error getting weather data: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.handle_error(e)
    
    def _geocode_location(self, location: str) -> Dict[str, Any]:
        """
        Convert a location name to coordinates.
        
        Args:
            location: The location name to geocode
            
        Returns:
            Dictionary with latitude and longitude
        """
        logger.debug(f"Geocoding location: {location}")
        
        # Dictionary of common locations and their coordinates
        geocode_map = {
            # Turkish cities
            "istanbul": {"latitude": 41.0082, "longitude": 28.9784},
            "ankara": {"latitude": 39.9334, "longitude": 32.8597},
            "izmir": {"latitude": 38.4237, "longitude": 27.1428},
            "antalya": {"latitude": 36.8969, "longitude": 30.7133},
            "bursa": {"latitude": 40.1885, "longitude": 29.0610},
            "adana": {"latitude": 37.0000, "longitude": 35.3213},
            
            # European cities
            "london": {"latitude": 51.5074, "longitude": -0.1278},
            "paris": {"latitude": 48.8566, "longitude": 2.3522},
            "berlin": {"latitude": 52.5200, "longitude": 13.4050},
            "rome": {"latitude": 41.9028, "longitude": 12.4964},
            "madrid": {"latitude": 40.4168, "longitude": -3.7038},
            "amsterdam": {"latitude": 52.3676, "longitude": 4.9041},
            
            # American cities
            "new york": {"latitude": 40.7128, "longitude": -74.0060},
            "los angeles": {"latitude": 34.0522, "longitude": -118.2437},
            "chicago": {"latitude": 41.8781, "longitude": -87.6298},
            "toronto": {"latitude": 43.6532, "longitude": -79.3832},
            
            # Asian cities
            "tokyo": {"latitude": 35.6762, "longitude": 139.6503},
            "beijing": {"latitude": 39.9042, "longitude": 116.4074},
            "shanghai": {"latitude": 31.2304, "longitude": 121.4737},
            "hong kong": {"latitude": 22.3193, "longitude": 114.1694},
            "singapore": {"latitude": 1.3521, "longitude": 103.8198},
            
            # Default fallback
            "default": {"latitude": 41.0082, "longitude": 28.9784}  # Istanbul
        }
        
        # Convert location to lowercase for case-insensitive matching
        location_lower = location.lower().strip()
        
        # Check for exact match
        if location_lower in geocode_map:
            logger.debug(f"Found exact match for location: {location}")
            return geocode_map[location_lower]
        
        # Check for partial match
        best_match = None
        best_match_score = 0
        
        for key, coords in geocode_map.items():
            # Check if location contains the key or key contains the location
            if key in location_lower:
                match_score = len(key) / len(location_lower)
                if match_score > best_match_score:
                    best_match = key
                    best_match_score = match_score
            elif location_lower in key:
                match_score = len(location_lower) / len(key)
                if match_score > best_match_score:
                    best_match = key
                    best_match_score = match_score
        
        # If we found a good match (score > 0.5)
        if best_match and best_match_score > 0.5:
            logger.debug(f"Found partial match for location '{location}': {best_match} (score: {best_match_score:.2f})")
            return geocode_map[best_match]
        
        # If no match found, use default (Istanbul)
        logger.warning(f"No match found for location '{location}'. Using default coordinates for Istanbul.")
        return {
            "latitude": 41.0082,
            "longitude": 28.9784,
            "warning": f"Could not geocode '{location}'. Using default coordinates for Istanbul."
        }
    
    def _get_weather_descriptions(self) -> Dict[int, str]:
        """
        Get a dictionary of weather code to description mappings.
        
        Returns:
            Dictionary mapping weather codes to descriptions
        """
        return {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }