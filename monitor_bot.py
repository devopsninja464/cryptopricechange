import os
import json
from telegram import Bot
import dexapicode

# Load environment variables
TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]

# Initialize the Telegram bot
bot = Bot(token=TG_BOT_TOKEN)

# Load previous alerted prices
last_prices_file = "last_prices.json"

if os.path.exists(last_prices_file):
    with open(last_prices_file, "r") as f:
        last_prices = json.load(f)
else:
    last_prices = {}

# Get current token prices from DEX API
crypto_data = dexapicode.get_prices()

# Track if we updated any prices
updated = False

for chain_data in crypto_data:
    for chain_name, tokens in chain_data.items():
        for coin in tokens:
            symbol = coin.get("symbol")
            current_price = float(coin.get("priceUsd", 0))

            if current_price == 0 or not symbol:
                continue  # skip invalid entries

            old_price = last_prices.get(symbol)

            # If it's the first time, store the price but don't alert
            if old_price is None:
                last_prices[symbol] = current_price
                print(f"Initialized price for {symbol}: {current_price}")
                continue

            # Calculate % change
            change_pct = ((current_price - old_price) / old_price) * 100

            if abs(change_pct) >= 20:
                # Send alert to Telegram
                msg = (
                    f"🚨 Price Alert for *{symbol}*\n"
                    f"Change: `{change_pct:.2f}%`\n"
                    f"Old: `${old_price:.6f}`\n"
                    f"New: `${current_price:.6f}`"
                )
                bot.send_message(chat_id=TG_CHAT_ID, text=msg, parse_mode="Markdown")
                print(f"Sent alert for {symbol} | Change: {change_pct:.2f}%")

                # Update price only after alerting
                last_prices[symbol] = current_price
                updated = True
            else:
                print(f"No significant change for {symbol} | Change: {change_pct:.2f}% | Old: {old_price:.6f} | New: {current_price:.6f}")

# Write updated prices back to JSON if needed
if updated:
    with open(last_prices_file, "w") as f:
        json.dump(last_prices, f, indent=2)
    print("Updated last_prices.json")
else:
    print("No alerts sent. No updates to last_prices.json")
