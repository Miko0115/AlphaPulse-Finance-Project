"""
AlphaPulse — GARCH-Enhanced Monte Carlo Simulation
Runs 10,000 simulations with daily-updated GARCH volatility,
producing more realistic risk estimates than the static baseline MC.
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

# Simulation parameters
num_simulations = 10000
num_days = 252
num_assets = len(tickers)
weights = np.array([1/num_assets] * num_assets)

# Step 1: Fit GARCH(1,1) and extract parameters
garch_params = {}                                      # ω, α, β per ticker
last_variance = {}                                     # last observed conditional variance
last_return = {}                                       # last observed return

for ticker in tickers:
    returns = log_returns[ticker] * 100                # scale to percentage for GARCH
    model = arch_model(returns, vol="GARCH", p=1, q=1, dist="normal")
    fitted = model.fit(disp="off")

    garch_params[ticker] = {
        'omega': fitted.params['omega'],
        'alpha': fitted.params['alpha[1]'],
        'beta': fitted.params['beta[1]']
    }
    last_variance[ticker] = fitted.conditional_volatility.iloc[-1] ** 2
    last_return[ticker] = returns.iloc[-1]

# Step 2: Static correlation matrix (variances change, correlations don't)
correlation_matrix = log_returns.corr().values
mean_daily_returns = log_returns.mean().values

# Step 3: Run GARCH-enhanced Monte Carlo
portfolio_returns_garch = np.zeros(num_simulations)
np.random.seed(42)

for sim in range(num_simulations):
    portfolio_value = 1.0
    # Initialize variances from last known GARCH state
    current_var = np.array([last_variance[t] for t in tickers])

    for day in range(num_days):
        # Build today's covariance from GARCH variances + static correlations
        current_std = np.sqrt(current_var) / 100       # convert %² → decimal std dev
        D = np.diag(current_std)                       # diagonal matrix of std devs
        cov_matrix = D @ correlation_matrix @ D        # Cov = D × Corr × D

        # Cholesky decomposition for correlated sampling
        L = np.linalg.cholesky(cov_matrix)
        Z = np.random.standard_normal(num_assets)
        correlated_returns = mean_daily_returns + L @ Z

        # Update portfolio
        daily_portfolio_return = np.dot(weights, correlated_returns)
        portfolio_value *= np.exp(daily_portfolio_return)

        # Update GARCH variances for next day: σ²(t+1) = ω + α×r²(t) + β×σ²(t)
        for i, ticker in enumerate(tickers):
            p = garch_params[ticker]
            r_pct = correlated_returns[i] * 100        # convert back to % for GARCH equation
            current_var[i] = p['omega'] + p['alpha'] * r_pct**2 + p['beta'] * current_var[i]

    portfolio_returns_garch[sim] = portfolio_value

# Results
pct_returns_garch = (portfolio_returns_garch - 1) * 100

var_95_garch = np.percentile(pct_returns_garch, 5)
var_99_garch = np.percentile(pct_returns_garch, 1)
cvar_95_garch = pct_returns_garch[pct_returns_garch <= var_95_garch].mean()
cvar_99_garch = pct_returns_garch[pct_returns_garch <= var_99_garch].mean()

print(f"GARCH-Enhanced Monte Carlo ({num_simulations:,} simulations)")
print(f"{'='*50}")
print(f"Mean return:   {np.mean(pct_returns_garch):+.2f}%")
print(f"Median return: {np.median(pct_returns_garch):+.2f}%")
print(f"Std dev:       {np.std(pct_returns_garch):.2f}%")
print(f"Best case:     {np.max(pct_returns_garch):+.2f}%")
print(f"Worst case:    {np.min(pct_returns_garch):+.2f}%")
print(f"\nRisk Metrics:")
print(f"  VaR 95%:  {var_95_garch:+.2f}%")
print(f"  VaR 99%:  {var_99_garch:+.2f}%")
print(f"  CVaR 95%: {cvar_95_garch:+.2f}%")
print(f"  CVaR 99%: {cvar_99_garch:+.2f}%")

# Comparison with basic MC
print(f"\n{'='*50}")
print(f"Comparison: Basic MC vs GARCH MC")
print(f"{'Metric':<20} {'Basic MC':>12} {'GARCH MC':>12}")
print(f"{'Mean return':<20} {'+21.84%':>12} {np.mean(pct_returns_garch):>+12.2f}%")
print(f"{'VaR 95%':<20} {'-14.20%':>12} {var_95_garch:>+12.2f}%")
print(f"{'VaR 99%':<20} {'-24.27%':>12} {var_99_garch:>+12.2f}%")
print(f"{'CVaR 95%':<20} {'-20.42%':>12} {cvar_95_garch:>+12.2f}%")
print(f"{'CVaR 99%':<20} {'-28.67%':>12} {cvar_99_garch:>+12.2f}%")
print(f"{'Worst case':<20} {'-41.01%':>12} {np.min(pct_returns_garch):>+12.2f}%")

# Export
pd.DataFrame({
    'Final Value': portfolio_returns_garch,
    'Pct Return': pct_returns_garch
}).to_csv("data/garch_mc_results.csv", index=False)

print("\nExported: garch_mc_results")
