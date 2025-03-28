import requests
import csv
import datetime
import os

# API Credentials from GitHub Secrets
KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

# Instrument Tokens (Replace with actual values)
INSTRUMENT_TOKENS = {
    "NSE:ANGELONE": "123456",
    "NSE:IREDA": "789101",
    "NSE:CAMS": "112131",
    "NSE:TATAELXSI": "415161"
}

# Get today's date
today = datetime.datetime.now().strftime("%Y-%m-%d")
csv_file = "minute_data_today.csv"

# Write CSV Header
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Symbol", "Close Price"])

# Fetch Data for Each Instrument
for symbol, token in INSTRUMENT_TOKENS.items():
    api_url = f"https://api.kite.trade/instruments/historical/{token}/minute?from={today}+09:15:00&to={today}+15:30:00&interval=minute"

    headers = {
        "X-Kite-Version": "3",
        "Authorization": f"token {KITE_API_KEY}:{KITE_ACCESS_TOKEN}"
    }

    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        with open(csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            for candle in data["data"]["candles"]:
                timestamp, _, _, _, close_price, _ = candle
                writer.writerow([timestamp, symbol, close_price])
        print(f"Data saved for {symbol}")
    else:
        print(f"Error fetching data for {symbol}: {response.text}")

print(f"CSV file saved: {csv_file}")
