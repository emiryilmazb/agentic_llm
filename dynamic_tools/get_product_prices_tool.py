from mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List

class GetProductPricesTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="get_product_prices",
            description="Retrieves the prices of specified products from various online retailers or databases."
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        product_name = args.get("product_name")
        country = args.get("country")
        currency = args.get("currency")

        if not product_name:
            return {"error": "Product name is required."}
        if not country:
            return {"error": "Country is required."}

        try:
            results = self.get_product_prices(product_name, country, currency)
            return {"results": results}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def get_product_prices(self, product_name: str, country: str, currency: Optional[str] = None) -> List[Dict[str, Any]]:
        # This is a simplified example using a dummy API.  A real implementation would
        # integrate with actual e-commerce APIs or web scraping.
        # Due to the lack of a reliable free product API, this will use a mock API.

        if country.lower() == "usa" or country.lower() == "united states":
            country_code = "US"
            default_currency = "USD"
        elif country.lower() == "turkey":
            country_code = "TR"
            default_currency = "TRY"
        else:
            return [{"error": "Country not supported.  Only USA and Turkey are supported."}]

        if not currency:
            currency = default_currency

        # Mock API call
        try:
            response = requests.get(f"https://dummyjson.com/products/search?q={product_name}", timeout=5)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching product data: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding JSON response: {e}")

        results = []
        if data and "products" in data:
            for product in data["products"]:
                # Currency conversion if needed
                price = product["price"]
                if currency != default_currency:
                    try:
                        exchange_rate = self.get_exchange_rate(default_currency, currency)
                        price = round(price * exchange_rate, 2)
                    except Exception as e:
                        print(f"Currency conversion error: {e}")
                        # If currency conversion fails, return the price in the default currency
                        results.append({
                            "product_name": product["title"],
                            "price": product["price"],
                            "currency": default_currency,
                            "retailer": "Dummy Retailer"
                        })
                        continue

                results.append({
                    "product_name": product["title"],
                    "price": price,
                    "currency": currency,
                    "retailer": "Dummy Retailer"
                })
        else:
            return [{"message": "No products found."}]

        return results

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        try:
            response = requests.get(f"https://open.er-api.com/v6/latest/{from_currency}", timeout=5)
            response.raise_for_status()
            data = response.json()
            if "rates" in data and to_currency in data["rates"]:
                return data["rates"][to_currency]
            else:
                raise Exception(f"Could not find exchange rate for {to_currency}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching exchange rate: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding JSON response: {e}")