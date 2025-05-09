from mcp_server import MCPTool
import requests
import json
import re
from typing import Dict, Any, Optional, List

class GetProductPriceTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="get_product_price",
            description="Retrieves the price of a specified product from a specified retailer or online marketplace."
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        product_name = args.get("product_name")
        retailer = args.get("retailer")
        country = args.get("country")

        if not product_name or not retailer:
            return {"error": "Product name and retailer are required."}

        if not country:
            try:
                response = requests.get("http://ip-api.com/json/")
                response.raise_for_status()
                country = response.json().get("countryCode", "US")
            except requests.exceptions.RequestException as e:
                print(f"Geolocation failed: {e}")
                country = "US"

        try:
            if retailer.lower() == "amazon":
                if country.lower() == "tr":
                    url = f"https://www.amazon.com.tr/s?k={product_name}"
                elif country.lower() == "uk":
                    url = f"https://www.amazon.co.uk/s?k={product_name}"
                elif country.lower() == "de":
                    url = f"https://www.amazon.de/s?k={product_name}"
                else:
                    url = f"https://www.amazon.com/s?k={product_name}"

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()

                # Basic scraping - this is fragile and will likely break.  A real implementation would use a proper scraping library and handle variations in Amazon's HTML.
                text = response.text
                price_match = re.search(r'\$\d+\.\d{2}', text) # US Dollar price
                if country.lower() == "tr":
                    price_match = re.search(r'\d+\,\d{2}\sTL', text) # Turkish Lira price
                elif country.lower() == "uk":
                    price_match = re.search(r'£\d+\.\d{2}', text) # British Pound price
                elif country.lower() == "de":
                    price_match = re.search(r'\d+\,\d{2}\s€', text) # Euro price

                if price_match:
                    price_str = price_match.group(0)
                    price = float(re.sub(r'[^\d\.]', '', price_str).replace(",", "."))

                    currency = "USD"
                    if country.lower() == "tr":
                        currency = "TRY"
                    elif country.lower() == "uk":
                        currency = "GBP"
                    elif country.lower() == "de":
                        currency = "EUR"

                    if currency != "USD":
                        try:
                            conversion_url = f"https://open.er-api.com/v6/latest/{currency}"
                            conversion_response = requests.get(conversion_url)
                            conversion_response.raise_for_status()
                            conversion_data = conversion_response.json()
                            usd_rate = conversion_data["rates"]["USD"]
                            price_usd = price * usd_rate
                            return {"product": product_name, "retailer": retailer, "price": price_usd, "currency": "USD"}
                        except requests.exceptions.RequestException as e:
                            print(f"Currency conversion failed: {e}")
                            return {"product": product_name, "retailer": retailer, "price": price, "currency": currency, "message": "Could not convert to USD."}

                    return {"product": product_name, "retailer": retailer, "price": price, "currency": currency}
                else:
                    return {"error": f"Could not find price for {product_name} on Amazon {country}."}
            else:
                return {"error": f"Retailer {retailer} not supported."}

        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {e}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}