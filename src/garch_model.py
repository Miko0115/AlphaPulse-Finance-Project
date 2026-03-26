"""
AlphaPulse — GARCH(1,1) Volatility Forecasting
Fits a GARCH(1,1) model to each asset's log returns to capture
time-varying volatility and forecast next-day conditional variance.
"""

import numpy as np
import pandas as pd
from arch import arch_model

# Load data and compute log returns
df = pd.read_csv("data/stock_data.csv", header=[0, 1], index_col=0, parse_dates=True)
tickers = ["AAPL", "UNH", "JPM", "XOM", "AMZN"]

close_prices = df.loc[:, (tickers, "Close")]
close_prices.columns = tickers
log_returns = np.log(close_prices / close_prices.shift(1)).dropna()

# Fit GARCH(1,1) to each ticker
garch_results = {}                                     # fitted model objects
garch_forecasts = {}                                   # next-day volatility forecasts
garch_conditional_vol = {}                             # historical conditional volatility series

for ticker in tickers:
    # Scale returns to percentage — GARCH optimizer works better with larger values
    returns = log_returns[ticker] * 100

    # GARCH(1,1): σ²(t) = ω + α × r²(t-1) + β × σ²(t-1)
    model = arch_model(returns, vol="GARCH", p=1, q=1, dist="normal")
    fitted = model.fit(disp="off")                     # suppress optimizer output

    garch_results[ticker] = fitted
    garch_conditional_vol[ticker] = fitted.conditional_volatility / 100  # scale back to decimal

    # Forecast next-day volatility
    forecast = fitted.forecast(horizon=1)
    next_day_vol = np.sqrt(forecast.variance.iloc[-1, 0]) / 100  # variance → std dev, scale back

    garch_forecasts[ticker] = next_day_vol

    # Print model parameters
    print(f"\n{ticker} GARCH(1,1) Parameters:")
    print(f"  omega:      {fitted.params['omega']:.6f}  (baseline variance)")
    print(f"  alpha:      {fitted.params['alpha[1]']:.4f}  (shock reaction)")
    print(f"  beta:       {fitted.params['beta[1]']:.4f}  (persistence)")
    print(f"  alpha+beta: {fitted.params['alpha[1]'] + fitted.params['beta[1]']:.4f}  (total persistence)")
    print(f"  Next-day forecasted vol (annualized): {next_day_vol * np.sqrt(252):.4f}")

# Build DataFrame of conditional volatilities for all tickers
conditional_vol_df = pd.DataFrame(garch_conditional_vol, index=log_returns.index)

print(f"\nGARCH Forecasted Next-Day Volatility (annualized):")
for ticker in tickers:
    print(f"  {ticker}: {garch_forecasts[ticker] * np.sqrt(252):.4f}")

# Export
conditional_vol_df.to_csv("data/garch_conditional_vol.csv")
print("\nExported: garch_conditional_vol")
