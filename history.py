import os
import pandas as pd
from datetime import datetime, timedelta
from kiteconnect import KiteConnect

api_key = os.environ["KITE_API_KEY"]
access_token = os.environ["KITE_ACCESS_TOKEN"]

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

to_date = datetime.today()
from_date = to_date - timedelta(days=180)

# ---- Instruments ----
instruments = kite.instruments()

spot = next(
    item for item in instruments
    if item["tradingsymbol"] == "KFINTECH" and item["exchange"] == "NSE"
)

# Get ALL futures (including future expiries)
all_futures = [
    item for item in instruments
    if item["name"] == "KFINTECH"
    and item["exchange"] == "NFO"
    and item["instrument_type"] == "FUT"
]

# ---- Fetch Spot Data ----
spot_data = kite.historical_data(
    spot["instrument_token"],
    from_date,
    to_date,
    interval="day"
)

spot_df = pd.DataFrame(spot_data)[["date", "close"]]
spot_df.rename(columns={"close": "spot"}, inplace=True)

# ---- Fetch Historical Data for Each Futures Contract ----
fut_data_dict = {}

for fut in all_futures:
    data = kite.historical_data(
        fut["instrument_token"],
        from_date,
        to_date,
        interval="day"
    )
    if data:
        df = pd.DataFrame(data)[["date", "close"]]
        df["expiry"] = fut["expiry"]
        df["symbol"] = fut["tradingsymbol"]
        fut_data_dict[fut["tradingsymbol"]] = df

# Combine all futures data
fut_df = pd.concat(fut_data_dict.values(), ignore_index=True)

# ---- Merge Spot + Futures ----
merged = pd.merge(spot_df, fut_df, on="date", how="left")

# ---- Dynamic Near / Next / Far Selection ----
final_rows = []

for date in merged["date"].unique():

    day_data = merged[merged["date"] == date]
    spot_price = day_data["spot"].iloc[0]

    valid = day_data[day_data["expiry"] >= date.date()].sort_values("expiry")

    if len(valid) < 3:
        continue

    near = valid.iloc[0]
    next_m = valid.iloc[1]
    far = valid.iloc[2]

    final_rows.append({
        "date": date,
        "spot": spot_price,
        "near_fut": near["close"],
        "next_fut": next_m["close"],
        "far_fut": far["close"],
        "spread_spot_near": spot_price - near["close"],
        "spread_spot_next": spot_price - next_m["close"],
        "spread_spot_far": spot_price - far["close"]
    })

final_df = pd.DataFrame(final_rows)
final_df.to_csv("kfintech_term_structure_full_6months.csv", index=False)

print("Full 6 months term structure saved!")
print(final_df.head())
print("Total rows:", len(final_df))
