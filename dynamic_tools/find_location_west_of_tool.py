from mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List

class FindLocationWestOfTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="find_location_west_of",
            description="Finds locations that are west of a given location."
        )

    def _get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """
        Geocodes a location string to latitude and longitude using the Nominatim API.
        """
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={location}&format=jsonv2"
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if data:
                return {"latitude": float(data[0]["lat"]), "longitude": float(data[0]["lon"])}
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error during geocoding: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            print(f"Error parsing geocoding response: {e}")
            return None

    def _find_locations_west(self, reference_longitude: float, number_of_results: int = 5) -> List[Dict[str, Any]]:
        """
        Finds locations west of the reference longitude using a simplified approach.
        This implementation uses a hardcoded list of locations and filters them.
        A real-world implementation would query a geographical database.
        """
        locations = [
            {"name": "San Francisco", "latitude": 37.7749, "longitude": -122.4194},
            {"name": "Los Angeles", "latitude": 34.0522, "longitude": -118.2437},
            {"name": "Tokyo", "latitude": 35.6895, "longitude": 139.6917},
            {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
            {"name": "London", "latitude": 51.5074, "longitude": 0.1278},
            {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
            {"name": "Honolulu", "latitude": 21.3069, "longitude": -157.8583},
            {"name": "Sydney", "latitude": -33.8688, "longitude": 151.2093},
            {"name": "Anchorage", "latitude": 61.2181, "longitude": -149.9003},
            {"name": "Seattle", "latitude": 47.6062, "longitude": -122.3321},
        ]

        west_locations = [
            loc for loc in locations if loc["longitude"] < reference_longitude
        ]

        return west_locations[:number_of_results]

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        location = args.get("location")
        number_of_results = args.get("number_of_results", 5)

        if not isinstance(location, str) or not location:
            return {"error": "Location must be a non-empty string."}

        if not isinstance(number_of_results, int) or number_of_results <= 0:
            return {"error": "Number of results must be a positive integer."}

        coordinates = self._get_coordinates(location)

        if coordinates is None:
            return {"error": f"Could not find coordinates for location: {location}"}

        reference_longitude = coordinates["longitude"]
        west_locations = self._find_locations_west(reference_longitude, number_of_results)

        return {"locations": west_locations}