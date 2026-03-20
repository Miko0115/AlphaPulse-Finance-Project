# Week 3 — Visual Storytelling (Power BI)

## Overview

| # | ID | Type | Task | Hours |
|---|-----|------|------|-------|
| 1 | 3.1 | Core | Import all CSV exports into Power BI | 2h |
| 2 | 3.3 | Core | Create correlation heatmap | 3h |
| 3 | 3.4 | Core | Build Monte Carlo distribution histogram | 3h |
| 4 | 3.5 | Core | Build rolling volatility time-series chart | 2h |
| 5 | 3.2 | Core | Build What-If scenario parameters | 5h |
| 6 | 3.6 | Core | Assemble full dashboard with KPI cards | 4h |
| 7 | 3.A3 | Bonus | Regime timeline visualization | 2h |
| 8 | 3.A4 | Bonus | GARCH vs Rolling vol comparison chart | 2h |

**Total: 23 hours**

---

## Prerequisites

Before starting, ensure the following files exist in `data/`:

```
data/
├── correlation_matrix.csv
├── monte_carlo_results.csv
├── rolling_volatility_annualized.csv
├── summary_stats.csv
├── var_summary.csv
├── garch_conditional_vol.csv
├── garch_mc_results.csv
├── regime_mc_results.csv
└── regime_labels.csv          ← IF MISSING: re-run src/regime_detection.py
```

**IMPORTANT:** `regime_labels.csv` may be missing. Re-run `regime_detection.py` to generate it.

### Data Prep Script (Run Once)

Some CSVs need reshaping for Power BI. Run this script BEFORE importing into Power BI:

**Create and run: `src/data_prep_powerbi.py`**

```python
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
```

---

## Task 3.1 — Import CSVs into Power BI

### Files to Import

| Power BI Data Source | CSV File | Purpose |
|---------------------|----------|---------|
| Correlation Heatmap | `data/pbi_correlation_heatmap.csv` | Heatmap (3.3) |
| MC Combined | `data/pbi_mc_combined.csv` | Histogram (3.4) |
| Rolling Volatility | `data/pbi_rolling_vol.csv` | Time-series (3.5) |
| Summary Stats | `data/summary_stats.csv` | KPI cards (3.6) |
| VaR Summary | `data/var_summary.csv` | KPI cards (3.6) |
| Vol Comparison | `data/pbi_vol_comparison.csv` | GARCH vs Rolling (3.A4) |
| Regime Timeline | `data/pbi_regime_timeline.csv` | Regime scatter (3.A3) |

### Steps

1. Open **Power BI Desktop** → Home → Get Data → Text/CSV
2. Import each CSV file listed above
3. For each import, verify in **Power Query Editor**:
   - `Date` columns are type **Date** (not Text)
   - Numeric columns are type **Decimal Number**
   - Text columns (Ticker, MC_Type, regime_label) are type **Text**
4. Click **Close & Apply**

### Data Type Checklist

| CSV | Column | Expected Type |
|-----|--------|--------------|
| pbi_correlation_heatmap | Ticker1, Ticker2 | Text |
| pbi_correlation_heatmap | Correlation | Decimal |
| pbi_mc_combined | Pct_Return | Decimal |
| pbi_mc_combined | MC_Type | Text |
| pbi_rolling_vol | Date | Date |
| pbi_rolling_vol | Ticker | Text |
| pbi_rolling_vol | Volatility | Decimal |
| summary_stats | all numeric cols | Decimal |
| var_summary | Metric | Text |
| var_summary | Value | Decimal |

---

## Task 3.3 — Correlation Heatmap

### Data Source: `pbi_correlation_heatmap.csv`

### Option A: Matrix Visual (Simple)

1. Add a **Matrix** visual to the canvas
2. Configuration:
   - **Rows:** Ticker1
   - **Columns:** Ticker2
   - **Values:** Correlation (set to "Don't summarize" or "Average")
3. Format:
   - Enable **Conditional formatting** on the Values field:
     - Background color → Rules or Gradient:
       - Minimum (0.15) → Light blue
       - Maximum (1.0) → Dark red
     - Or use a diverging scale: Blue (low) → White (mid ~0.4) → Red (high)
   - Turn off row/column totals
   - Set font size to 10-11pt

### Option B: Python Visual (Better Looking)

1. Add a **Python visual** to the canvas
2. Drag `Ticker1`, `Ticker2`, `Correlation` into the Values field
3. In the Python script editor, paste:

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Pivot back to matrix format for seaborn
corr_matrix = dataset.pivot(index='Ticker1', columns='Ticker2', values='Correlation')

# Create heatmap
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(
    corr_matrix,
    annot=True,                    # show numbers in each cell
    fmt='.2f',                     # 2 decimal places
    cmap='RdYlBu_r',              # red (high) to blue (low)
    vmin=0, vmax=1,                # correlation range
    square=True,                   # square cells
    linewidths=0.5,                # cell borders
    cbar_kws={'label': 'Correlation'},
    ax=ax
)
ax.set_title('Portfolio Correlation Matrix', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()
```

### What the interviewer should see:
- AAPL-AMZN: highest correlation (~0.56) — both tech-adjacent
- XOM-AMZN: lowest (~0.18) — best diversifier pair
- Diagonal: all 1.00

---

## Task 3.4 — Monte Carlo Distribution Histogram

### Data Source: `pbi_mc_combined.csv`

### Building the Histogram

1. Add a **Clustered Bar Chart** or **Histogram** visual
   - If using the built-in histogram: drag `Pct_Return` to Values
   - If using a bar chart: you may need to create bins first

### Creating Bins (if needed)

1. In the Fields pane, right-click `Pct_Return` → **New Group**
2. Set bin size to **5** (each bar covers a 5% return range)
3. Use the binned field as the X-axis

### Configuration

- **X-axis:** Pct_Return (bins)
- **Y-axis:** Count of Pct_Return
- **Legend:** MC_Type (this overlays all three MC types)

### Formatting

- Title: "Monte Carlo Return Distribution (10,000 Simulations)"
- Colors:
  - Basic MC: Blue
  - GARCH MC: Orange
  - Regime MC: Green
- Set transparency to ~40% so overlapping bars are visible
- Add reference lines for VaR:
  - VaR 95% = -14.20% → Red dashed line
  - VaR 99% = -24.27% → Dark red dashed line

### Adding VaR Reference Lines

1. Click the chart → Format → Analytics pane (magnifying glass icon)
2. Add **Constant Line**:
   - Value: -14.20
   - Label: "VaR 95%"
   - Color: Red, Style: Dashed
3. Add another Constant Line:
   - Value: -24.27
   - Label: "VaR 99%"
   - Color: Dark Red, Style: Dashed

### What the interviewer should see:
- Bell-shaped distribution centered around +15-20%
- Long left tail (negative returns) — "fat tail" risk
- VaR lines clearly marking the danger zone
- Three overlapping distributions showing how different MC methods compare

---

## Task 3.5 — Rolling Volatility Time-Series Chart

### Data Source: `pbi_rolling_vol.csv`

### Building the Chart

1. Add a **Line Chart** visual
2. Configuration:
   - **X-axis:** Date
   - **Y-axis:** Volatility
   - **Legend:** Ticker
3. Format:
   - Title: "30-Day Rolling Volatility (Annualized)"
   - Y-axis label: "Annualized Volatility"
   - Line thickness: 2px
   - Colors: Use distinct colors per ticker

### Suggested Colors

| Ticker | Color | Hex |
|--------|-------|-----|
| AAPL | Blue | #0071C5 |
| UNH | Green | #00A651 |
| JPM | Orange | #FF6600 |
| XOM | Red | #CC0000 |
| AMZN | Purple | #7B2D8E |

### Adding Event Annotations

Add **Constant Lines** on the X-axis to mark key events:
1. March 2020 → Label: "COVID Crash"
2. Jan 2022 → Label: "Rate Hikes Begin"
3. Aug 2015 → Label: "China Devaluation"

To add X-axis constant lines:
- Format → Analytics → Constant Line → Date value

### What the interviewer should see:
- Volatility spikes during COVID (March 2020) — all stocks surge to 60-120%
- XOM spike during 2015 oil crash
- Calm period in 2017 (all stocks ~10-15%)
- Clear visual proof that volatility clusters (high vol follows high vol)

---

## Task 3.2 — What-If Scenario Parameters

### What are What-If parameters?

Power BI's built-in feature that lets users **slide a value** and see the dashboard update in real-time. Perfect for risk analysis.

### Parameters to Create

#### Parameter 1: Portfolio Investment Amount

1. Modeling tab → **New Parameter** → What-If
2. Settings:
   - Name: `Investment_Amount`
   - Data type: Whole number
   - Minimum: 10000
   - Maximum: 1000000
   - Increment: 10000
   - Default: 100000

#### Parameter 2: Confidence Level

1. Modeling tab → New Parameter → What-If
2. Settings:
   - Name: `Confidence_Level`
   - Data type: Decimal number
   - Minimum: 0.90
   - Maximum: 0.99
   - Increment: 0.01
   - Default: 0.95

#### Parameter 3: Simulation Time Horizon (Days)

1. Modeling tab → New Parameter → What-If
2. Settings:
   - Name: `Time_Horizon`
   - Data type: Whole number
   - Minimum: 21 (1 month)
   - Maximum: 504 (2 years)
   - Increment: 21
   - Default: 252

### DAX Measures to Create

After creating the parameters, create these measures that USE the parameters:

```
VaR_Dollar_Loss =
VAR VaR_Pct = PERCENTILE.INC('pbi_mc_combined'[Pct_Return], 1 - [Confidence_Level Value])
RETURN
    [Investment_Amount Value] * ABS(VaR_Pct) / 100
```

```
CVaR_Dollar_Loss =
VAR VaR_Pct = PERCENTILE.INC('pbi_mc_combined'[Pct_Return], 1 - [Confidence_Level Value])
RETURN
    [Investment_Amount Value] *
    ABS(AVERAGEX(
        FILTER('pbi_mc_combined', 'pbi_mc_combined'[Pct_Return] <= VaR_Pct),
        'pbi_mc_combined'[Pct_Return]
    )) / 100
```

```
Expected_Return_Dollar =
    [Investment_Amount Value] * AVERAGE('pbi_mc_combined'[Pct_Return]) / 100
```

### Connecting Parameters to Visuals

1. Place the **parameter sliders** at the top of the dashboard
2. Use the DAX measures above in **Card visuals** to show:
   - "Max Expected Loss (VaR): $XX,XXX"
   - "Avg Loss in Worst Scenarios (CVaR): $XX,XXX"
   - "Expected Return: $XX,XXX"
3. When the user moves the slider, all cards update automatically

---

## Task 3.6 — Assemble Full Dashboard with KPI Cards

### Dashboard Layout (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│  ALPHAPULSE PORTFOLIO RISK MONITOR                          │
│  Investment: [____slider____]  Confidence: [____slider____] │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  KPI: Return │  KPI: Vol    │  KPI: VaR    │  KPI: Sharpe   │
│  +17.93%     │  20.13%      │  -$14,196    │  0.6795        │
├──────────────┴──────────────┴──────────────┴────────────────┤
│                                                             │
│  [Rolling Volatility Time-Series Chart]         [Correlation│
│  (full width or 2/3 width)                       Heatmap]   │
│                                                             │
├─────────────────────────────────┬───────────────────────────┤
│                                 │                           │
│  [Monte Carlo Histogram]        │  [Regime Timeline]        │
│  with VaR lines                 │  Color-coded scatter      │
│                                 │                           │
├─────────────────────────────────┴───────────────────────────┤
│  [GARCH vs Rolling Vol Comparison]                          │
└─────────────────────────────────────────────────────────────┘
```

### KPI Cards

Create 4-6 **Card** visuals across the top:

| KPI | Data Source | Value | Format |
|-----|-----------|-------|--------|
| Portfolio Return | summary_stats.csv | 17.93% | Percentage, green |
| Portfolio Volatility | summary_stats.csv | 20.13% | Percentage, amber |
| VaR 95% (Dollar) | DAX measure | $14,196 | Currency, red |
| Sharpe Ratio | summary_stats.csv | 0.6795 | 2 decimal places |
| CVaR 95% (Dollar) | DAX measure | $20,416 | Currency, dark red |
| Current Regime | regime_labels.csv | "Calm" | Text, conditional color |

### Creating KPI Cards

1. Add a **Card** visual
2. Drag the appropriate measure/field into the Fields well
3. Format:
   - Font size: 24-28pt for the number
   - Label size: 10-12pt
   - Background: subtle color matching the KPI meaning
     - Green: positive metrics (return, Sharpe)
     - Red: risk metrics (VaR, CVaR)
     - Blue: neutral metrics (volatility)

### For Summary Stats (non-DAX cards):

Since `summary_stats.csv` is in row format, you may need to filter to the "Portfolio" row:

1. Import `summary_stats.csv`
2. Add a **Card** visual
3. Add filter: first column = "Portfolio"
4. Drag "Annual Return" to the card

### Dashboard Theme & Formatting

- **Background:** Dark theme (#1E1E1E) or light (#F5F5F5) — pick one
- **Title bar:** Bold, large font, professional — "AlphaPulse Portfolio Risk Monitor"
- **Consistent fonts:** Segoe UI (Power BI default) throughout
- **Number formatting:**
  - Percentages: 2 decimal places
  - Dollars: comma-separated, no decimals ($14,196)
  - Ratios: 4 decimal places (0.6795)

---

## Task 3.A3 — Regime Timeline Visualization (Bonus)

### Data Source: `pbi_regime_timeline.csv`

### Building the Chart

1. Add a **Scatter Chart** visual
2. Configuration:
   - **X-axis:** Date
   - **Y-axis:** Portfolio_Return
   - **Legend (color):** regime_label
3. Colors:
   - Calm: Green (#00A651)
   - Stress: Orange (#FF9900)
   - Crisis: Red (#CC0000)
4. Format:
   - Title: "Market Regime Timeline (K-Means Classification)"
   - Marker size: 4-5px (small dots)
   - Turn off connecting lines

### Alternative: Colored Band Chart

For a cleaner look, use a **ribbon/area chart** approach:

1. Add a **Stacked Area Chart**
2. X-axis: Date
3. Y-axis: a constant value of 1
4. Legend: regime_label
5. This creates colored bands showing regime periods

### What the interviewer should see:
- Green (Calm) dominates ~83% of the timeline
- Red (Crisis) clusters around COVID (Mar-May 2020), 2022 rate hikes, and 2015-16 oil crash
- Orange (Stress) appears during slow grinding selloffs
- Clear visual that crisis is rare but impactful

---

## Task 3.A4 — GARCH vs Rolling Volatility Comparison (Bonus)

### Data Source: `pbi_vol_comparison.csv`

### Building the Chart

1. Add a **Line Chart** visual
2. Configuration:
   - **X-axis:** Date
   - **Y-axis:** Vol_Value
   - **Legend:** Vol_Type (Rolling 30-day vs GARCH)
3. Add a **Slicer** visual for Ticker:
   - Drag `Ticker` to a slicer
   - Set to **Dropdown** or **Buttons** style
   - User can select one ticker at a time to compare its rolling vs GARCH vol
4. Format:
   - Title: "Volatility Comparison: GARCH vs 30-Day Rolling"
   - Rolling line: Solid, Blue
   - GARCH line: Dashed, Orange
   - Line thickness: 2px

### What the interviewer should see:
- GARCH reacts faster to shocks (spikes earlier)
- Rolling vol is smoother but lags behind
- During COVID: GARCH spikes first, rolling vol catches up ~2 weeks later
- GARCH is the "early warning system"

---

## Final Checklist

Before submitting/presenting, verify:

- [ ] All 6 core visuals are on the dashboard
- [ ] KPI cards show correct numbers matching your Python outputs
- [ ] What-If sliders work and update VaR/CVaR cards
- [ ] Correlation heatmap shows values and color gradient
- [ ] MC histogram shows VaR reference lines
- [ ] Rolling vol chart has event annotations (COVID, rate hikes)
- [ ] Regime timeline shows correct color coding
- [ ] GARCH vs Rolling comparison has ticker slicer
- [ ] Dashboard has a professional title and consistent formatting
- [ ] All axes are labeled
- [ ] All charts have titles
- [ ] Number formatting is consistent (2 decimals for %, commas for $)

## Interview Talking Points for the Dashboard

1. **"Why Power BI?"** — "It's the industry standard for enterprise analytics. The built-in What-If parameters let stakeholders explore scenarios without touching Python."

2. **"Walk me through the dashboard."** — Start with KPIs (top), then rolling vol (the story of risk over time), then MC histogram (the distribution of outcomes), then heatmap (why diversification works).

3. **"What's the most interesting insight?"** — "The regime-aware analysis shows that our VaR drops from -14.2% to -6.3% in calm markets. Risk isn't static — it depends on the current market state."

4. **"How would you improve this?"** — "I'd add real-time data feeds, implement a Markov chain for regime transition probabilities, and add sector-level drill-down."
