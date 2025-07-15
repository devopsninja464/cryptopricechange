import os
import requests
import json

def get_prices():
    try:
        urls = [
           "https://api.dexscreener.com/latest/dex/pairs/ethereum/0xe472a9450974d9bae8be0eaebe556dfc892297cd"
        ]

        all_data = []

        for url in urls:
            response = requests.get(url)
            response.raise_for_status()
            response_data = response.json()
            # print("Full datA from DEXScreener API RESPONSE_DATA", response_data)

            data = []
            for pair in response_data.get("pairs", []):
                # print("Printing the pair required information", pair)
                chain = pair.get("chainId")

                coin_data = {}
                base_token = pair.get("baseToken", {})
                coin_data["name"] = base_token.get("name")
                coin_data["address"] = base_token.get("address")
                coin_data["symbol"] = base_token.get("symbol")

                price = pair.get("priceUsd")
                coin_data["priceUsd"] = price if price is not None else None

                fdv = pair.get("fdv")
                if coin_data["name"] == 'Amino':
                    if price is not None:
                        fdv = float(price) * 50000000000
                    else:
                        fdv = None
                coin_data["fdv"] = fdv

                h24 = pair.get("priceChange", {}).get("h24")
                coin_data["priceChange"] = h24 if h24 is not None else None

                data.append(coin_data)

            all_data.append({chain: data})

        return all_data

    except requests.exceptions.RequestException as req_ex:
        print(f"Error in making the HTTP request: {req_ex}")
    except json.JSONDecodeError as json_ex:
        print(f"Error decoding JSON response: {json_ex}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")

if __name__ == "__main__":
    get_prices()
