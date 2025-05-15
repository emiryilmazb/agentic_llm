from src.tools.base import DynamicTool
import requests
from typing import Dict, Any, Optional, List
import datetime

class CurrencyConverterTool(DynamicTool):
    def __init__(self):
        super().__init__(
            name="currency_converter",
            description="Converts between different currencies using current exchange rates.",
            created_at=datetime.datetime.now().isoformat(),
            parameters=[
                {
                    "name": "from_currency",
                    "type": "string",
                    "description": "Source currency code (e.g., USD, EUR)",
                    "required": True
                },
                {
                    "name": "to_currency",
                    "type": "string",
                    "description": "Target currency code (e.g., TRY, EUR)",
                    "required": True
                },
                {
                    "name": "amount",
                    "type": "number",
                    "description": "Amount to convert",
                    "required": True
                }
            ]
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        from_currency = args.get("from_currency")
        to_currency = args.get("to_currency")
        amount = args.get("amount")

        if not isinstance(from_currency, str):
            return {"error": "from_currency must be a string"}
        if not isinstance(to_currency, str):
            return {"error": "to_currency must be a string"}
        if not isinstance(amount, (int, float)):
            return {"error": "amount must be a number"}

        try:
            base_url = f"https://open.er-api.com/v6/latest/{from_currency}"
            response = requests.get(base_url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if "rates" not in data:
                return {"error": f"Could not retrieve exchange rates for {from_currency}"}

            rates = data["rates"]

            if to_currency not in rates:
                return {"error": f"Could not find exchange rate for {to_currency} in {from_currency}"}

            exchange_rate = rates[to_currency]
            converted_amount = amount * exchange_rate

            return {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "amount": amount,
                "converted_amount": converted_amount,
                "exchange_rate": exchange_rate
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"Error during API request: {e}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}