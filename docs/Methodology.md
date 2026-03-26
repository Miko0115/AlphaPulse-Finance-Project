# AlphaPulse — Methodology Document

## Project Overview

**Project:** Portfolio Risk & Volatility Monitor
**Author:** Param Chaudhary
**Date:** March 2026
**Data Period:** January 2, 2015 – December 31, 2024 (10 years, 2,516 trading days)

### Objective

Build a quantitative risk analysis pipeline that measures, forecasts, and visualizes portfolio risk using Monte Carlo simulation, GARCH volatility modeling, and K-Means regime detection — then present the results in an interactive Power BI dashboard for stakeholder decision-making.

### Portfolio Composition

| Ticker | Company | Sector | Weight |
|--------|---------|--------|--------|
| AAPL | Apple Inc. | Technology | 20% |
| UNH | UnitedHealth Group | Healthcare | 20% |
| JPM | JPMorgan Chase | Financials | 20% |
| XOM | ExxonMobil | Energy | 20% |
| AMZN | Amazon.com | Consumer Discretionary | 20% |

**Selection rationale:** Five large-cap, highly liquid stocks from five different GICS sectors to ensure diversification. Each stock has 10+ years of trading history with no delistings, ensuring complete data coverage. Equal weighting (1/N) was chosen for simplicity and transparency — it avoids optimization bias and is a well-documented baseline in portfolio theory (DeMiguel et al., 2009).

**Note on UNH:** UnitedHealth Group replaced Johnson & Johnson (JNJ) in the portfolio after discovering that JNJ's Kenvue consumer health spinoff in May 2023 created a structural break in the time series. Pre-spinoff and post-spinoff JNJ are fundamentally different companies, which would contaminate covariance estimates and regime detection. UNH provides clean, continuous healthcare sector exposure over the full 10-year window.

---

## 1. Data Acquisition & Cleaning

### 1.1 Data Source

- **Provider:** Yahoo Finance via the `yfinance` Python library (v0.2+)
- **Data type:** Daily OHLCV (Open, High, Low, Close, Volume)
- **Adjustment:** `auto_adjust=True` — all historical prices are retroactively adjusted for stock splits and dividend distributions
- **Date range:** Fixed at 2015-01-01 to 2025-01-01 for reproducibility

### 1.2 Missing Data Handling

- **Method:** Forward fill (`ffill`) followed by backward fill (`bfill`)
- **Rationale:** Forward fill is the industry standard for financial time series — "no trade" means "the price didn't change." Backward fill is applied only as a safety net for potential leading NaN values on the first row.
- **Result:** Zero missing values detected across all 5 tickers and all 25 columns (5 tickers × 5 OHLCV fields)

### 1.3 Data Validation

- **Anomaly detection:** Computed daily percentage returns for each ticker and flagged any day with a return exceeding ±50% as a potential stock split artifact or data error
- **Threshold rationale:** The largest single-day moves in US large-cap stock history are approximately ±25%. A 50% threshold provides ample margin to avoid false positives while catching genuine data quality issues
- **Result:** Zero anomalies detected across all 5 tickers, confirming that `auto_adjust=True` correctly handled:
  - AAPL 4:1 stock split (August 31, 2020)
  - AMZN 20:1 stock split (June 6, 2022)

### 1.4 Assumptions

- Yahoo Finance data is accurate and complete for the selected tickers and date range
- Adjusted close prices correctly account for all corporate actions
- The portfolio is rebalanced daily to maintain equal weights (theoretical assumption — in practice, this would incur transaction costs)
- No transaction costs, taxes, or slippage are modeled

---

## 2. Returns Calculation

### 2.1 Log Returns

- **Formula:** `r(t) = ln(P(t) / P(t-1))` where P(t) is the adjusted close price on day t
- **Why log returns over simple returns:**
  1. **Time additivity:** Log returns can be summed across periods: `r(1→3) = r(1→2) + r(2→3)`. Simple returns cannot.
  2. **Symmetry:** A +5% and -5% log return are symmetric around zero. Simple returns are not (a +50% followed by -50% results in a 25% loss, not breakeven).
  3. **Normality assumption:** Log returns more closely approximate a normal distribution, which is a core assumption for Monte Carlo simulation and GARCH modeling.
- **Result:** 2,515 daily log return observations per ticker (one less than price observations due to differencing)

### 2.2 Summary Statistics

| Ticker | Annual Return | Annual Volatility | Sharpe Ratio |
|--------|--------------|-------------------|-------------|
| AAPL | 23.35% | 28.47% | 0.6711 |
| UNH | 17.69% | 26.19% | 0.5131 |
| JPM | 16.17% | 27.32% | 0.4365 |
| XOM | 5.84% | 27.79% | 0.0573 |
| AMZN | 26.60% | 32.66% | 0.6844 |
| **Portfolio** | **17.93%** | **20.13%** | **0.6795** |

### 2.3 Annualization

- **Returns:** Daily mean × 252 (trading days per year)
- **Volatility:** Daily std × √252
- **Rationale:** Based on the i.i.d. assumption — daily returns are assumed to be independent and identically distributed. Returns scale linearly with time; variance scales linearly, so standard deviation scales with the square root.

---

## 3. Covariance & Correlation Analysis

### 3.1 Covariance Matrix

- **Method:** `pandas.DataFrame.cov()` on daily log returns, then annualized by multiplying by 252
- **Purpose:** Captures both individual asset variance (diagonal) and pairwise co-movement (off-diagonal). Required for Cholesky decomposition and portfolio variance calculation.

### 3.2 Correlation Matrix

Key pairwise correlations:

| Pair | Correlation | Interpretation |
|------|-------------|---------------|
| AAPL–AMZN | 0.557 | Highest — both tech-adjacent growth stocks |
| JPM–XOM | 0.559 | Both cyclical/value stocks, sensitive to economic cycles |
| XOM–AMZN | 0.182 | Lowest — best diversifier pair (energy vs tech) |
| UNH–AMZN | 0.259 | Low — healthcare vs tech, independent drivers |

### 3.3 Diversification Benefit

- Average individual volatility: 28.49%
- Portfolio volatility: 20.13%
- **Diversification reduction: 8.36 percentage points** (29.3% reduction in risk)
- This reduction is driven by correlations below 1.0, particularly the low XOM–AMZN (0.18) and UNH–AMZN (0.26) pairs

### 3.4 Cholesky Decomposition

- **Method:** `numpy.linalg.cholesky()` on the daily covariance matrix
- **Purpose:** Produces a lower triangular matrix L such that Σ = L × Lᵀ. Used in Monte Carlo simulation to transform independent random samples into correlated samples that respect the portfolio's correlation structure.
- **Verification:** Reconstruction error (max absolute difference between original and reconstructed covariance matrix): 1.39 × 10⁻¹⁷ — effectively zero, confirming numerical accuracy.

### 3.5 Assumptions

- Correlations are stationary over the observation period (violated during crises — addressed by regime-aware analysis in Section 7)
- The covariance matrix is positive definite (verified by successful Cholesky decomposition)

---

## 4. Monte Carlo Simulation (Baseline)

### 4.1 Method

- **Model:** Geometric Brownian Motion (GBM)
- **Formula:** `r(t) = μ + L × Z` where μ = mean daily returns, L = Cholesky matrix, Z ~ N(0,1)
- **Price update:** `P(t+1) = P(t) × exp(r(t))`
- **Simulations:** 10,000 independent paths
- **Horizon:** 252 trading days (1 year)
- **Portfolio weights:** Equal (20% each)
- **Random seed:** 42 (for reproducibility)

### 4.2 Results

| Metric | Value |
|--------|-------|
| Mean return | +21.84% |
| Median return | +19.16% |
| Standard deviation | 24.84% |
| Best case | +166.43% |
| Worst case | -41.01% |

### 4.3 Assumptions

- Daily log returns follow a multivariate normal distribution (simplification — real returns exhibit fat tails and skewness)
- Returns are independent across time (no serial correlation or volatility clustering — addressed by GARCH in Section 6)
- The drift (mean return) and covariance matrix are constant over the simulation horizon
- No regime changes during the simulation period (addressed by regime-aware MC in Section 7)

---

## 5. Value at Risk & Expected Shortfall

### 5.1 VaR (Value at Risk)

- **Method:** Historical simulation — computed as percentiles of the Monte Carlo return distribution
- **VaR 95%:** -14.20% (the 5th percentile of 10,000 simulated returns)
- **VaR 99%:** -24.27% (the 1st percentile)
- **Interpretation:** "With 95% confidence, the portfolio will not lose more than 14.20% over one year"

### 5.2 CVaR (Conditional VaR / Expected Shortfall)

- **Method:** Average of all simulated returns below the VaR threshold
- **CVaR 95%:** -20.42% (average loss in the worst 5% of scenarios, ~500 simulations)
- **CVaR 99%:** -28.67% (average loss in the worst 1% of scenarios, ~100 simulations)
- **Why CVaR in addition to VaR:** VaR only tells us the threshold — it does not describe how bad losses get beyond that point. CVaR captures the expected loss in the tail, making it a more informative risk metric. Basel III/IV regulations increasingly require Expected Shortfall as the primary risk measure.

### 5.3 Assumptions

- The Monte Carlo distribution is a reasonable approximation of the true return distribution
- VaR and CVaR are computed from a single simulation run (10,000 paths). Simulation error is approximately ±1-2% at the 95th percentile level given the sample size.

---

## 6. GARCH(1,1) Volatility Forecasting

### 6.1 Model Specification

- **Model:** GARCH(1,1) — Generalized Autoregressive Conditional Heteroskedasticity
- **Formula:** `σ²(t) = ω + α × r²(t-1) + β × σ²(t-1)`
- **Library:** `arch` Python package
- **Estimation:** Maximum Likelihood Estimation (MLE) with normal distribution assumption
- **Input:** Daily log returns scaled to percentages (×100) for numerical stability

### 6.2 Fitted Parameters

| Ticker | ω (omega) | α (alpha) | β (beta) | α + β | Interpretation |
|--------|-----------|-----------|----------|-------|---------------|
| AAPL | 0.1437 | 0.1044 | 0.8492 | 0.954 | Balanced shock reaction and persistence |
| UNH | 0.0866 | 0.0676 | 0.8967 | 0.964 | High persistence, low shock reaction |
| JPM | 0.1974 | 0.1299 | 0.7911 | 0.921 | Most reactive to news |
| XOM | 0.0174 | 0.0823 | 0.9146 | 0.997 | Near unit root — shocks almost never fade |
| AMZN | 0.3199 | 0.2010 | 0.7445 | 0.946 | Highest shock reaction, fastest mean reversion |

### 6.3 Interpretation

- **α (alpha)** measures how strongly today's volatility reacts to yesterday's return shock. AMZN has the highest α (0.20) — its volatility spikes sharply after surprises (e.g., earnings).
- **β (beta)** measures volatility persistence. XOM has the highest β (0.91) — once volatility rises, it stays elevated for extended periods (geopolitical events create lasting uncertainty in energy markets).
- **α + β < 1** is required for stationarity. All tickers satisfy this condition, though XOM is very close to the boundary (0.997), suggesting near-integrated behavior.

### 6.4 GARCH-Enhanced Monte Carlo

- **Modification:** Instead of a constant covariance matrix, volatility is updated daily using the GARCH equation. Correlations remain static; only variances change.
- **Covariance reconstruction:** `Cov(t) = D(t) × Corr × D(t)` where D(t) is a diagonal matrix of GARCH standard deviations
- **Starting point:** The last known conditional variance from the fitted model (reflects current market conditions)

### 6.5 GARCH MC Results vs Baseline

| Metric | Basic MC | GARCH MC |
|--------|----------|----------|
| Mean return | +21.84% | +21.72% |
| VaR 95% | -14.20% | -12.97% |
| VaR 99% | -24.27% | -23.18% |
| CVaR 95% | -20.42% | -19.15% |

GARCH MC shows tighter risk estimates because the model was conditioned on a **low-volatility market state** at the end of 2024. In a high-volatility regime, GARCH would produce wider tails. This adaptiveness is precisely the value of GARCH — it reflects current conditions rather than historical averages.

### 6.6 Assumptions

- Volatility follows a GARCH(1,1) process (higher-order models like GARCH(2,1) or EGARCH were not tested)
- Return innovations are normally distributed (in reality, financial returns have fat tails — a Student-t distribution would be more accurate)
- Correlations between assets remain constant even as individual variances change (a simplification — full DCC-GARCH would model dynamic correlations)

---

## 7. K-Means Regime Detection

### 7.1 Method

- **Algorithm:** K-Means clustering (scikit-learn)
- **Number of clusters:** K=3 (Calm, Stress, Crisis)
- **Feature engineering:** Three features per trading day:
  1. **Portfolio daily return** — weighted average log return across 5 stocks
  2. **30-day rolling volatility** — annualized standard deviation of portfolio returns over a 30-day window
  3. **Average absolute return** — mean |return| across all 5 stocks (captures shock magnitude)
- **Preprocessing:** StandardScaler (z-score normalization) — required because K-Means uses Euclidean distance and features have different scales
- **Initialization:** 10 random restarts (`n_init=10`), best result selected by inertia
- **Random seed:** 42

### 7.2 Regime Characteristics

| Regime | Days | % of Data | Annualized Return | Avg Rolling Vol | Avg |Return| |
|--------|------|-----------|-------------------|-----------------|----------------|
| Calm | 2,061 | 83% | +11.93% | 14.87% | 0.95% |
| Stress | 161 | 6% | -68.13% | 28.32% | 2.95% |
| Crisis | 264 | 11% | +48.52% | 30.84% | 2.36% |

### 7.3 Regime Labeling Logic

- Clusters are assigned labels based on average rolling volatility: lowest = Calm, middle = Stress, highest = Crisis
- **Important finding:** The "Crisis" regime shows positive annualized returns (+48.52%) because it captures both sharp crashes AND sharp recoveries (e.g., the COVID V-shaped bounce had extreme volatility with positive returns). The "Stress" regime shows the most consistently negative returns (-68.13%) — these are slow-grinding selloffs like the 2022 rate hike cycle.

### 7.4 Validation Against Known Events

| Known Event | Date | Detected? |
|-------------|------|:---------:|
| China devaluation / oil crash | Aug–Sep 2015 | Yes |
| Worst January since 2009 | Jan 2016 | Yes |
| Volmageddon | Feb 2018 | Yes |
| Fed tightening selloff | Oct–Dec 2018 | Yes |
| COVID-19 crash | Mar–May 2020 | Yes (71 consecutive crisis days) |
| 2022 rate hiking cycle | Jan–Oct 2022 | Yes (scattered episodes) |
| SVB banking crisis | Mar 2023 | Yes |

### 7.5 Regime-Aware Monte Carlo

- **Method:** Compute a separate covariance matrix for each regime. Detect the current regime using the last trading day's features. Simulate using the current regime's covariance matrix and mean returns.
- **Current regime (Dec 31, 2024):** Calm

| Metric | Basic MC | GARCH MC | Regime MC (Calm) |
|--------|----------|----------|-----------------|
| Mean return | +21.84% | +21.72% | +13.25% |
| VaR 95% | -14.20% | -12.97% | -6.28% |
| VaR 99% | -24.27% | -23.18% | -12.51% |
| CVaR 95% | -20.42% | -19.15% | -10.14% |

The Regime MC in Calm mode shows significantly lower risk because it uses only the Calm regime's covariance matrix, which has 2-4× smaller variances and lower correlations than the full-sample matrix.

### 7.6 Assumptions

- K=3 is the correct number of regimes (not validated with silhouette score or elbow method — could be explored further)
- The current regime persists for the entire 252-day simulation horizon (no regime transitions modeled — a Markov switching model would address this)
- K-Means assumes spherical, equal-size clusters in feature space (may not hold — Gaussian Mixture Models would allow for ellipsoidal clusters)
- Features are sufficient to distinguish regimes (other features like credit spreads, VIX, or yield curve slope could improve detection)

---

## 8. Rolling Volatility

### 8.1 Method

- **Window:** 30 trading days (~1 calendar month)
- **Formula:** Standard deviation of daily log returns within the window, annualized by × √252
- **Purpose:** Provides a time-varying measure of risk that complements the static covariance matrix and GARCH model

### 8.2 Key Observations

| Period | Portfolio Rolling Vol | Market Context |
|--------|---------------------|---------------|
| Mid-2017 (calm) | ~10-12% | Historic low VIX, S&P 500 rose every month |
| March 2020 (COVID peak) | ~60-120% per stock | Fastest bear market in history |
| Dec 2024 (latest) | 14-39% per stock | Mixed — UNH elevated, others calm |

### 8.3 Window Size Rationale

- 30 days balances responsiveness and smoothness
- Shorter windows (5-10 days) produce noisy estimates
- Longer windows (90+ days) over-smooth and fail to capture rapid regime changes

---

## 9. Sharpe Ratio

### 9.1 Method

- **Formula:** `Sharpe = (R_p - R_f) / σ_p`
- **Risk-free rate:** 4.25% (approximate 10-year US Treasury yield as of late 2024)
- **Portfolio return:** 17.93% (annualized)
- **Portfolio volatility:** 20.13% (annualized)
- **Result:** 0.6795

### 9.2 Interpretation

- A Sharpe ratio of 0.68 indicates decent risk-adjusted performance — the portfolio earns approximately 0.68 units of excess return per unit of risk
- The portfolio Sharpe (0.68) exceeds 4 out of 5 individual stock Sharpes, demonstrating the diversification benefit
- Only AMZN (0.68) marginally exceeds the portfolio Sharpe

### 9.3 Assumptions

- The risk-free rate is constant over the analysis period (in reality, it varied from ~1.5% to ~5% during 2015-2024)
- Returns are normally distributed (Sharpe ratio is less meaningful for non-normal distributions)

---

## 10. Dashboard & Visualization

### 10.1 Tool

- **Platform:** Microsoft Power BI Desktop
- **Pages:** 3 (Portfolio Risk Monitor, Detailed Analytics, Executive Summary)

### 10.2 Interactive Features

- **Investment Amount slider:** $10,000 – $1,000,000 (updates VaR and CVaR in dollar terms)
- **Confidence Level slider:** 90% – 99% (recalculates VaR percentile from the MC distribution)

### 10.3 Key Visualizations

| Visual | Data Source | Purpose |
|--------|-----------|---------|
| KPI Cards | DAX measures | At-a-glance portfolio health |
| MC Histogram | 30,000 simulations (3 types) | Return distribution comparison |
| Correlation Heatmap | Matrix visual with conditional formatting | Diversification quality |
| Rolling Volatility | Line chart with event annotations | Risk evolution over time |
| GARCH vs Rolling Vol | Dual-line comparison | Forward-looking vs backward-looking vol |
| Regime Timeline | Color-coded scatter/line | K-Means regime classification |

---

## 11. Known Limitations

1. **Normal distribution assumption** — MC underestimates tail risk due to fat tails and negative skewness.
2. **Static correlations in GARCH MC** — volatility is time-varying but correlations are held fixed.
3. **No regime transitions in simulation** — each MC path assumes one regime for the full 252-day horizon.
4. **Equal weighting** — simple and robust, but does not optimize risk-adjusted returns.
5. **No transaction costs** — daily rebalancing is assumed without friction.
6. **US large-cap equities only** — no bonds, commodities, or international diversification.
7. **Survivorship bias** — only stocks that survived the full 10-year period are included.

---

## 12. Technical Stack

| Component | Technology |
|-----------|-----------|
| Data fetching | Python, yfinance |
| Analysis | NumPy, pandas |
| GARCH modeling | arch (Python) |
| Regime detection | scikit-learn (KMeans) |
| Visualization | Power BI Desktop |
| Version control | Git |

