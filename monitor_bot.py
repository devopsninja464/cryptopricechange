import json
import os
from telegram import Bot
import dexapicode

TG_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
bot = Bot(token=TG_TOKEN)

PRICE_FILE = 'last_prices.json'
THRESHOLD = 20  # percent

try:
    with open(PRICE_FILE, 'r') as f:
        last_prices = json.load(f)
except FileNotFoundError:
    last_prices = {}

try:
    crypto_data = dexapicode.get_prices()

    for chain_data in crypto_data:
        chain_id = list(chain_data.keys())[0]
        coins = chain_data[chain_id]

        for coin in coins:
            symbol = coin.get("symbol")
            price_str = coin.get("priceUsd")
            if symbol is None or price_str is None:
                continue

            current_price = float(price_str)

            if symbol in last_prices:
                old_price = float(last_prices[symbol])
                change = ((current_price - old_price) / old_price) * 100

                if abs(change) >= THRESHOLD:
                    message = (
                        f"🚨 *{symbol}* price changed by {change:.2f}%\n"
                        f"💰 Current Price: ${current_price:,.6f}\n"
                        f"Chain ID: {chain_id}"
                    )
                    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

            last_prices[symbol] = current_price

    with open(PRICE_FILE, 'w') as f:
        json.dump(last_prices, f)

except Exception as e:
    print(f"Error during price monitoring: {e}")
