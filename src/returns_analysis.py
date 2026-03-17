import numpy as np
import pandas as pd

df = pd.read_csv("data/stock_data.csv",header=[0, 1], index_col=0, parse_dates=True)
print(df.head())

tickers = ["AAPL", "JNJ", "JPM", "XOM", "AMZN"]

close_prices = df.loc[:, (tickers, "Close")]
close_prices.columns = tickers
print(close_prices.head())

log_returns = np.log(close_prices/close_prices.shift(1))

log_returns = log_returns.dropna()

print(f"Log returns shape: {log_returns.shape}")
print(f"\nMean daily returns (annualized)") #this return %
print((log_returns.mean() * 252).round(4))
print(f"\nDaily return std dev (annualized)") #this is volatility
print((log_returns.std() * np.sqrt(252)).round(4))
print(f"\nFirst 5 Rows")
print(log_returns.head())

daily_cov_matrix = log_returns.cov()

annual_cov_matrix = daily_cov_matrix * 252

correlation_matrix = log_returns.corr()

print("Daily Covariance Matrix")
print(daily_cov_matrix.round(6))
print(f"\nAnnual Covariance Matrix")
print(annual_cov_matrix.round(4))
print(f"\nCorrelation Matrix")
print(correlation_matrix.round(4))

L = np.linalg.cholesky(annual_cov_matrix)

print(f"\nCholesky Matrix")
print(pd.DataFrame(L, columns=tickers, index=tickers).round(4))

reconstructed = L @ L.T
print(f"\nVerification of Annual covariance matrix")
print(f"Max difference: {np.max(np.abs(reconstructed - annual_cov_matrix.values)):.2e}")