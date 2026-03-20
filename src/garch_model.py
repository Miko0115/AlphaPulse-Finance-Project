import numpy as np
import pandas as pd
from arch import arch_model

df = pd.read_csv("data/stock_data.csv", header=[0, 1], index_col=0, parse_dates=True)
print(df.head())

tickers = ["AAPL", "UNH", "JPM", "XOM", "AMZN"]

close_prices = df.loc[:, (tickers, "Close")]
close_prices.columns = tickers
log_returns = np.log(close_prices / close_prices.shift(1)).dropna()

garch_results = {}
garch_forecasts = {}
garch_conditional_vol = {}

for ticker in tickers:
    returns = log_returns[ticker] * 100
    
    model = arch_model(
        returns,
        vol="GARCH",
        p=1,
        q=1,
        dist="normal"
    )
    
    fitted = model.fit(disp="off")
    garch_results[ticker] = fitted
    garch_conditional_vol[ticker] = fitted.conditional_volatility / 100
    
    forecast = fitted.forecast(horizon=1)
    next_day_vol = np.sqrt(forecast.variance.iloc[-1, 0]) / 100
    garch_forecasts[ticker] = next_day_vol
    
    #model parameters:
    print(f"\n{ticker} GARCH(1,1) Parameters:")
    print(f"omega: {fitted.params['omega']:.6f} baseline variance")
    print(f"alpha: {fitted.params['alpha[1]']:.4f} shock reaction")
    print(f"beta: {fitted.params['beta[1]']:.4f} persistance")
    print(f"alpha+beta: {fitted.params['alpha[1]'] + fitted.params['beta[1]']:.4f} total persistance")
    print(f"Next-day forecasted vol (annualized): {next_day_vol * np.sqrt(252):.4f}")
    
    conditional_vol_df = pd.DataFrame(garch_conditional_vol, index=log_returns.index)
    
print(f"\nGARCH forecasted next-day volatility (annualized):")
for ticker in tickers:
    print(f"{ticker}: {garch_forecasts[ticker] * np.sqrt(252):.4f}")
    
conditional_vol_df.to_csv("data/garch_conditional_vol.csv")
print("Exported: garch_conditional_vol")