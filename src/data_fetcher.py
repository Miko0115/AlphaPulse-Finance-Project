import pandas as pd
import yfinance as yf
from datetime import datetime

output_path = "data/stock_data.csv"

tickers = ["AAPL", "JNJ", "JPM", "XOM", "AMZN"]
start_date = "2016-03-16"
end_date = datetime.today().strftime('%Y-%m-%d')

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

cleaned_raw_data = raw_data.ffill()
cleaned_raw_data = cleaned_raw_data.bfill()

print("Missing values in cleaned_raw_data:")
print(raw_data.isnull().sum())


for ticker in tickers:
    close_prices = cleaned_raw_data[ticker]["Close"]
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

cleaned_raw_data.to_csv(output_path, index=True)

print(f"Cleaned data saved to {output_path}")
print(f"Rows: {cleaned_raw_data.shape[0]}, Columns: {cleaned_raw_data.shape[1]}")


