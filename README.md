# AlphaPulse: Portfolio Risk & Volatility Monitor

A quantitative risk analysis system that measures, forecasts, and visualizes portfolio risk across market regimes using Monte Carlo simulation, GARCH volatility modeling, and K-Means regime detection.

## Portfolio

| Ticker | Company            | Sector                 | Weight |
| ------ | ------------------ | ---------------------- | ------ |
| AAPL   | Apple              | Technology             | 20%    |
| UNH    | UnitedHealth Group | Healthcare             | 20%    |
| JPM    | JPMorgan Chase     | Financials             | 20%    |
| XOM    | ExxonMobil         | Energy                 | 20%    |
| AMZN   | Amazon             | Consumer Discretionary | 20%    |

**Data period:** Jan 2015 – Dec 2024 (2,516 trading days)

## Key Results

| Metric                  | Value               |
| ----------------------- | ------------------- |
| Portfolio Annual Return | 17.93%              |
| Portfolio Volatility    | 20.13%              |
| Sharpe Ratio            | 0.6795              |
| VaR 95% (Baseline MC)   | -14.20%             |
| CVaR 95%                | -20.42%             |
| Diversification Benefit | 29.3% vol reduction |

Three Monte Carlo variants provide a spectrum of risk estimates:

- **Baseline MC** — static covariance, VaR 95% = -14.20%
- **GARCH MC** — time-varying volatility, VaR 95% = -12.97%
- **Regime MC (Calm)** — regime-specific covariance, VaR 95% = -6.28%

K-Means regime detection correctly identified all 7 major market events (2015 oil crash, COVID, 2022 rate hikes, SVB crisis, etc.)

## Project Structure

```
AlphaPulse-Finance Project/
├── src/                              # Python analysis scripts (7)
│   ├── data_fetcher.py               # Fetch & validate OHLCV data
│   ├── returns_analysis.py           # Log returns, covariance, Sharpe
│   ├── monte_carlo.py                # Baseline MC + VaR/CVaR
│   ├── garch_model.py                # GARCH(1,1) volatility forecasting
│   ├── garch_monte_carlo.py          # GARCH-enhanced MC simulation
│   ├── regime_detection.py           # K-Means regimes + regime-aware MC
│   └── data_prep_powerbi.py          # Reshape CSVs for Power BI
├── data/                             # Generated CSVs (not in git)
├── docs/                             # Reports & documentation
│   ├── AlphaPulse_Project_Report.md  # 5-page project report
│   ├── Methodology.md               # Full methodology & assumptions
│   ├── SME_Validation.md            # 30-point validation report
│   ├── AlphaPulse PowerBI Report.pbix  # Power BI dashboard
│   └── AlphaPulse PowerBI Report.pdf   # Dashboard PDF export
├── requirements.txt
└── README.md
```

## Setup & Execution

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run the pipeline (in order)

```bash
cd src/
python data_fetcher.py           # 1. Fetch 10 years of stock data
python returns_analysis.py       # 2. Compute returns, covariance, Sharpe
python monte_carlo.py            # 3. Run baseline MC + VaR/CVaR
python garch_model.py            # 4. Fit GARCH(1,1) models
python garch_monte_carlo.py      # 5. Run GARCH-enhanced MC
python regime_detection.py       # 6. K-Means regimes + regime MC
python data_prep_powerbi.py      # 7. Reshape data for Power BI
```

All scripts use `random_seed=42` for full reproducibility.

### Power BI Dashboard

Open `docs/AlphaPulse PowerBI Report.pbix` in Power BI Desktop. The dashboard has 3 pages:

1. **Portfolio Risk Monitor** — KPIs, MC histogram, correlation heatmap, What-If sliders
2. **Detailed Analytics** — Rolling volatility, GARCH comparison, regime timeline
3. **Executive Summary** — 4 KPIs + key insight for stakeholders

## Technical Stack

| Component        | Technology            |
| ---------------- | --------------------- |
| Data fetching    | Python, yfinance      |
| Analysis         | NumPy, pandas         |
| GARCH modeling   | arch                  |
| Regime detection | scikit-learn (KMeans) |
| Visualization    | Power BI Desktop      |
| Version control  | Git                   |

## Documentation

- **[Project Report](docs/AlphaPulse_Project_Report.md)** — 5-page project report with full analysis and findings
- **[Methodology](docs/Methodology.md)** — Full methodology with all assumptions, formulas, and limitations
- **[SME Validation](docs/SME_Validation.md)** — 30-point validation report checking all outputs against benchmarks
