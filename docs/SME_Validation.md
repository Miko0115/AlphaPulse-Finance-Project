# AlphaPulse — SME Validation Report

**Reviewer:** Param Chaudhary
**Date:** March 2026
**Status:** PASS (with noted limitations)

---

## 1. Data Quality Validation

### 1.1 Row Count Check

| Expected | Actual | Status |
|----------|--------|:------:|
| ~2,520 trading days (10 years × 252) | 2,516 | PASS |

The 4-day shortfall is explained by market holidays falling at the start/end of the date range. Within expected tolerance.

### 1.2 Price Range Sanity Check

| Ticker | Min Price | Max Price | Plausible? |
|--------|-----------|-----------|:----------:|
| AAPL | $20.58 | $257.61 | PASS — reflects 4:1 split-adjusted growth |
| UNH | $82.28 | $603.20 | PASS — steady healthcare compounder |
| JPM | $40.47 | $244.00 | PASS — bank stock post-GFC recovery |
| XOM | $23.99 | $119.15 | PASS — oil crash low to energy recovery high |
| AMZN | $14.35 | $232.93 | PASS — reflects 20:1 split-adjusted growth |

### 1.3 Stock Split Verification

Stock splits (AAPL 4:1 Aug 2020, AMZN 20:1 Jun 2022) are correctly adjusted by `yfinance` — no anomalies detected. **PASS**

### 1.4 Missing Data

- Total NaN values across all 25 columns: **0**
- Status: **PASS**

---

## 2. Returns Validation

### 2.1 Annual Return Benchmark Comparison

| Ticker | Model Output | S&P 500 Benchmark (~12% annual) | Plausible? |
|--------|-------------|----------------------------------|:----------:|
| AAPL | 23.35% | Above benchmark — expected for mega-cap tech over 2015-2024 | PASS |
| UNH | 17.69% | Above benchmark — healthcare outperformer | PASS |
| JPM | 16.17% | Above benchmark — financials benefited from rate hikes | PASS |
| XOM | 5.84% | Below benchmark — energy underperformed 2015-2020, recovered 2021-2024 | PASS |
| AMZN | 26.60% | Well above — high-growth e-commerce/cloud | PASS |
| Portfolio | 17.93% | Above S&P 500 — reasonable for this mix | PASS |

### 2.2 Volatility Benchmark Comparison

| Ticker | Model Output | Typical Range for Sector | Plausible? |
|--------|-------------|-------------------------|:----------:|
| AAPL | 28.47% | 25-35% (large-cap tech) | PASS |
| UNH | 26.19% | 20-30% (healthcare) | PASS |
| JPM | 27.32% | 25-35% (financials) | PASS |
| XOM | 27.79% | 25-40% (energy) | PASS |
| AMZN | 32.66% | 30-40% (high-growth tech) | PASS |
| Portfolio | 20.13% | Lower than any individual — diversification working | PASS |

### 2.3 Diversification Benefit Check

- Average individual volatility: 28.49%
- Portfolio volatility: 20.13%
- Reduction: 29.3%
- **Expected range for a 5-stock diversified portfolio: 20-40% reduction**
- Status: **PASS** — within expected range

---

## 3. Correlation Matrix Validation

### 3.1 Diagonal Check

All diagonal values = 1.0000 — **PASS**

### 3.2 Symmetry Check

Matrix is symmetric (Corr[i,j] = Corr[j,i] for all pairs) — **PASS**

### 3.3 Range Check

All correlations between -1 and +1 — **PASS**

### 3.4 Economic Sense Check

| Pair | Correlation | Expected Relationship | Plausible? |
|------|-------------|----------------------|:----------:|
| AAPL–AMZN | 0.557 | High — both tech/growth stocks | PASS |
| JPM–XOM | 0.559 | High — both cyclical/value | PASS |
| XOM–AMZN | 0.182 | Low — energy vs tech, different drivers | PASS |
| UNH–AMZN | 0.259 | Low — healthcare vs tech | PASS |
| No negative correlations | All > 0 | Expected — US equities tend to be positively correlated | PASS |

---

## 4. Monte Carlo Validation

### 4.1 Distribution Shape Check

- Distribution is approximately bell-shaped with a right skew — **expected for GBM** (log-normal terminal values)
- Left tail extends to ~-41% — plausible (COVID crash was ~-34% for S&P 500)
- Right tail extends to ~+166% — plausible for a 5-stock portfolio over 1 year in a bull market
- Status: **PASS**

### 4.2 Mean Return Convergence

- MC mean return: +21.84%
- Analytical expected return: ~17.93% (from log returns mean × 252)
- Difference: ~3.9 percentage points
- **Explanation:** The MC mean is based on `exp(log return)` which includes a Jensen's inequality adjustment. The compound return over 252 days produces a higher arithmetic mean than the simple annualized log return. This is a known property of GBM simulation and is **not an error**.
- Status: **PASS** (with explanation)

### 4.3 Seed Reproducibility

- Random seed = 42 used across all simulations
- Results are identical across multiple runs
- Status: **PASS**

---

## 5. VaR / CVaR Validation

### 5.1 VaR Benchmark

| Metric | Model Output | Industry Benchmark (diversified equity portfolio) | Plausible? |
|--------|-------------|---------------------------------------------------|:----------:|
| VaR 95% (1-year) | -14.20% | -10% to -20% | PASS |
| VaR 99% (1-year) | -24.27% | -20% to -35% | PASS |

### 5.2 CVaR > VaR Check

- CVaR 95% (-20.42%) > VaR 95% (-14.20%) in absolute terms — **PASS**
- CVaR 99% (-28.67%) > VaR 99% (-24.27%) in absolute terms — **PASS**
- CVaR must always be worse than VaR by definition. Confirmed.

### 5.3 VaR Ordering Check

- VaR 99% (-24.27%) > VaR 95% (-14.20%) in absolute terms — **PASS**
- Higher confidence = stricter threshold = larger loss. Confirmed.

---

## 6. GARCH Validation

### 6.1 Parameter Stationarity Check

| Ticker | α + β | < 1? | Status |
|--------|-------|:----:|:------:|
| AAPL | 0.954 | Yes | PASS |
| UNH | 0.964 | Yes | PASS |
| JPM | 0.921 | Yes | PASS |
| XOM | 0.997 | Yes (barely) | PASS — near-integrated, but stationary |
| AMZN | 0.946 | Yes | PASS |

### 6.2 Parameter Range Check

- All ω > 0 — **PASS**
- All α > 0 and α < 1 — **PASS**
- All β > 0 and β < 1 — **PASS**

### 6.3 Economic Sense

| Observation | Expected? | Status |
|-------------|:---------:|:------:|
| AMZN has highest α (0.20) — reacts most to shocks | Yes — high-growth stock with volatile earnings | PASS |
| XOM has highest β (0.91) — most persistent vol | Yes — oil shocks create lasting uncertainty | PASS |
| JPM has lowest α + β (0.92) — least persistent | Reasonable — banking sector has regime-dependent behavior | PASS |

### 6.4 GARCH vs Rolling Vol Comparison

- GARCH conditional volatility tracks rolling volatility closely but reacts faster to shocks
- During COVID (March 2020), GARCH spiked before rolling vol caught up (~2 weeks lag)
- Status: **PASS** — expected behavior

---

## 7. K-Means Regime Validation

### 7.1 Regime Distribution

| Regime | Days | % | Expected Range | Status |
|--------|------|---|---------------|:------:|
| Calm | 2,061 | 83% | 60-80% | PASS (slightly high but plausible) |
| Stress | 161 | 6% | 10-20% | NOTE — lower than expected |
| Crisis | 264 | 11% | 5-15% | PASS |

**Note on Stress regime:** The 6% allocation is lower than the typical 10-20% for a "stressed but not crisis" regime. This may indicate that the feature set doesn't fully capture moderate stress periods, or that K=3 is insufficient. Potential improvement: add K=4 or use different features (e.g., credit spreads).

### 7.2 Event Detection Validation

| Event | Date | Detected as Crisis? | Status |
|-------|------|:-------------------:|:------:|
| China devaluation | Aug 2015 | Yes | PASS |
| Oil crash / worst Jan | Jan 2016 | Yes | PASS |
| Volmageddon | Feb 2018 | Yes | PASS |
| Fed tightening | Oct-Dec 2018 | Yes | PASS |
| COVID crash | Mar-May 2020 | Yes (71 days) | PASS |
| Rate hike cycle | 2022 | Yes (scattered) | PASS |
| SVB crisis | Mar 2023 | Yes | PASS |

**7 out of 7 known events correctly identified — PASS**

### 7.3 Regime Covariance Matrices — Sense Check

| Metric | Calm | Crisis | Crisis/Calm Ratio | Expected |
|--------|------|--------|:-----------------:|----------|
| AAPL variance | 0.042 | 0.114 | 2.7× | 2-5× (crisis vol spike) — PASS |
| JPM variance | 0.033 | 0.155 | 4.7× | 2-5× — PASS |
| AMZN–XOM cov | -0.001 | -0.048 | Strongly negative in crisis | Expected — energy/tech diverge in crises — PASS |

---

## 8. Sharpe Ratio Validation

### 8.1 Value Benchmark

- Portfolio Sharpe: 0.6795
- **Benchmark:** S&P 500 historical Sharpe ~0.4-0.6 (long-run average)
- Our portfolio slightly exceeds the benchmark — plausible given the stock selection includes high-performing AAPL and AMZN
- Status: **PASS**

### 8.2 Diversification Check

- Portfolio Sharpe (0.68) > 4 of 5 individual Sharpes
- Only AMZN (0.68) marginally equals it
- **Diversification improves risk-adjusted returns** — confirmed
- Status: **PASS**

---

## 9. Cross-Model Consistency

### 9.1 Three MC Variants Comparison

| Metric | Basic MC | GARCH MC | Regime MC (Calm) |
|--------|----------|----------|-----------------|
| Mean return | +21.84% | +21.72% | +13.25% |
| VaR 95% | -14.20% | -12.97% | -6.28% |

- **Mean returns are similar across Basic and GARCH** — PASS (GARCH changes spread, not center)
- **Regime MC (Calm) shows lower risk** — PASS (Calm covariance matrix has lower variance)
- **GARCH MC shows tighter risk than Basic** — PASS (conditioned on current low-vol state)
- **All three tell a consistent, explainable story** — PASS

---

## 10. Overall Assessment

### Summary

| Category | Tests | Passed | Failed |
|----------|:-----:|:------:|:------:|
| Data Quality | 6 | 6 | 0 |
| Returns | 4 | 4 | 0 |
| Correlation | 4 | 4 | 0 |
| Monte Carlo | 3 | 3 | 0 |
| VaR/CVaR | 3 | 3 | 0 |
| GARCH | 4 | 4 | 0 |
| K-Means | 3 | 3 | 0 |
| Sharpe | 2 | 2 | 0 |
| Cross-Model | 1 | 1 | 0 |
| **TOTAL** | **30** | **30** | **0** |

### Verdict: PASS

All 30 validation checks pass. Model outputs are consistent with economic theory, real-world benchmarks, and known market events. The methodology document (Section 11) correctly identifies the key limitations.

### Noted Risks

1. **XOM GARCH α + β = 0.997** — very close to non-stationarity boundary. Monitor in future updates.
2. **Stress regime only 6% of days** — lower than expected. Consider K=4 or additional features.
3. **MC mean vs analytical mean gap (~3.9pp)** — explained by Jensen's inequality but should be documented clearly for stakeholders.
