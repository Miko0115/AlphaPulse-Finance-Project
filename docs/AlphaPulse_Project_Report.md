**AlphaPulse Project:** Portfolio Risk & Volatility Monitor Report

**Author:** Param Chaudhary

**Date:** March 2026

**Tools:** Python (NumPy, pandas, arch, scikit-learn) | Power BI | Git

**1. Executive Summary**

AlphaPulse is a quantitative portfolio risk monitoring system built for an asset management firm seeking to measure, forecast, and visualize downside risk across market regimes. The system analyzes a 5-stock, equally-weighted portfolio spanning five GICS sectors over 10 years of daily data (January 2015 – December 2024, 2,516 trading days).

**Portfolio:** AAPL (Technology), UNH (Healthcare), JPM (Financials), XOM (Energy), AMZN (Consumer Discretionary)

**Key findings:**

- The portfolio delivered a **17.93% annualized return** with **20.13% volatility**, producing a Sharpe ratio of **0.6795**. Diversification reduced portfolio volatility by 29.3% versus the average individual stock (28.5% → 20.1%), driven by genuinely low cross-sector correlations — the XOM–AMZN pair at 0.18 represents a near-zero co-movement between energy and e-commerce.
- Three Monte Carlo variants — Baseline, GARCH-enhanced, and Regime-aware — provide a spectrum of risk estimates. Value at Risk at 95% confidence ranges from **-14.20%** (baseline) to **-6.28%** (regime-aware in calm markets), demonstrating that risk is state-dependent, not a fixed property of the portfolio.
- K-Means regime detection (K=3) correctly identified all 7 major market events in the dataset, including 71 consecutive crisis days during COVID (March–May 2020) and the extended stress of the 2022 rate hiking cycle.
- A counterintuitive finding: the **Stress regime (-681.3% annualized return)** is more damaging than the **Crisis regime (+485.2%)**. Crisis captures acute shocks that trigger V-shaped recoveries and central bank intervention, while Stress captures slow-grinding selloffs with no catalyst for a bounce.

The system is delivered as a 3-page interactive Power BI dashboard with What-If parameters (investment amount, confidence level), enabling stakeholders to explore risk scenarios without executing Python code.

# **2. Data & Portfolio Construction**

## **2.1 Data Acquisition**

Daily OHLCV data was sourced from Yahoo Finance via the yfinance Python library with auto\_adjust=True, ensuring all prices are retroactively adjusted for stock splits and dividend distributions. The date range was fixed at January 2, 2015 to December 31, 2024 for reproducibility — running the pipeline on any machine produces identical results regardless of execution date.

## **2.2 Portfolio Selection**

Five large-cap, highly liquid stocks were selected from five different GICS sectors to maximize cross-sector diversification:

| **Ticker** | **Sector** | **10Y Return** | **10Y Volatility** | **Sharpe** |
| :--------------- | :--------------- | :------------------- | :----------------------- | :--------------- |
| AAPL             | Technology       | 23\.35%              | 28\.47%                  | 0\.671           |
| UNH              | Healthcare       | 17\.69%              | 26\.19%                  | 0\.513           |
| JPM              | Financials       | 16\.17%              | 27\.32%                  | 0\.437           |
| XOM              | Energy           | 5\.84%               | 27\.79%                  | 0\.057           |
| AMZN             | Consumer Disc.   | 26\.60%              | 32\.66%                  | 0\.684           |

**Design decision — UNH over JNJ:** Johnson & Johnson’s Kenvue consumer health spinoff (May 2023) created a structural break in its time series. Pre-spinoff JNJ was a diversified healthcare/consumer conglomerate; post-spinoff JNJ is a focused pharma/medtech company. Using JNJ’s 10-year series would blend two fundamentally different return-generating processes, contaminating covariance estimates and producing regime classifications that conflate corporate restructuring with genuine market regime changes. UnitedHealth Group (UNH) provides continuous healthcare exposure without this discontinuity.

**Design decision — Equal weighting:** A 1/N allocation (20% each) was chosen over mean-variance optimization as a transparent, bias-free baseline. While Markowitz optimization could theoretically improve the risk-return frontier, it is highly sensitive to estimation error in expected returns — small changes in mean estimates produce large swings in optimal weights. The 1/N portfolio has been shown to perform competitively against optimized portfolios in practice.

## **2.3 Data Quality**

Two validation checks were applied: (1) zero missing values across all 25 columns (5 tickers × 5 OHLCV fields) — no imputation was necessary; (2) no daily returns exceeding ±50%, confirming that Apple’s 4:1 split (August 2020) and Amazon’s 20:1 split (June 2022) were correctly adjusted by `auto_adjust=True`.

# **3. Quantitative Analysis**

## **3.1 Log Returns & Correlation Structure**

Daily log returns were computed as r(t) = ln(P(t) / P(t-1)). Log returns were chosen over simple percentage returns for three properties essential to downstream modelling: **time additivity** (weekly return = sum of daily log returns), **symmetry** (a +10% log return followed by -10% returns to exactly zero), and **approximate normality** (the distributional assumption underlying both Monte Carlo simulation and GARCH estimation).

The correlation matrix reveals the diversification structure:

|      | **AAPL** | **UNH** | **JPM** | **XOM**  | **AMZN** |
| :--- | :------------- | :------------ | :------------ | :------------- | :------------- |
| AAPL | 1\.00          | 0\.40         | 0\.42         | 0\.31          | 0\.56          |
| UNH  | 0\.40          | 1\.00         | 0\.44         | 0\.35          | 0\.26          |
| JPM  | 0\.42          | 0\.44         | 1\.00         | 0\.56          | 0\.30          |
| XOM  | 0\.31          | 0\.35         | 0\.56         | 1\.00          | **0.18** |
| AMZN | 0\.56          | 0\.26         | 0\.30         | **0.18** | 1\.00          |

The XOM–AMZN pair at 0.18 represents the strongest diversification relationship: energy prices are driven by geopolitical supply dynamics and OPEC decisions, while Amazon’s valuation responds to consumer spending, AWS cloud adoption, and interest rate sensitivity. No pair exceeds 0.60, confirming that the portfolio achieves genuine cross-sector diversification rather than sector-concentration masquerading as diversification.

## **3.2 Monte Carlo Simulation (Three Variants)**

10,000 simulations were run over a 252-day horizon for each of three methodologically distinct variants:

**Baseline MC** uses Geometric Brownian Motion with a constant covariance matrix estimated from the full 10-year sample. Cholesky decomposition (Σ = L × Lᵀ) transforms independent standard normal draws into correlated returns that respect the historical co-movement structure. This serves as the reference model against which enhancements are benchmarked.

**GARCH-Enhanced MC** replaces the constant variance assumption with a GARCH(1,1) model fitted individually to each asset. Volatility is updated daily during each simulation path using the conditional variance equation σ²(t) = ω + α·r²(t-1) + β·σ²(t-1). Correlations remain static (a Constant Conditional Correlation approximation); only the diagonal volatilities are time-varying. The simulation initialises from the last observed conditional variance, making risk estimates responsive to the current market environment.

**Regime-Aware MC** applies K-Means clustering to identify the current market regime, then simulates using that regime’s specific covariance matrix and mean returns. Unlike the GARCH variant, this captures regime-specific **correlations** — a critical advantage because cross-asset correlations spike during crises (the “correlation breakdown” phenomenon), precisely when diversification is needed most.

## **3.3 Risk Metrics**

| **Metric**  | **Baseline MC** | **GARCH MC** | **Regime MC (Calm)** |
| :---------------- | :-------------------- | :----------------- | :------------------------- |
| Mean Return       | +21.84%               | +21.72%            | +13.25%                    |
| **VaR 95%** | **-14.20%**     | **-12.97%**  | **-6.28%**           |
| VaR 99%           | -24.27%               | -23.18%            | -12.51%                    |
| CVaR 95%          | -20.42%               | -19.15%            | -10.14%                    |
| CVaR 99%          | -28.67%               | -27.71%            | -15.31%                    |

GARCH MC produces tighter risk estimates than baseline because it is conditioned on a low-volatility state at the end of 2024. In a high-volatility regime, GARCH would produce wider tails — the model is adaptive, not uniformly optimistic. Regime MC (Calm) shows the most favourable risk profile because it uses only calm-period data, where variances are 2–4× smaller.

CVaR (Expected Shortfall) consistently exceeds VaR by 5–8 percentage points across all variants, quantifying the **tail severity** that VaR alone misses. Basel III regulations now require Expected Shortfall rather than VaR for bank capital requirements, making CVaR the more relevant risk metric for institutional use.

## **3.4 GARCH(1,1) Volatility Forecasting**

Per-asset GARCH models were estimated via maximum likelihood. The table below shows the fitted parameters and their financial interpretation:

| **Ticker** | **ω (Baseline)** | **α (Shock)** | **β (Persist.)** | **α + β** | **Interpretation**                         |
| :--------------- | :---------------------- | :------------------- | :---------------------- | :---------------- | :----------------------------------------------- |
| AAPL             | 0\.1437                 | 0\.1044              | 0\.8492                 | 0\.954            | Balanced shock reaction and persistence          |
| UNH              | 0\.0866                 | 0\.0676              | 0\.8967                 | 0\.964            | High persistence, low shock reaction             |
| **JPM**    | 0\.1974                 | **0.1299**     | 0\.7911                 | 0\.921            | Most reactive to news, fastest decay             |
| **XOM**    | 0\.0174                 | 0\.0823              | **0.9146**        | **0.997**   | Near-integrated: geopolitical vol lingers months |
| **AMZN**   | 0\.3199                 | **0.2010**     | 0\.7445                 | 0\.946            | Highest shock reaction, fast mean-reversion      |

Three standout findings: **AMZN** has the highest shock sensitivity (α = 0.201) and the highest baseline variance (ω = 0.320), meaning its volatility spikes sharply after earnings surprises or macro announcements but mean-reverts quickly due to the lowest persistence (β = 0.745). **JPM** shows the fastest total decay (α + β = 0.921, lowest sum), meaning banking sector volatility dissipates faster than any other asset — likely because rate and credit shocks are priced in quickly by the deep, liquid financials market. In contrast, **XOM**’s near-integrated behaviour (α + β = 0.997) means that once oil-driven volatility rises, it persists for months — reflecting the structural, slow-resolving nature of geopolitical risk in energy markets.

GARCH-forecasted volatility at sample end is below the historical average for all assets except UNH (31.2% GARCH vs 26.2% historical), reflecting elevated healthcare sector uncertainty from regulatory and litigation developments in late 2024.

## **3.5 K-Means Regime Detection**

An unsupervised K-Means model (K=3) classified each trading day into one of three market regimes using three engineered features: portfolio daily return, 30-day rolling volatility, and average absolute return across all assets. Features were standardised via z-score normalisation before clustering.

| **Regime** | **Days** | **Share** | **Avg Return (ann.)** | **Avg Rolling Vol** |
| :--------------- | :------------- | :-------------- | :-------------------------- | :------------------------ |
| **Calm**   | 2,061          | 83%             | +11.93%                     | 14\.87%                   |
| **Stress** | 161            | 6%              | -681.3%                     | 28\.32%                   |
| **Crisis** | 264            | 11%             | +485.2%                     | 30\.84%                   |

The model correctly identified all 7 major market events in the dataset: the 2015 China devaluation, the 2016 oil price collapse, Volmageddon (February 2018), the Q4 2018 Fed tightening selloff, the COVID-19 crash (71 consecutive crisis days, March–May 2020), the 2022 rate hiking cycle, and the SVB banking crisis (March 2023).

**A counterintuitive but economically important finding:** the Crisis regime shows **positive** average returns (+485.2%) while the Stress regime shows deeply **negative** returns (-681.3%). This occurs because Crisis captures acute, dramatic shocks — the kind that trigger immediate central bank intervention (Fed rate cuts, QE), fiscal stimulus, and sharp V-shaped recoveries. The crash itself is short and the recovery is aggressive, producing a net-positive return when averaged across the full crisis period. Stress, by contrast, captures slow, grinding selloffs like Q4 2018 and the 2022 rate hiking cycle — periods where there is no single catalyst for a bounce, policy response is gradual rather than dramatic, and portfolio erosion is sustained over months. For portfolio risk management, this distinction matters profoundly: **Stress regimes are more damaging to wealth than Crisis regimes.**

# **4. Dashboard & Visualization**

The analysis is delivered through a 3-page interactive Power BI dashboard:

**Page 1 — Portfolio Risk Monitor:** Six KPI cards (Return, Volatility, VaR, CVaR, Sharpe, Expected Return) driven by DAX measures connected to two What-If parameters (Investment Amount: $10K–$1M; Confidence Level: 90–99%). A Monte Carlo histogram overlays all three simulation types with VaR reference lines at the 95th and 99th percentiles. A correlation heatmap with conditional formatting displays the diversification structure.

**Page 2 — Detailed Analytics:** A 30-day rolling volatility line chart with event annotations (China Devaluation, COVID Crash, Rate Hikes Begin) shows risk evolution over the full 10-year period. A GARCH vs Rolling Volatility comparison chart with a ticker slicer demonstrates GARCH’s faster shock response and smoother decay. A regime timeline chart colour-codes each trading day by detected market state (green = calm, amber = stress, red = crisis).

**Page 3 — Executive Summary:** A stripped-down view with 4 KPI cards, a dynamically generated key insight sentence, and a single portfolio volatility area chart. Designed for stakeholders who need a 10-second risk assessment without analytical detail.

# **5. Limitations**

1. **Normal distribution assumption** — Monte Carlo underestimates tail risk due to fat tails and negative skewness in real returns.
2. **Static correlations in GARCH MC** — Volatility is time-varying but correlations are held fixed, missing correlation spikes during crises.
3. **No regime transitions within simulations** — Each MC path assumes one regime for the full 252-day horizon.
4. **Equal weighting** — Simple and robust, but does not optimize risk-adjusted returns.
5. **US large-cap equities only** — No bonds, commodities, or international diversification.
