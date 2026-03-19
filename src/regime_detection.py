import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("data/stock_data.csv", header=[0, 1], index_col=0, parse_dates=True)

tickers = ["AAPL", "UNH", "JPM", "XOM", "AMZN"]

close_prices = df.loc[:, (tickers, "Close")]
close_prices.columns = tickers
log_returns = np.log(close_prices / close_prices.shift(1)).dropna()

weights = np.array([1/len(tickers)] * len(tickers))

portfolio_returns = log_returns @ weights
rolling_vol = portfolio_returns.rolling(window=30).std() * np.sqrt(252)
avg_abs_return = log_returns.abs().mean(axis=1)

features = pd.DataFrame({
    "portfolio_return": portfolio_returns,
    "rolling_vol": rolling_vol,
    "avg_abs_return": avg_abs_return
}, index=log_returns.index).dropna()

scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)
kmeans.fit(features_scaled)

features["regime"] = kmeans.labels_

regime_stats_temp = features.groupby('regime').agg({
    "rolling_vol": "mean",
    "avg_abs_return": "mean"
}).sort_values("rolling_vol")

sorted_regimes = regime_stats_temp.index.tolist()
regime_map = {
    sorted_regimes[0]: "Calm",
    sorted_regimes[1]: "Stress",
    sorted_regimes[2]: "Crisis"
}
        
features["regime_label"] = features["regime"].map(regime_map)

print(f"Regime Detection Results")
print(f"\nRegime distribution:")
print(features['regime_label'].value_counts().sort_index())

print(f"\nRegime characteristics (mean values):")
regime_stats = features.groupby('regime_label')[['portfolio_return', 'rolling_vol', 'avg_abs_return']].mean()
regime_stats['portfolio_return'] = regime_stats['portfolio_return'] * 252    # annualize
print(regime_stats.round(4))

print(f"\nRegime date ranges (first and last occurrence):")
for label in ['Calm', 'Crisis', 'Stress']:
    regime_dates = features[features["regime_label"] == label].index
    if len(regime_dates) > 0:
        print(f"{label}: {regime_dates[0].date()} to {regime_dates[-1].date()} ({len(regime_dates)}) days")
    
print(f"\nCrisis regime dates:")
crisis_dates = features[features["regime_label"] == "Crisis"].index.tolist()

if len(crisis_dates) > 0:
    episodes = []
    ep_start = crisis_dates[0]
    ep_end = crisis_dates[0]
    
    for i in range(1, len(crisis_dates)):
        if (crisis_dates[i] - crisis_dates[i-1]).days > 5:
            episodes.append((ep_start, ep_end))
            ep_start = crisis_dates[i]
        ep_end = crisis_dates[i]
    episodes.append((ep_start, ep_end))

    for start, end in episodes:
        duration = (end - start).days
        if duration > 0:
            print(f"{start.date()} to {end.date()} ({duration}) days")
            

#regime monte carlo:
