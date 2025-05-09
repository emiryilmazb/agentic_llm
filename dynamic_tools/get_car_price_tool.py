from mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List
import re
from datetime import datetime

class GetCarPriceTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="get_car_price",
            description="Retrieves the price of a specified car model in a specified country."
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        car_model = args.get("car_model")
        country_code = args.get("country_code")

        if not car_model or not country_code:
            return {"error": "Both car_model and country_code are required."}

        try:
            if country_code.upper() == "TR":
                return self._get_car_price_tr(car_model)
            elif country_code.upper() == "US":
                return self._get_car_price_us(car_model)
            else:
                return {"error": f"Country code {country_code} is not supported."}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def _get_car_price_tr(self, car_model: str) -> Dict[str, Any]:
        try:
            url = f"https://www.sahibinden.com/otomobil?query={car_model}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            text = response.text
            prices = re.findall(r'<span class="classifiedDetail">(.*?) TL</span>', text)

            if not prices:
                return {"error": f"No prices found for {car_model} in Turkey."}

            prices_numeric = []
            for price_str in prices:
                price_str = price_str.replace('.', '').strip()
                try:
                    price = int(price_str)
                    prices_numeric.append(price)
                except ValueError:
                    pass

            if not prices_numeric:
                return {"error": f"No valid prices found for {car_model} in Turkey."}

            avg_price = sum(prices_numeric) / len(prices_numeric)
            return {"price": f"{avg_price:.2f} TRY", "currency": "TRY", "car_model": car_model, "country": "Turkey"}

        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching data from sahibinden.com: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred while processing data: {str(e)}"}

    def _get_car_price_us(self, car_model: str) -> Dict[str, Any]:
        try:
            url = f"https://www.cars.com/shopping/results/?stock_type=used&makes[]={car_model}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            text = response.text
            prices = re.findall(r'\$(\d{1,3}(,\d{3})*(\.\d+)?)', text)

            if not prices:
                return {"error": f"No prices found for {car_model} in the US."}

            prices_numeric = []
            for price_str, _, _ in prices:
                price_str = price_str.replace(',', '')
                try:
                    price = float(price_str)
                    prices_numeric.append(price)
                except ValueError:
                    pass

            if not prices_numeric:
                return {"error": f"No valid prices found for {car_model} in the US."}

            avg_price = sum(prices_numeric) / len(prices_numeric)
            return {"price": f"{avg_price:.2f} USD", "currency": "USD", "car_model": car_model, "country": "USA"}

        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching data from cars.com: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred while processing data: {str(e)}"}