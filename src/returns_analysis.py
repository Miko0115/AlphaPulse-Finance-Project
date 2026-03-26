"""
AlphaPulse — Returns Analysis
Computes log returns, covariance/correlation matrices, Cholesky decomposition,
rolling volatility, and Sharpe ratios for the portfolio.
"""

import numpy as np
import pandas as pd

# Load cleaned price data
df = pd.read_csv("data/stock_data.csv", header=[0, 1], index_col=0, parse_dates=True)
tickers = ["AAPL", "UNH", "JPM", "XOM", "AMZN"]

# Extract close prices and flatten MultiIndex columns
close_prices = df.loc[:, (tickers, "Close")]
close_prices.columns = tickers

# log return = ln(P_today / P_yesterday) — additive across time, closer to normal distribution
log_returns = np.log(close_prices / close_prices.shift(1)).dropna()

print(f"Log returns shape: {log_returns.shape}")
print(f"\nMean daily returns (annualized):")       # daily mean × 252 trading days
print((log_returns.mean() * 252).round(4))
print(f"\nDaily return std dev (annualized):")      # daily std × √252 for annual volatility
print((log_returns.std() * np.sqrt(252)).round(4))

# Covariance and correlation matrices 
daily_cov_matrix = log_returns.cov()                   # pairwise daily covariance
annual_cov_matrix = daily_cov_matrix * 252             # annualize variance
correlation_matrix = log_returns.corr()               

print("\nDaily Covariance Matrix:")
print(daily_cov_matrix.round(6))
print(f"\nAnnual Covariance Matrix:")
print(annual_cov_matrix.round(4))
print(f"\nCorrelation Matrix:")
print(correlation_matrix.round(4))

# Cholesky Decompose Σ = L × Lᵀ 
L = np.linalg.cholesky(annual_cov_matrix)

print(f"\nCholesky Matrix (L):")
print(pd.DataFrame(L, columns=tickers, index=tickers).round(4))

# Verify reconstruction: L × Lᵀ should equal the original covariance matrix
reconstructed = L @ L.T
max_error = np.max(np.abs(reconstructed - annual_cov_matrix.values))
print(f"\nVerification — reconstruction error: {max_error:.2e}")

# 30-day rolling volatility (annualized)
rolling_vol = log_returns.rolling(window=30).std()     # 30-day rolling std of daily returns
rolling_vol_annualized = rolling_vol * np.sqrt(252)    # annualize
rolling_vol_annualized = rolling_vol_annualized.dropna()

# Compare crisis vs calm periods
covid_period_vol = rolling_vol_annualized.loc['2020-03':'2020-04']
calm_period_vol = rolling_vol_annualized.loc['2019-06':'2019-08']

print(f"\nRolling volatility shape: {rolling_vol_annualized.shape}")
print(f"Latest 30-day annualized volatility:")
print(rolling_vol_annualized.iloc[-1].round(4))
print(f"\nCOVID peak volatility (March 2020):")
print(covid_period_vol.max().round(4))
print(f"\nCalm period volatility (mid-2019):")
print(calm_period_vol.mean().round(4))

# Sharpe Ratio
risk_free_rate = 0.0425                                # ~10-year US Treasury yield
weights = np.array([1/len(tickers)] * len(tickers))   # equal weight: 20% each

# Portfolio return = weighted average of individual annualized returns
portfolio_annual_return = np.sum(log_returns.mean() * weights) * 252

# Portfolio volatility = sqrt(wᵀ × Σ × w) — accounts for correlations
portfolio_annual_vol = np.sqrt(weights @ annual_cov_matrix.values @ weights)

# Sharpe = (return - risk-free) / volatility
sharpe_ratio = (portfolio_annual_return - risk_free_rate) / portfolio_annual_vol

print(f"\nSharpe Ratio Analysis:")
print(f"Portfolio annual return:     {portfolio_annual_return*100:.2f}%")
print(f"Portfolio annual volatility: {portfolio_annual_vol*100:.2f}%")
print(f"Risk-free rate:              {risk_free_rate*100:.2f}%")
print(f"Sharpe Ratio:                {sharpe_ratio:.4f}")

# Individual stock Sharpe ratios for comparison
print(f"\nIndividual stock Sharpe Ratios:")
for ticker in tickers:
    stock_return = log_returns[ticker].mean() * 252
    stock_vol = log_returns[ticker].std() * np.sqrt(252)
    stock_sharpe = (stock_return - risk_free_rate) / stock_vol
    print(f"  {ticker}: {stock_sharpe:.4f} (return: {stock_return*100:.1f}%, vol: {stock_vol*100:.1f}%)")

# Export datasets
log_returns.to_csv("data/log_returns.csv")
correlation_matrix.to_csv("data/correlation_matrix.csv")
rolling_vol_annualized.to_csv("data/rolling_volatility_annualized.csv")

summary_stats = pd.DataFrame({
    'Annual Return': log_returns.mean() * 252,
    'Annual Volatility': log_returns.std() * np.sqrt(252),
    'Sharpe Ratio': (log_returns.mean() * 252 - risk_free_rate) / (log_returns.std() * np.sqrt(252))
}, index=tickers)
summary_stats.loc["Portfolio"] = [portfolio_annual_return, portfolio_annual_vol, sharpe_ratio]
summary_stats.to_csv("data/summary_stats.csv")

print("\nExported: log_returns, correlation_matrix, rolling_volatility, summary_stats")
