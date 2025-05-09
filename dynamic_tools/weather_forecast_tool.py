from mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List

class WeatherForecastTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="weather_forecast",
            description="Gets weather forecast for a specified location"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        location = args.get("location", "")
        days = int(args.get("days", 3))
        
        if not location:
            return {"error": "location parameter is required"}
        
        # Basit bir geocoding işlemi
        # Gerçek uygulamada daha gelişmiş bir geocoding servisi kullanılabilir
        geocode_result = self._geocode_location(location)
        
        if "error" in geocode_result:
            return geocode_result
        
        latitude = geocode_result["latitude"]
        longitude = geocode_result["longitude"]
        
        # Open-Meteo API'sini kullan
        try:
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "weathercode"],
                    "timezone": "auto",
                    "forecast_days": days
                }
            )
            
            if response.status_code != 200:
                error_message = f"API request failed with status code {response.status_code}"
                print(error_message)
                return {"error": error_message}
            
            data = response.json()
            
            # Forecast verilerini işle
            forecast = []
            daily = data.get("daily", {})
            
            if not daily:
                error_message = "Failed to get forecast data from API response"
                print(error_message)
                return {"error": error_message}
            
            dates = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            precip = daily.get("precipitation_sum", [])
            weather_codes = daily.get("weathercode", [])
            
            # Veri eksikliği kontrolü
            if not dates or not max_temps or not min_temps or not precip or not weather_codes:
                missing_fields = []
                if not dates: missing_fields.append("dates")
                if not max_temps: missing_fields.append("max_temps")
                if not min_temps: missing_fields.append("min_temps")
                if not precip: missing_fields.append("precipitation")
                if not weather_codes: missing_fields.append("weather_codes")
                
                error_message = f"Missing data fields in API response: {', '.join(missing_fields)}"
                print(error_message)
                return {"error": error_message}
            
            # Hava durumu kodlarını açıklamalara dönüştür
            weather_descriptions = {
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
            
            for i in range(len(dates)):
                if i < len(max_temps) and i < len(min_temps) and i < len(precip) and i < len(weather_codes):
                    weather_desc = weather_descriptions.get(weather_codes[i], "Unknown")
                    forecast.append({
                        "date": dates[i],
                        "max_temp": max_temps[i],
                        "min_temp": min_temps[i],
                        "precipitation": precip[i],
                        "weather": weather_desc
                    })
            
            # Eğer forecast boşsa, hata döndür
            if not forecast:
                error_message = "Failed to process forecast data"
                print(error_message)
                return {"error": error_message}
            
            return {
                "location": location,
                "forecast": forecast,
                "units": {
                    "temperature": "°C",
                    "precipitation": "mm"
                }
            }
        except requests.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message)
            return {"error": error_message}
        except (ValueError, KeyError) as e:
            error_message = f"Error processing data: {str(e)}"
            print(error_message)
            return {"error": error_message}
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message)
            return {"error": error_message}
    
    def _geocode_location(self, location: str) -> Dict[str, Any]:
        """
        Basit bir geocoding işlemi
        Gerçek uygulamada daha gelişmiş bir geocoding servisi kullanılabilir
        """
        # Bazı yaygın şehirler ve ülkeler için sabit koordinatlar
        geocode_map = {
            # Türkiye şehirleri
            "istanbul": {"latitude": 41.0082, "longitude": 28.9784},
            "ankara": {"latitude": 39.9334, "longitude": 32.8597},
            "izmir": {"latitude": 38.4237, "longitude": 27.1428},
            "antalya": {"latitude": 36.8969, "longitude": 30.7133},
            "bursa": {"latitude": 40.1885, "longitude": 29.0610},
            "adana": {"latitude": 37.0000, "longitude": 35.3213},
            
            # Avrupa şehirleri
            "london": {"latitude": 51.5074, "longitude": -0.1278},
            "paris": {"latitude": 48.8566, "longitude": 2.3522},
            "berlin": {"latitude": 52.5200, "longitude": 13.4050},
            "rome": {"latitude": 41.9028, "longitude": 12.4964},
            "madrid": {"latitude": 40.4168, "longitude": -3.7038},
            "amsterdam": {"latitude": 52.3676, "longitude": 4.9041},
            "brussels": {"latitude": 50.8503, "longitude": 4.3517},
            "vienna": {"latitude": 48.2082, "longitude": 16.3738},
            "athens": {"latitude": 37.9838, "longitude": 23.7275},
            
            # Amerika şehirleri
            "new york": {"latitude": 40.7128, "longitude": -74.0060},
            "los angeles": {"latitude": 34.0522, "longitude": -118.2437},
            "chicago": {"latitude": 41.8781, "longitude": -87.6298},
            "toronto": {"latitude": 43.6532, "longitude": -79.3832},
            "mexico city": {"latitude": 19.4326, "longitude": -99.1332},
            "rio de janeiro": {"latitude": -22.9068, "longitude": -43.1729},
            "buenos aires": {"latitude": -34.6037, "longitude": -58.3816},
            
            # Asya şehirleri
            "tokyo": {"latitude": 35.6762, "longitude": 139.6503},
            "beijing": {"latitude": 39.9042, "longitude": 116.4074},
            "shanghai": {"latitude": 31.2304, "longitude": 121.4737},
            "hong kong": {"latitude": 22.3193, "longitude": 114.1694},
            "singapore": {"latitude": 1.3521, "longitude": 103.8198},
            "mumbai": {"latitude": 19.0760, "longitude": 72.8777},
            "delhi": {"latitude": 28.6139, "longitude": 77.2090},
            "seoul": {"latitude": 37.5665, "longitude": 126.9780},
            
            # Orta Doğu şehirleri
            "dubai": {"latitude": 25.2048, "longitude": 55.2708},
            "riyadh": {"latitude": 24.7136, "longitude": 46.6753},
            "jeddah": {"latitude": 21.5433, "longitude": 39.1728},
            "mecca": {"latitude": 21.3891, "longitude": 39.8579},
            "tehran": {"latitude": 35.6892, "longitude": 51.3890},
            "cairo": {"latitude": 30.0444, "longitude": 31.2357},
            
            # Afrika şehirleri
            "lagos": {"latitude": 6.5244, "longitude": 3.3792},
            "nairobi": {"latitude": 1.2921, "longitude": 36.8219},
            "cape town": {"latitude": -33.9249, "longitude": 18.4241},
            "johannesburg": {"latitude": -26.2041, "longitude": 28.0473},
            
            # Okyanusya şehirleri
            "sydney": {"latitude": -33.8688, "longitude": 151.2093},
            "melbourne": {"latitude": -37.8136, "longitude": 144.9631},
            "auckland": {"latitude": -36.8509, "longitude": 174.7645},
            
            # Ülkeler (ülke merkezleri)
            "turkey": {"latitude": 38.9637, "longitude": 35.2433},
            "usa": {"latitude": 37.0902, "longitude": -95.7129},
            "uk": {"latitude": 55.3781, "longitude": -3.4360},
            "france": {"latitude": 46.2276, "longitude": 2.2137},
            "germany": {"latitude": 51.1657, "longitude": 10.4515},
            "italy": {"latitude": 41.8719, "longitude": 12.5674},
            "spain": {"latitude": 40.4637, "longitude": -3.7492},
            "russia": {"latitude": 61.5240, "longitude": 105.3188},
            "china": {"latitude": 35.8617, "longitude": 104.1954},
            "japan": {"latitude": 36.2048, "longitude": 138.2529},
            "india": {"latitude": 20.5937, "longitude": 78.9629},
            "brazil": {"latitude": -14.2350, "longitude": -51.9253},
            "australia": {"latitude": -25.2744, "longitude": 133.7751},
            "canada": {"latitude": 56.1304, "longitude": -106.3468},
            "saudi arabia": {"latitude": 23.8859, "longitude": 45.0792},
            "arabia": {"latitude": 23.8859, "longitude": 45.0792},  # Arabistan için özel giriş
            "egypt": {"latitude": 26.8206, "longitude": 30.8025},
            "south africa": {"latitude": -30.5595, "longitude": 22.9375}
        }
        
        # Lokasyonu küçük harfe çevir ve haritada ara
        location_lower = location.lower().strip()
        
        # Tam eşleşme kontrolü
        if location_lower in geocode_map:
            print(f"Exact match found for '{location}': {geocode_map[location_lower]}")
            return geocode_map[location_lower]
        
        # Kısmi eşleşme kontrolü - daha akıllı algoritma
        best_match = None
        best_match_score = 0
        
        for key, coords in geocode_map.items():
            # Tam içerme kontrolü
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
        
        # Eğer iyi bir eşleşme bulunduysa (skor > 0.5)
        if best_match and best_match_score > 0.5:
            print(f"Partial match found for '{location}': {best_match} (score: {best_match_score})")
            return geocode_map[best_match]
        
        # Geocoding API kullanma (bu örnekte taklit ediyoruz)
        try:
            # Gerçek bir uygulamada burada bir geocoding API'si kullanılabilir
            # Örneğin: Nominatim, Google Maps Geocoding API, vb.
            
            # Bazı özel durumlar için manuel eşleştirme
            if "arab" in location_lower:
                print(f"Special case for '{location}': Using Saudi Arabia coordinates")
                return geocode_map["saudi arabia"]
            
            if "amster" in location_lower:
                print(f"Special case for '{location}': Using Amsterdam coordinates")
                return geocode_map["amsterdam"]
            
            # Eşleşme bulunamazsa, varsayılan olarak İstanbul koordinatlarını döndür
            # ve bir uyarı ekle
            print(f"No match found for '{location}'. Using default coordinates for Istanbul.")
            return {
                "latitude": 41.0082,
                "longitude": 28.9784,
                "warning": f"Could not geocode '{location}'. Using default coordinates for Istanbul."
            }
        except Exception as e:
            print(f"Error in geocoding: {str(e)}")
            return {
                "latitude": 41.0082,
                "longitude": 28.9784,
                "warning": f"Error geocoding '{location}': {str(e)}. Using default coordinates for Istanbul."
            }