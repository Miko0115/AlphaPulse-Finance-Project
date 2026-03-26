"""
AlphaPulse — Data Fetcher
Fetches 10 years of OHLCV data for 5 diversified stocks,
validates for anomalies, and exports a cleaned CSV.
"""

import pandas as pd
import yfinance as yf

tickers = ["AAPL", "UNH", "JPM", "XOM", "AMZN"]
start_date = "2015-01-01"                              
end_date = "2025-01-01"                               
output_path = "data/stock_data.csv"

# Step 1: Fetch OHLCV data from Yahoo Finance
raw_data = yf.download(
    tickers,
    start=start_date,
    end=end_date,
    group_by='ticker',
    auto_adjust=True                                   # adjust for stock splits and dividends
)

print(f"Fetched: {raw_data.shape[0]} rows x {raw_data.shape[1]} columns")
print(raw_data.head())

# Step 2: Check for missing values
print("\nMissing values in raw_data:")
print(raw_data.isnull().sum())

# Step 3: Validate for stock splits and anomalies
# Flag any daily return exceeding ±50% as a potential data quality issue
for ticker in tickers:
    close_prices = raw_data[ticker]["Close"]
    daily_returns = close_prices.pct_change()
    anomalies = daily_returns[daily_returns.abs() > 0.5]

    if len(anomalies) > 0:
        print(f"{ticker} — {len(anomalies)} anomalies detected:")
        print(anomalies)
    else:
        print(f"{ticker} — No anomalies detected.")

    print(f"  Price range: ${close_prices.min():.2f} – ${close_prices.max():.2f}")
    print(f"  Trading days: {len(close_prices)}")
    print()

# Step 4: Export cleaned data
raw_data.to_csv(output_path, index=True)
print(f"Exported: {output_path} ({raw_data.shape[0]} rows, {raw_data.shape[1]} columns)")
