import pandas as pd
import numpy as np

# --- 1. Reshape correlation matrix from wide to long format ---
# Power BI can't easily visualize a 5x5 matrix. Convert to: Ticker1, Ticker2, Correlation
corr = pd.read_csv("data/correlation_matrix.csv", index_col=0)
corr_long = corr.reset_index().melt(
    id_vars='index',
    var_name='Ticker2',
    value_name='Correlation'
)
corr_long.rename(columns={'index': 'Ticker1'}, inplace=True)
corr_long.to_csv("data/pbi_correlation_heatmap.csv", index=False)
print("Created: data/pbi_correlation_heatmap.csv")

# --- 2. Combine all three MC results for overlay comparison ---
basic_mc = pd.read_csv("data/monte_carlo_results.csv")
basic_mc['MC_Type'] = 'Basic MC'

garch_mc = pd.read_csv("data/garch_mc_results.csv")
garch_mc['MC_Type'] = 'GARCH MC'

regime_mc = pd.read_csv("data/regime_mc_results.csv")
regime_mc['MC_Type'] = 'Regime MC'

# Standardize column names
basic_mc.columns = ['Final_Value', 'Pct_Return', 'MC_Type']
garch_mc.columns = ['Final_Value', 'Pct_Return', 'MC_Type']
regime_mc.columns = ['Final_Value', 'Pct_Return', 'MC_Type']

combined_mc = pd.concat([basic_mc, garch_mc, regime_mc], ignore_index=True)
combined_mc.to_csv("data/pbi_mc_combined.csv", index=False)
print("Created: data/pbi_mc_combined.csv")

# --- 3. Reshape rolling volatility from wide to long ---
# Wide format (Date, AAPL, UNH, ...) → Long format (Date, Ticker, Volatility)
rolling_vol = pd.read_csv("data/rolling_volatility_annualized.csv")
rolling_vol_long = rolling_vol.melt(
    id_vars='Date',
    var_name='Ticker',
    value_name='Volatility'
)
rolling_vol_long.to_csv("data/pbi_rolling_vol.csv", index=False)
print("Created: data/pbi_rolling_vol.csv")

# --- 4. Reshape GARCH conditional volatility from wide to long ---
garch_vol = pd.read_csv("data/garch_conditional_vol.csv")
garch_vol_long = garch_vol.melt(
    id_vars='Date',
    var_name='Ticker',
    value_name='GARCH_Vol'
)
garch_vol_long.to_csv("data/pbi_garch_vol.csv", index=False)
print("Created: data/pbi_garch_vol.csv")

# --- 5. Combine rolling vol + GARCH vol for comparison chart ---
rolling_vol_long['Vol_Type'] = 'Rolling 30-day'
rolling_vol_long.rename(columns={'Volatility': 'Vol_Value'}, inplace=True)

garch_vol_long['Vol_Type'] = 'GARCH'
garch_vol_long.rename(columns={'GARCH_Vol': 'Vol_Value'}, inplace=True)

vol_comparison = pd.concat([rolling_vol_long, garch_vol_long], ignore_index=True)
vol_comparison.to_csv("data/pbi_vol_comparison.csv", index=False)
print("Created: data/pbi_vol_comparison.csv")

# --- 6. Prepare regime labels with returns for timeline ---
# Merge regime labels with portfolio returns for the timeline chart
log_returns = pd.read_csv("data/log_returns.csv", index_col=0)
tickers = ["AAPL", "UNH", "JPM", "XOM", "AMZN"]
weights = [0.2, 0.2, 0.2, 0.2, 0.2]
portfolio_ret = (log_returns[tickers] * weights).sum(axis=1)

try:
    regime_labels = pd.read_csv("data/regime_labels.csv", index_col=0)
    regime_timeline = regime_labels.copy()
    regime_timeline['Portfolio_Return'] = portfolio_ret
    regime_timeline = regime_timeline.dropna()
    regime_timeline.to_csv("data/pbi_regime_timeline.csv")
    print("Created: data/pbi_regime_timeline.csv")
except FileNotFoundError:
    print("WARNING: regime_labels.csv not found. Re-run src/regime_detection.py first.")

print("\nAll Power BI data prep complete!")