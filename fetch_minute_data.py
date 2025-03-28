import requests
import csv
import datetime
import os

# API Credentials from GitHub Secrets
KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

# Instrument Tokens for Stocks & Futures (Replace with actual values)
INSTRUMENT_TOKENS = {
    "NSE:ANGELONE": "82945",
    "NFO:ANGELONE25APRFUT": "16781314",
    "NSE:IREDA": "5186817",
    "NFO:IREDA25APRFUT": "14679554",
    "NSE:CAMS": "87553",
    "NFO:CAMS25APRFUT": "18756098",
    "NSE:TATAELXSI": "873217",
    "NFO:TATAELXSI25APRFUT": "18836482"
}

# Get today's date
today = datetime.datetime.now().strftime("%Y-%m-%d")
csv_file = "minute_data_today.csv"

# Write CSV Header
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Stock Symbol", "Stock Close Price", "Future Symbol", "Future Close Price", "Difference"])

# Fetch Data for Each Stock & Future Pair
STOCK_FUTURE_PAIRS = [
    ("NSE:ANGELONE", "NFO:ANGELONE25APRFUT"),
    ("NSE:IREDA", "NFO:IREDA25APRFUT"),
    ("NSE:CAMS", "NFO:CAMS25APRFUT"),
    ("NSE:TATAELXSI", "NFO:TATAELXSI25APRFUT")
]

for stock_symbol, future_symbol in STOCK_FUTURE_PAIRS:
    stock_token = INSTRUMENT_TOKENS[stock_symbol]
    future_token = INSTRUMENT_TOKENS[future_symbol]

    stock_api_url = f"https://api.kite.trade/instruments/historical/{stock_token}/minute?from={today}+09:15:00&to={today}+15:30:00&interval=minute"
    future_api_url = f"https://api.kite.trade/instruments/historical/{future_token}/minute?from={today}+09:15:00&to={today}+15:30:00&interval=minute"

    headers = {
        "X-Kite-Version": "3",
        "Authorization": f"token {KITE_API_KEY}:{KITE_ACCESS_TOKEN}"
    }

    stock_response = requests.get(stock_api_url, headers=headers)
    future_response = requests.get(future_api_url, headers=headers)

    if stock_response.status_code == 200 and future_response.status_code == 200:
        stock_data = stock_response.json()
        future_data = future_response.json()

        # Open CSV file in append mode
        with open(csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)

            # Loop through the minute-by-minute data
            for stock_candle, future_candle in zip(stock_data["data"]["candles"], future_data["data"]["candles"]):
                stock_timestamp, _, _, _, stock_close, _ = stock_candle
                future_timestamp, _, _, _, future_close, _ = future_candle

                # Ensure timestamps match
                if stock_timestamp == future_timestamp:
                    difference = round(float(stock_close) - float(future_close), 2)
                    writer.writerow([stock_timestamp, stock_symbol, stock_close, future_symbol, future_close, difference])

        print(f"Data saved for {stock_symbol} and {future_symbol}")
    else:
        print(f"Error fetching data for {stock_symbol}: {stock_response.text}")
        print(f"Error fetching data for {future_symbol}: {future_response.text}")

print(f"CSV file saved: {csv_file}")
