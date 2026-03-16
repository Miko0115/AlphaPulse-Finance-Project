import pandas as pd
import yfinance as yf
from datetime import datetime

tickers = ['AAPL', 'JNJ', 'JPM', 'XOM', 'AMZN']
start_date = "2021-03-16"
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