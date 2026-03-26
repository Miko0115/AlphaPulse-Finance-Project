"""
AlphaPulse — K-Means Regime Detection & Regime-Aware Monte Carlo
Classifies each trading day as Calm, Stress, or Crisis using unsupervised
clustering, then runs a Monte Carlo simulation conditioned on the current regime.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load data and compute log returns
df = pd.read_csv("data/stock_data.csv", header=[0, 1], index_col=0, parse_dates=True)
tickers = ["AAPL", "UNH", "JPM", "XOM", "AMZN"]

close_prices = df.loc[:, (tickers, "Close")]
close_prices.columns = tickers
log_returns = np.log(close_prices / close_prices.shift(1)).dropna()

weights = np.array([1/len(tickers)] * len(tickers))

# PART 1: K-MEANS REGIME DETECTION

# Step 1: Engineer features for clustering
portfolio_returns = log_returns @ weights                              # weighted daily return
rolling_vol = portfolio_returns.rolling(window=30).std() * np.sqrt(252)  # 30-day annualized vol
avg_abs_return = log_returns.abs().mean(axis=1)                        # shock magnitude

features = pd.DataFrame({
    "portfolio_return": portfolio_returns,
    "rolling_vol": rolling_vol,
    "avg_abs_return": avg_abs_return
}, index=log_returns.index).dropna()

# Step 2: Standardize features (K-Means uses Euclidean distance)
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Step 3: Fit K-Means with 3 clusters
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(features_scaled)
features["regime"] = kmeans.labels_

# Step 4: Map cluster numbers to labels by ascending volatility
regime_stats_temp = features.groupby('regime').agg({
    "rolling_vol": "mean",
    "avg_abs_return": "mean"
}).sort_values("rolling_vol")

sorted_regimes = regime_stats_temp.index.tolist()
regime_map = {
    sorted_regimes[0]: "Calm",                         # lowest avg volatility
    sorted_regimes[1]: "Stress",                       # middle avg volatility
    sorted_regimes[2]: "Crisis"                        # highest avg volatility
}
features["regime_label"] = features["regime"].map(regime_map)

# Step 5: Print regime analysis
print("Regime Detection Results")
print(f"{'='*50}")
print(f"\nRegime distribution:")
print(features['regime_label'].value_counts().sort_index())

print(f"\nRegime characteristics (mean values):")
regime_stats = features.groupby('regime_label')[['portfolio_return', 'rolling_vol', 'avg_abs_return']].mean()
regime_stats['portfolio_return'] = regime_stats['portfolio_return'] * 252  # annualize
print(regime_stats.round(4))

print(f"\nRegime date ranges:")
for label in ['Calm', 'Stress', 'Crisis']:
    regime_dates = features[features["regime_label"] == label].index
    if len(regime_dates) > 0:
        print(f"  {label}: {regime_dates[0].date()} to {regime_dates[-1].date()} ({len(regime_dates)} days)")

# Step 6: Identify crisis episodes (consecutive crisis days)
print(f"\nCrisis episodes:")
crisis_dates = features[features["regime_label"] == "Crisis"].index.tolist()

if len(crisis_dates) > 0:
    episodes = []
    ep_start = crisis_dates[0]
    ep_end = crisis_dates[0]

    for i in range(1, len(crisis_dates)):
        if (crisis_dates[i] - crisis_dates[i-1]).days > 5:  # gap > 5 days = new episode
            episodes.append((ep_start, ep_end))
            ep_start = crisis_dates[i]
        ep_end = crisis_dates[i]
    episodes.append((ep_start, ep_end))

    for start, end in episodes:
        duration = (end - start).days
        if duration > 0:                               # skip single-day blips
            print(f"  {start.date()} to {end.date()} ({duration} days)")

# PART 2: REGIME-AWARE MONTE CARLO

num_simulations = 10000
num_days = 252
num_assets = len(tickers)
mc_weights = np.array([1/num_assets] * num_assets)

# Step 7: Compute regime-specific covariance matrices
regime_cov_matrices = {}
regime_mean_returns = {}

for label in ['Calm', 'Stress', 'Crisis']:
    regime_dates = features[features["regime_label"] == label].index
    regime_rets = log_returns.loc[regime_dates]
    regime_cov_matrices[label] = regime_rets.cov().values
    regime_mean_returns[label] = regime_rets.mean().values

print("\nRegime-specific covariance matrices (annualized):")
for label in ['Calm', 'Stress', 'Crisis']:
    annual_cov = regime_cov_matrices[label] * 252
    print(f"\n  {label} regime:")
    print(pd.DataFrame(annual_cov, index=tickers, columns=tickers).round(4))

# Step 8: Detect current regime
last_features = features_scaled[-1].reshape(1, -1)
current_regime_num = kmeans.predict(last_features)[0]
current_regime = regime_map[current_regime_num]

print(f"\nCurrent market regime (last trading day): {current_regime}")

# Step 9: Simulate using current regime's covariance
current_cov = regime_cov_matrices[current_regime]
current_mean = regime_mean_returns[current_regime]
L_regime = np.linalg.cholesky(current_cov)             # Cholesky of regime covariance

portfolio_returns_regime = np.zeros(num_simulations)
np.random.seed(42)

for sim in range(num_simulations):
    portfolio_value = 1.0
    for day in range(num_days):
        Z = np.random.standard_normal(num_assets)
        correlated_returns = current_mean + L_regime @ Z
        daily_return = np.dot(mc_weights, correlated_returns)
        portfolio_value *= np.exp(daily_return)
    portfolio_returns_regime[sim] = portfolio_value

# Results
pct_returns_regime = (portfolio_returns_regime - 1) * 100

var_95_regime = np.percentile(pct_returns_regime, 5)
var_99_regime = np.percentile(pct_returns_regime, 1)
cvar_95_regime = pct_returns_regime[pct_returns_regime <= var_95_regime].mean()
cvar_99_regime = pct_returns_regime[pct_returns_regime <= var_99_regime].mean()

print(f"\nRegime-Aware Monte Carlo ({num_simulations:,} simulations)")
print(f"Current regime: {current_regime}")
print(f"{'='*50}")
print(f"Mean return:   {np.mean(pct_returns_regime):+.2f}%")
print(f"Median return: {np.median(pct_returns_regime):+.2f}%")
print(f"Std dev:       {np.std(pct_returns_regime):.2f}%")
print(f"Best case:     {np.max(pct_returns_regime):+.2f}%")
print(f"Worst case:    {np.min(pct_returns_regime):+.2f}%")
print(f"\nRisk Metrics:")
print(f"  VaR 95%:  {var_95_regime:+.2f}%")
print(f"  VaR 99%:  {var_99_regime:+.2f}%")
print(f"  CVaR 95%: {cvar_95_regime:+.2f}%")
print(f"  CVaR 99%: {cvar_99_regime:+.2f}%")

# Comparison across all three MC methods
print(f"\n{'='*60}")
print(f"Comparison: Basic MC vs GARCH MC vs Regime MC ({current_regime})")
print(f"{'='*60}")
print(f"{'Metric':<20} {'Basic MC':>12} {'GARCH MC':>12} {'Regime MC':>12}")
print(f"{'Mean return':<20} {'+21.84%':>12} {'+21.72%':>12} {np.mean(pct_returns_regime):>+12.2f}%")
print(f"{'VaR 95%':<20} {'-14.20%':>12} {'-12.97%':>12} {var_95_regime:>+12.2f}%")
print(f"{'VaR 99%':<20} {'-24.27%':>12} {'-23.18%':>12} {var_99_regime:>+12.2f}%")
print(f"{'CVaR 95%':<20} {'-20.42%':>12} {'-19.15%':>12} {cvar_95_regime:>+12.2f}%")
print(f"{'CVaR 99%':<20} {'-28.67%':>12} {'-27.71%':>12} {cvar_99_regime:>+12.2f}%")
print(f"{'Worst case':<20} {'-41.01%':>12} {'-41.88%':>12} {np.min(pct_returns_regime):>+12.2f}%")

# Export
features[['regime_label']].to_csv("data/regime_labels.csv")

pd.DataFrame({
    'Final Value': portfolio_returns_regime,
    'Pct Return': pct_returns_regime
}).to_csv("data/regime_mc_results.csv", index=False)

print("\nExported: regime_labels, regime_mc_results")
