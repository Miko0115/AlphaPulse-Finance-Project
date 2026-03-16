import { useState, useEffect } from "react";

const WEEKS = [
  {
    id: 1, title: "Data Acquisition & Cleaning", subtitle: "Building the foundation",
    color: "#2563eb", colorDim: "#1e40af",
    interviewQs: [
      "Why adjusted close prices instead of raw?",
      "Forward fill vs interpolation for financial data?",
      "70% single-day price drop — what do you investigate?",
      "What is survivorship bias in portfolio analysis?",
    ],
    core: [
      { id: "1.1", title: "Select diversified portfolio (5 tickers, 5 sectors)", deliverable: "Ticker list with sector justification", validation: "No two tickers share a sector", difficulty: "B", hours: 2, resources: [{ t: "yfinance docs", u: "https://pypi.org/project/yfinance/" }, { t: "MPT basics", u: "https://www.investopedia.com/terms/m/modernportfoliotheory.asp" }] },
      { id: "1.2", title: "Fetch 5-year OHLCV data via yfinance API", deliverable: "Raw DataFrame ~1260 rows x 5 tickers", validation: "Row count, date range, dtype check", difficulty: "B", hours: 3, resources: [{ t: "yfinance GitHub", u: "https://github.com/ranaroussi/yfinance" }] },
      { id: "1.3", title: "Handle missing data with forward fill", deliverable: "Clean DataFrame, zero NaN values", validation: "df.isnull().sum() == 0", difficulty: "B", hours: 2, resources: [{ t: "Pandas fillna", u: "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html" }] },
      { id: "1.4", title: "Validate for stock splits and corporate actions", deliverable: "Price validation charts (matplotlib PNG)", validation: "No anomalous 50%+ jumps", difficulty: "I", hours: 3, resources: [{ t: "Adjusted price explained", u: "https://www.investopedia.com/terms/a/adjusted_closing_price.asp" }] },
      { id: "1.5", title: "Export clean dataset as CSV + documentation", deliverable: "prices_clean.csv + data_dictionary.md", validation: "Data integrity report", difficulty: "B", hours: 1, resources: [] },
    ],
    addon: [
      { id: "1.A1", title: "Build reusable DataPipeline class with logging & retry", deliverable: "pipeline.py with logging, retry decorators, auto-quality report", validation: "Class can re-run end-to-end with one function call", difficulty: "A", hours: 4, resources: [{ t: "Python logging", u: "https://docs.python.org/3/library/logging.html" }] },
      { id: "1.A2", title: "Add automated data quality HTML report", deliverable: "data_quality_report.html with stats, charts, anomaly flags", validation: "Report auto-generates on every pipeline run", difficulty: "I", hours: 3, resources: [{ t: "Pandas Profiling", u: "https://github.com/ydataai/ydata-profiling" }] },
    ],
  },
  {
    id: 2, title: "Quantitative Analysis", subtitle: "The mathematical core",
    color: "#7c3aed", colorDim: "#5b21b6",
    interviewQs: [
      "Why log returns instead of simple returns? (3 reasons)",
      "What does the off-diagonal of a covariance matrix represent?",
      "Explain Cholesky decomposition in plain English",
      "VaR says 10% loss max, but portfolio lost 25% — what went wrong?",
      "What is the Sharpe Ratio? What does a negative Sharpe tell you?",
      "How would you validate a Monte Carlo simulation?",
      "Explain GARCH(1,1) — what do alpha and beta represent?",
      "Why use K-Means for regime detection instead of a threshold rule?",
    ],
    core: [
      { id: "2.1", title: "Calculate daily log returns for all tickers", deliverable: "log_returns DataFrame ~1259 x 5", validation: "Means near zero, no extreme outliers", difficulty: "I", hours: 2, resources: [{ t: "Log vs simple returns", u: "https://www.investopedia.com/terms/l/logreturns.asp" }] },
      { id: "2.2", title: "Build and annualize covariance matrix (x252)", deliverable: "5x5 annualized covariance matrix", validation: "Symmetric, positive semi-definite, diagonal > 0", difficulty: "I", hours: 3, resources: [{ t: "NumPy cov", u: "https://numpy.org/doc/stable/reference/generated/numpy.cov.html" }] },
      { id: "2.3", title: "Implement Cholesky decomposition for correlated draws", deliverable: "Lower triangular L verified: L @ L.T ≈ cov", validation: "np.allclose(L @ L.T, cov_daily) == True", difficulty: "A", hours: 4, resources: [{ t: "Cholesky", u: "https://numpy.org/doc/stable/reference/generated/numpy.linalg.cholesky.html" }] },
      { id: "2.4", title: "Run Monte Carlo simulation (10,000+ iterations)", deliverable: "Array of 10K final portfolio values", validation: "Histogram is roughly lognormal", difficulty: "A", hours: 6, resources: [{ t: "Monte Carlo for finance", u: "https://www.investopedia.com/terms/m/montecarlosimulation.asp" }] },
      { id: "2.5", title: "Calculate VaR at 95% and 99% confidence", deliverable: "VaR values + max expected loss figures", validation: "Sanity check vs historical max drawdown", difficulty: "I", hours: 2, resources: [{ t: "VaR explained", u: "https://www.investopedia.com/terms/v/var.asp" }] },
      { id: "2.6", title: "Compute 30-day rolling volatility (annualized)", deliverable: "rolling_volatility.csv + time-series plot", validation: "Spikes align with known events (COVID crash)", difficulty: "I", hours: 3, resources: [{ t: "Pandas rolling", u: "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html" }] },
      { id: "2.7", title: "Calculate Sharpe Ratio for the portfolio", deliverable: "Sharpe value + interpretation", validation: "Sharpe > 0 means beats risk-free rate", difficulty: "I", hours: 2, resources: [{ t: "Sharpe formula", u: "https://www.investopedia.com/terms/s/sharperatio.asp" }] },
      { id: "2.8", title: "Export all computed datasets as CSV", deliverable: "4 CSVs: returns, vol, MC results, correlation", validation: "No NaN in exports, column verification", difficulty: "B", hours: 1, resources: [] },
    ],
    addon: [
      { id: "2.A1", title: "Implement CVaR (Expected Shortfall) — the Basel III standard", deliverable: "CVaR values at 95% and 99% + comparison to VaR", validation: "CVaR is always worse (larger loss) than VaR", difficulty: "I", hours: 2, resources: [{ t: "CVaR explained", u: "https://www.investopedia.com/terms/c/conditional_value_at_risk.asp" }] },
      { id: "2.A2", title: "Plot the Efficient Frontier (optimal risk-return curve)", deliverable: "Scatter plot of 5000 random portfolios + efficient frontier line", validation: "Frontier forms upper-left boundary of the cloud", difficulty: "A", hours: 5, resources: [{ t: "Efficient Frontier tutorial", u: "https://www.investopedia.com/terms/e/efficientfrontier.asp" }] },
      { id: "2.A3", title: "Build stress test module (simulate 2008-style crash)", deliverable: "Stressed VaR with manually elevated correlations (all → 0.8)", validation: "Stressed VaR is significantly worse than normal VaR", difficulty: "A", hours: 4, resources: [{ t: "Stress testing", u: "https://www.investopedia.com/terms/s/stresstesting.asp" }] },
      { id: "2.A4", title: "GARCH(1,1) volatility forecasting per asset", deliverable: "GARCH-fitted models for all 5 tickers + 252-day vol forecast", validation: "alpha + beta close to 1.0 (persistence check), forecasted vol curve is smooth", difficulty: "A", hours: 5, resources: [{ t: "arch library docs", u: "https://arch.readthedocs.io/en/latest/" }, { t: "GARCH explained", u: "https://www.investopedia.com/terms/g/garch.asp" }] },
      { id: "2.A5", title: "Enhanced Monte Carlo with GARCH time-varying covariance", deliverable: "10K simulations using day-specific GARCH-forecasted vol + comparison to original VaR", validation: "GARCH VaR differs from static VaR (shows time-varying risk matters)", difficulty: "A", hours: 4, resources: [{ t: "GARCH for MC", u: "https://arch.readthedocs.io/en/latest/univariate/forecasting.html" }] },
      { id: "2.A6", title: "K-Means regime detection (calm / normal / crisis)", deliverable: "Regime labels for every trading day + 3 regime-specific cov matrices", validation: "Crisis regime shows ~10% of days with correlation spike to 0.6+", difficulty: "A", hours: 5, resources: [{ t: "sklearn KMeans", u: "https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html" }, { t: "Regime switching", u: "https://www.investopedia.com/terms/r/regime.asp" }] },
      { id: "2.A7", title: "Regime-aware Monte Carlo with current-state detection", deliverable: "Regime-aware VaR using current regime's cov matrix + comparison table", validation: "If current regime is Crisis, VaR should be worse than original", difficulty: "A", hours: 4, resources: [{ t: "Elbow method", u: "https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html" }] },
    ],
  },
  {
    id: 3, title: "Visual Storytelling", subtitle: "Tableau dashboard",
    color: "#059669", colorDim: "#047857",
    interviewQs: [
      "Design a dashboard for someone with 30 seconds to decide?",
      "Live connection vs extract in Tableau?",
      "How do Tableau parameters enable scenario analysis?",
      "Encode correlation visually for non-technical people?",
    ],
    core: [
      { id: "3.1", title: "Import all CSV exports into Tableau", deliverable: "4 connected data sources in workbook", validation: "Row counts match Python exports", difficulty: "B", hours: 2, resources: [{ t: "Tableau CSV guide", u: "https://help.tableau.com/current/pro/desktop/en-us/examples_text.htm" }] },
      { id: "3.2", title: "Build What-If scenario parameters", deliverable: "3 parameters: sector shock, weight adjuster, time horizon", validation: "Changes update all dependent charts", difficulty: "A", hours: 5, resources: [{ t: "Tableau parameters", u: "https://help.tableau.com/current/pro/desktop/en-us/parameters_create.htm" }] },
      { id: "3.3", title: "Create correlation heatmap visualization", deliverable: "5x5 matrix (blue = negative, red = positive)", validation: "Diagonal = 1.0, matrix is symmetric", difficulty: "I", hours: 3, resources: [] },
      { id: "3.4", title: "Build Monte Carlo distribution histogram", deliverable: "Histogram of 10K outcomes with VaR line overlay", validation: "VaR annotation at 5th percentile", difficulty: "I", hours: 3, resources: [] },
      { id: "3.5", title: "Build rolling volatility time-series chart", deliverable: "Multi-line chart per-asset 30-day rolling vol", validation: "COVID crash (Mar 2020) shows clear spike", difficulty: "I", hours: 2, resources: [] },
      { id: "3.6", title: "Assemble full dashboard with KPI cards", deliverable: "Published dashboard with visual hierarchy", validation: "Can answer 'is risk OK?' in 5 seconds", difficulty: "I", hours: 4, resources: [{ t: "Dashboard best practices", u: "https://help.tableau.com/current/pro/desktop/en-us/dashboards_best_practices.htm" }] },
    ],
    addon: [
      { id: "3.A1", title: "Build a Streamlit interactive web app alternative", deliverable: "Deployed Streamlit app with sliders, charts, and live recalculation", validation: "App runs locally and can be shared via Streamlit Cloud", difficulty: "A", hours: 8, resources: [{ t: "Streamlit docs", u: "https://docs.streamlit.io/" }] },
      { id: "3.A2", title: "Add animated Monte Carlo fan chart (Plotly)", deliverable: "Animated Plotly chart showing simulation paths spreading over time", validation: "Animation runs smoothly with 100+ visible paths", difficulty: "I", hours: 3, resources: [{ t: "Plotly animations", u: "https://plotly.com/python/animations/" }] },
      { id: "3.A3", title: "Regime timeline visualization (color-coded scatter)", deliverable: "Timeline chart with green/blue/red dots showing calm/normal/crisis periods", validation: "COVID crash (Mar 2020) is clearly red, 2021 bull run is green", difficulty: "I", hours: 2, resources: [{ t: "Matplotlib scatter", u: "https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html" }] },
      { id: "3.A4", title: "GARCH vs Rolling vol comparison chart", deliverable: "Overlay plot showing GARCH-forecasted vol vs 30-day rolling vol", validation: "GARCH line is smoother and leads the rolling line during transitions", difficulty: "I", hours: 2, resources: [] },
    ],
  },
  {
    id: 4, title: "Deployment & Documentation", subtitle: "Production handoff",
    color: "#d97706", colorDim: "#b45309",
    interviewQs: [
      "What assumptions does your model make? When do they break?",
      "Explain VaR to a non-technical executive in one sentence",
      "Why are historical correlations dangerous during a crisis?",
      "One improvement to this model — what and why?",
    ],
    core: [
      { id: "4.1", title: "Build executive summary dashboard (3-4 KPIs)", deliverable: "Single-page: VaR, Sharpe, Vol, Max Drawdown", validation: "Exec can answer 'is risk OK?' in 5 seconds", difficulty: "I", hours: 3, resources: [] },
      { id: "4.2", title: "Write methodology doc with all assumptions", deliverable: "2-page doc listing every model assumption", validation: "Each assumption paired with its limitation", difficulty: "I", hours: 4, resources: [] },
      { id: "4.3", title: "Conduct SME validation of model outputs", deliverable: "Validation checklist signed off by reviewer", validation: "VaR aligns with historical drawdown", difficulty: "I", hours: 3, resources: [] },
      { id: "4.4", title: "Clean and comment all Python scripts", deliverable: "Production-ready repo with README", validation: "Scripts run end-to-end from raw data to exports", difficulty: "B", hours: 3, resources: [{ t: "PEP 8", u: "https://peps.python.org/pep-0008/" }] },
      { id: "4.5", title: "Write 5-page project report", deliverable: "PDF: problem, architecture, findings, methodology", validation: "Covers all 4 sections, under page limit", difficulty: "I", hours: 4, resources: [] },
      { id: "4.6", title: "Package final submission", deliverable: "GitHub repo + Tableau link + PDF report", validation: "Full pipeline test: raw → dashboard in one run", difficulty: "B", hours: 2, resources: [] },
    ],
    addon: [
      { id: "4.A1", title: "Dockerize the entire pipeline", deliverable: "Dockerfile + docker-compose.yml that runs full pipeline", validation: "docker-compose up produces all outputs from scratch", difficulty: "A", hours: 5, resources: [{ t: "Docker for DS", u: "https://docs.docker.com/get-started/" }] },
      { id: "4.A2", title: "Backtest: compare model predictions vs actual outcomes", deliverable: "Backtest report showing predicted vs actual VaR breaches", validation: "VaR breach rate should be ~5% for a 95% model", difficulty: "A", hours: 4, resources: [{ t: "Backtesting VaR", u: "https://www.investopedia.com/terms/b/backtesting.asp" }] },
      { id: "4.A3", title: "Record a 5-minute project walkthrough video", deliverable: "MP4/YouTube link with screen recording + narration", validation: "Covers problem → approach → key finding → limitation in 5 min", difficulty: "I", hours: 3, resources: [{ t: "OBS Studio", u: "https://obsproject.com/" }] },
    ],
  },
];

const DIFF = { B: { l: "Beginner", c: "#10b981", bg: "#064e3b" }, I: { l: "Intermediate", c: "#f59e0b", bg: "#78350f" }, A: { l: "Advanced", c: "#ef4444", bg: "#7f1d1d" } };

export default function Tracker() {
  const [done, setDone] = useState({});
  const [week, setWeek] = useState(1);
  const [exp, setExp] = useState(null);
  const [showIQ, setShowIQ] = useState(false);
  const [tab, setTab] = useState("core");

  const W = WEEKS.find(w => w.id === week);
  const tasks = tab === "core" ? W.core : W.addon;
  const allTasks = WEEKS.flatMap(w => [...w.core, ...w.addon]);
  const coreTasks = WEEKS.flatMap(w => w.core);
  const addonTasks = WEEKS.flatMap(w => w.addon);
  const totalDone = allTasks.filter(t => done[t.id]).length;
  const coreDone = coreTasks.filter(t => done[t.id]).length;
  const addonDone = addonTasks.filter(t => done[t.id]).length;
  const wCore = W.core.filter(t => done[t.id]).length;
  const wAddon = W.addon.filter(t => done[t.id]).length;
  const wTotal = W.core.length + W.addon.length;
  const wDoneTotal = wCore + wAddon;
  const totalHrs = allTasks.reduce((s,t) => s+t.hours, 0);
  const hrsLeft = allTasks.filter(t => !done[t.id]).reduce((s,t) => s+t.hours, 0);

  const pct = allTasks.length ? Math.round(totalDone/allTasks.length*100) : 0;

  const S = {
    root: { fontFamily: "'Geist', 'SF Pro', -apple-system, sans-serif", background: "#09090b", minHeight: "100vh", color: "#fafafa" },
    header: { padding: "20px 16px 16px", borderBottom: "1px solid #1a1a1e" },
    brand: { fontSize: 10, fontWeight: 700, letterSpacing: "0.15em", textTransform: "uppercase", color: "#525252", marginBottom: 6 },
    h1: { fontSize: 22, fontWeight: 700, margin: "0 0 2px", letterSpacing: "-0.03em" },
    sub: { fontSize: 12, color: "#525252", margin: 0 },
    statGrid: { display: "grid", gridTemplateColumns: "repeat(4,minmax(0,1fr))", borderBottom: "1px solid #1a1a1e" },
    stat: { padding: "12px 14px", borderRight: "1px solid #1a1a1e" },
    statLabel: { fontSize: 10, color: "#525252", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 2 },
    statVal: { fontSize: 20, fontWeight: 700, fontFamily: "'Geist Mono', monospace", letterSpacing: "-0.02em" },
    statSub: { fontSize: 10, color: "#404040" },
    weekBar: { display: "flex", borderBottom: "1px solid #1a1a1e", overflow: "auto" },
    tabBar: { display: "flex", gap: 2, padding: "12px 16px 0", borderBottom: "1px solid #1a1a1e" },
    tab: (a) => ({ padding: "8px 16px", fontSize: 12, fontWeight: 600, border: "none", borderBottom: a ? `2px solid ${W.color}` : "2px solid transparent", background: "transparent", color: a ? "#fafafa" : "#525252", cursor: "pointer" }),
    card: (isDone) => ({ background: isDone ? "#0a1a0a" : "#111113", border: `1px solid ${isDone ? "#14532d" : "#1a1a1e"}`, borderRadius: 10, marginBottom: 6, overflow: "hidden", transition: "all 0.2s" }),
    check: (isDone) => ({ width: 20, height: 20, minWidth: 20, borderRadius: 5, border: `1.5px solid ${isDone ? "#22c55e" : "#333"}`, background: isDone ? "#22c55e" : "transparent", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", transition: "all 0.15s" }),
    diff: (d) => ({ fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 4, background: DIFF[d].bg, color: DIFF[d].c }),
    expandArea: { padding: "0 14px 14px 44px", borderTop: "1px solid #1a1a1e" },
    detailBlock: { marginBottom: 10 },
    detailLabel: { fontSize: 10, fontWeight: 600, color: "#525252", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 },
    detailVal: { fontSize: 12, color: "#a1a1a1", lineHeight: 1.5, background: "#0a0a0c", padding: "8px 10px", borderRadius: 6, border: "1px solid #1a1a1e" },
    validVal: { fontSize: 12, color: "#fbbf24", lineHeight: 1.5, background: "#1a1400", padding: "8px 10px", borderRadius: 6, border: "1px solid #332800" },
    resLink: { fontSize: 11, color: W.color, background: `${W.color}15`, padding: "4px 10px", borderRadius: 5, textDecoration: "none", border: `1px solid ${W.color}25`, display: "inline-block", marginRight: 6, marginBottom: 4 },
  };

  return (
    <div style={S.root}>
      <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;700&display=swap" rel="stylesheet" />

      {/* Header */}
      <div style={S.header}>
        <div style={S.brand}>AlphaPulse — Project 2</div>
        <h1 style={S.h1}>Portfolio Risk & Volatility Monitor</h1>
        <p style={S.sub}>Python → NumPy → Tableau &nbsp;|&nbsp; {coreTasks.length} core + {addonTasks.length} bonus tasks</p>
      </div>

      {/* Stats */}
      <div style={S.statGrid}>
        {[
          { l: "Progress", v: `${pct}%`, s: `${totalDone}/${allTasks.length}` },
          { l: "Core done", v: `${coreDone}/${coreTasks.length}`, s: `${Math.round(coreDone/coreTasks.length*100)}%` },
          { l: "Bonus done", v: `${addonDone}/${addonTasks.length}`, s: "recruiter edge" },
          { l: "Hours left", v: `${hrsLeft}h`, s: `of ${totalHrs}h total` },
        ].map((s,i) => (
          <div key={i} style={{...S.stat, ...(i===3?{borderRight:"none"}:{})}}>
            <div style={S.statLabel}>{s.l}</div>
            <div style={S.statVal}>{s.v}</div>
            <div style={S.statSub}>{s.s}</div>
          </div>
        ))}
      </div>

      {/* Progress bar */}
      <div style={{ height: 3, background: "#1a1a1e" }}>
        <div style={{ height: "100%", width: `${pct}%`, background: `linear-gradient(90deg, ${WEEKS[0].color}, ${WEEKS[3].color})`, transition: "width 0.5s ease" }} />
      </div>

      {/* Week tabs */}
      <div style={S.weekBar}>
        {WEEKS.map(w => {
          const a = week === w.id;
          const wd = w.core.filter(t=>done[t.id]).length + w.addon.filter(t=>done[t.id]).length;
          const wt = w.core.length + w.addon.length;
          return (
            <button key={w.id} onClick={() => { setWeek(w.id); setExp(null); setShowIQ(false); setTab("core"); }}
              style={{ flex: 1, minWidth: 80, padding: "12px 8px 10px", background: a ? "#111113" : "transparent", border: "none", borderBottom: a ? `2px solid ${w.color}` : "2px solid transparent", cursor: "pointer", textAlign: "left" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 4, marginBottom: 2 }}>
                <div style={{ width: 7, height: 7, borderRadius: "50%", background: wd===wt ? "#22c55e" : wd>0 ? w.color : "#333" }} />
                <span style={{ fontSize: 11, fontWeight: 600, color: a ? "#fafafa" : "#666" }}>W{w.id}</span>
              </div>
              <div style={{ fontSize: 10, color: "#444", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{w.title}</div>
              <div style={{ fontSize: 10, color: "#333", fontFamily: "'Geist Mono', monospace", marginTop: 1 }}>{wd}/{wt}</div>
            </button>
          );
        })}
      </div>

      {/* Content area */}
      <div style={{ padding: "14px 14px 80px" }}>
        {/* Week header */}
        <div style={{ background: `linear-gradient(135deg, ${W.color}12 0%, transparent 60%)`, borderRadius: 10, padding: "16px", marginBottom: 10, border: `1px solid ${W.color}20` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
            <div>
              <h2 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 2px" }}>Week {W.id}: {W.title}</h2>
              <p style={{ fontSize: 12, color: "#666", margin: 0 }}>{W.subtitle}</p>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              <div style={{ background: "#0a0a0c", borderRadius: 7, padding: "6px 12px", textAlign: "center" }}>
                <div style={{ fontSize: 16, fontWeight: 700, color: W.color, fontFamily: "'Geist Mono', monospace" }}>{W.core.filter(t=>!done[t.id]).reduce((s,t)=>s+t.hours,0) + W.addon.filter(t=>!done[t.id]).reduce((s,t)=>s+t.hours,0)}h</div>
                <div style={{ fontSize: 9, color: "#525252", textTransform: "uppercase" }}>left</div>
              </div>
              <div style={{ background: "#0a0a0c", borderRadius: 7, padding: "6px 12px", textAlign: "center" }}>
                <div style={{ fontSize: 16, fontWeight: 700, color: wDoneTotal===wTotal ? "#22c55e" : "#fafafa", fontFamily: "'Geist Mono', monospace" }}>{wTotal>0?Math.round(wDoneTotal/wTotal*100):0}%</div>
                <div style={{ fontSize: 9, color: "#525252", textTransform: "uppercase" }}>done</div>
              </div>
            </div>
          </div>
          <div style={{ marginTop: 10, height: 3, borderRadius: 2, background: "#1a1a1e" }}>
            <div style={{ height: "100%", borderRadius: 2, width: `${wTotal>0?Math.round(wDoneTotal/wTotal*100):0}%`, background: W.color, transition: "width 0.4s ease" }} />
          </div>
        </div>

        {/* Interview Qs toggle */}
        <button onClick={() => setShowIQ(!showIQ)}
          style={{ width: "100%", padding: "10px 14px", background: showIQ ? "#111113" : "#0a0a0c", border: "1px solid #1a1a1e", borderRadius: showIQ ? "8px 8px 0 0" : 8, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: showIQ ? 0 : 10 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ fontSize: 12 }}>&#127919;</span>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#e4e4e7" }}>Interview prep</span>
            <span style={{ fontSize: 10, color: "#525252", background: "#1a1a1e", padding: "1px 7px", borderRadius: 8, fontFamily: "'Geist Mono', monospace" }}>{W.interviewQs.length}</span>
          </div>
          <span style={{ fontSize: 10, color: "#525252", transform: showIQ ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}>&#9660;</span>
        </button>
        {showIQ && (
          <div style={{ background: "#0a0a0c", border: "1px solid #1a1a1e", borderTop: "none", borderRadius: "0 0 8px 8px", padding: "10px 14px", marginBottom: 10 }}>
            {W.interviewQs.map((q,i) => (
              <div key={i} style={{ display: "flex", gap: 8, padding: "8px 0", borderBottom: i<W.interviewQs.length-1 ? "1px solid #1a1a1e" : "none" }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: W.color, fontFamily: "'Geist Mono', monospace", minWidth: 22 }}>Q{i+1}</span>
                <span style={{ fontSize: 12, color: "#a1a1a1", lineHeight: 1.5 }}>{q}</span>
              </div>
            ))}
            <div style={{ marginTop: 8, padding: "6px 10px", background: `${W.color}10`, borderRadius: 6, border: `1px solid ${W.color}18` }}>
              <span style={{ fontSize: 11, color: W.color }}>&#9654; Full answers with interview tips are in the AlphaPulse Interview Prep document</span>
            </div>
          </div>
        )}

        {/* Core / Add-on tabs */}
        <div style={S.tabBar}>
          <button onClick={() => { setTab("core"); setExp(null); }} style={S.tab(tab==="core")}>
            Core tasks <span style={{ fontSize: 10, opacity: 0.6, marginLeft: 4 }}>{W.core.length}</span>
          </button>
          <button onClick={() => { setTab("addon"); setExp(null); }} style={S.tab(tab==="addon")}>
            Bonus tasks <span style={{ fontSize: 10, opacity: 0.6, marginLeft: 4, color: "#f59e0b" }}>+{W.addon.length}</span>
          </button>
        </div>

        {/* Addon banner */}
        {tab === "addon" && (
          <div style={{ margin: "10px 0", padding: "10px 14px", background: "#1a1400", borderRadius: 8, border: "1px solid #332800" }}>
            <span style={{ fontSize: 12, color: "#fbbf24", fontWeight: 600 }}>Recruiter edge tasks</span>
            <span style={{ fontSize: 11, color: "#a18207", marginLeft: 6 }}>— these are not required but will set your portfolio apart in interviews</span>
          </div>
        )}

        {/* Task cards */}
        <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 6 }}>
          {tasks.map((task) => {
            const isDone = done[task.id];
            const isExp = exp === task.id;
            const isAddon = task.id.includes("A");
            return (
              <div key={task.id} style={S.card(isDone)}>
                <div style={{ display: "flex", alignItems: "flex-start", gap: 8, padding: "12px 12px 10px", cursor: "pointer" }}
                  onClick={() => setExp(isExp ? null : task.id)}>
                  <button onClick={e => { e.stopPropagation(); setDone(p=>({...p,[task.id]:!p[task.id]})); }}
                    style={S.check(isDone)}>
                    {isDone && <span style={{ color: "#fff", fontSize: 12, fontWeight: 700 }}>&#10003;</span>}
                  </button>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap", marginBottom: 3 }}>
                      <span style={{ fontSize: 10, fontWeight: 700, color: "#444", fontFamily: "'Geist Mono', monospace" }}>{task.id}</span>
                      {isAddon && <span style={{ fontSize: 9, fontWeight: 700, padding: "1px 6px", borderRadius: 3, background: "#332800", color: "#fbbf24" }}>BONUS</span>}
                    </div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: isDone ? "#4ade80" : "#e4e4e7", textDecoration: isDone ? "line-through" : "none", textDecorationColor: "#166534", marginBottom: 4 }}>{task.title}</div>
                    <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap" }}>
                      <span style={S.diff(task.difficulty)}>{DIFF[task.difficulty].l}</span>
                      <span style={{ fontSize: 10, color: "#525252", fontFamily: "'Geist Mono', monospace" }}>~{task.hours}h</span>
                    </div>
                  </div>
                  <span style={{ fontSize: 10, color: "#333", transform: isExp ? "rotate(180deg)" : "none", transition: "transform 0.2s", padding: 4 }}>&#9660;</span>
                </div>

                {isExp && (
                  <div style={S.expandArea}>
                    <div style={{ paddingTop: 10 }}>
                      <div style={S.detailBlock}>
                        <div style={S.detailLabel}>Deliverable</div>
                        <div style={S.detailVal}>{task.deliverable}</div>
                      </div>
                      {task.validation && (
                        <div style={S.detailBlock}>
                          <div style={S.detailLabel}>Validation</div>
                          <div style={S.validVal}>{task.validation}</div>
                        </div>
                      )}
                      {task.resources.length > 0 && (
                        <div>
                          <div style={S.detailLabel}>Resources</div>
                          <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 4 }}>
                            {task.resources.map((r,i) => (
                              <a key={i} href={r.u} target="_blank" rel="noopener noreferrer" style={S.resLink}>{r.t} &#8599;</a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer legend */}
      <div style={{ position: "fixed", bottom: 0, left: 0, right: 0, padding: "10px 14px", borderTop: "1px solid #1a1a1e", background: "rgba(9,9,11,0.92)", backdropFilter: "blur(8px)", display: "flex", justifyContent: "center", gap: 14, flexWrap: "wrap", zIndex: 10 }}>
        {Object.entries(DIFF).map(([k,d]) => (
          <div key={k} style={{ display: "flex", alignItems: "center", gap: 3 }}>
            <div style={{ width: 7, height: 7, borderRadius: 2, background: d.c }} />
            <span style={{ fontSize: 10, color: "#525252" }}>{d.l}</span>
          </div>
        ))}
        <span style={{ fontSize: 10, color: "#262626" }}>|</span>
        <span style={{ fontSize: 10, color: "#525252" }}>{coreTasks.length} core + {addonTasks.length} bonus = {allTasks.length} total tasks</span>
      </div>
    </div>
  );
}
