import pandas as pd
import yfinance as yf
from datetime import datetime

output_path = "data/stock_data.csv"

tickers = ["AAPL", "UNH", "JPM", "XOM", "AMZN"]
start_date = "2015-01-01"
end_date = "2025-01-01"

raw_data = yf.download(
    tickers,
    start=start_date,
    end=end_date,
    group_by='ticker',
    auto_adjust=True
)

print(raw_data.shape)
print(raw_data.head())

print("Missing values in raw_data:")
print(raw_data.isnull().sum())

for ticker in tickers:
    close_prices = raw_data[ticker]["Close"]
    daily_returns = close_prices.pct_change()
    
    anomalies = daily_returns[daily_returns.abs() > 0.5]
    
    if len(anomalies) > 0:
        print(f"{ticker} - {len(anomalies)} anomalies detected in daily returns.")
        print(anomalies)
    else:
        print(f"{ticker} - No anomalies detected in daily returns.")
        
    print(f"Price Range: ${close_prices.min():.2f} - ${close_prices.max():.2f}")
    print(f"Total Trading Days: {len(close_prices)}")
    print()

raw_data.to_csv(output_path, index=True)

print(f"Cleaned data saved to {output_path}")
print(f"Rows: {raw_data.shape[0]}, Columns: {raw_data.shape[1]}")


