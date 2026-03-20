import numpy as np
import pandas as pd

df = pd.read_csv("data/stock_data.csv", header=[0, 1], index_col=0, parse_dates=True)

tickers = ["AAPL", "UNH", "JPM", "XOM", "AMZN"]

close_prices = df.loc[:, (tickers, "Close")]
close_prices.columns = tickers
log_returns = np.log(close_prices / close_prices.shift(1)).dropna()

num_simulations = 10000
num_days = 252
num_stocks = len(tickers)
initial_portfolio_value = 1.0

weights = np.array([1/num_stocks] * num_stocks)

mean_daily_returns = log_returns.mean().values
daily_cov_matrix = log_returns.cov().values
annual_cov_matrix = daily_cov_matrix * 252

L = np.linalg.cholesky(daily_cov_matrix)

portfolio_returns = np.zeros(num_simulations)

np.random.seed(42)

for i in range(num_simulations):
    portfolio_value = initial_portfolio_value
    for day in range(num_days):
        Z = np.random.standard_normal(num_stocks)
        correlated_returns = mean_daily_returns + L @ Z
        daily_portfolio_return = np.dot(weights, correlated_returns)
        portfolio_value *= np.exp(daily_portfolio_return)
        
    portfolio_returns[i] = portfolio_value
    
portfolio_percentage_returns = (portfolio_returns - 1) * 100

print(f"Monte Carlo Simulation results ({num_simulations:,} simulations)")
print(f"Mean final portfolio value: ${np.mean(portfolio_returns):.4f}")
print(f"Median final portfolio value: ${np.median(portfolio_returns):.4f} ")
print(f"Std dev of final value: ${np.std(portfolio_returns):.4f}")
print(f"\nPercentage Returns:")
print(f"Mean return: {np.mean(portfolio_percentage_returns):+.2f}%")
print(f"Median return: {np.median(portfolio_percentage_returns):+.2f}%")
print(f"Best case: {np.max(portfolio_percentage_returns):+.2f}%")
print(f"Worst case: {np.min(portfolio_percentage_returns):+.2f}%")
print(f"5th percentile: {np.percentile(portfolio_percentage_returns, 5):+.2f}%")
print(f"95th percentile: {np.percentile(portfolio_percentage_returns, 95):+.2f}%")

var_95 = np.percentile(portfolio_percentage_returns, 5)
var_99 = np.percentile(portfolio_percentage_returns, 1)

print(f"\nValue at Risk (VaR) - 1 Year period:")
print(f"VaR 95%: {var_95:+.2f}%")
print(f"VaR 99%: {var_99:+.2f}%")

portfolio_value_dollars = 100000
print(f"\nFor a ${portfolio_value_dollars:,} portfolio:")
print(f"VaR 95%: ${abs(portfolio_value_dollars * var_95/100):.2f} max expected loss")
print(f"VaR 99%: ${abs(portfolio_value_dollars * var_99/100):.2f} max expected loss")

cvar_95 = portfolio_percentage_returns[portfolio_percentage_returns <= var_95].mean()
cvar_99 = portfolio_percentage_returns[portfolio_percentage_returns <= var_99].mean()

print(f"\nConditional Value at Risk (CVaR / Expected Shortfall)")
print(f"CVaR 95%: {cvar_95:.2f}%")
print(f"CVar 99%: {cvar_99:.2f}%")

print(f"Comparison - VaR vs CVaR:")
print(f"VaR 95%: {var_95:.2f}% - CVaR 95%: {cvar_95:.2f}%")
print(f"VaR 99%: {var_99:.2f}% - CVaR 99%: {cvar_99:.2f}%")

# Dollars terms:
print("\nFor a $100000 portfolio:")
print(f"CVaR 95%: ${abs(portfolio_value_dollars * cvar_95/100):.2f} avg loss in worst scenarios")
print(f"CVaR 99%: ${abs(portfolio_value_dollars * cvar_99/100):.2f} avg loss in worst scenarios")

pd.DataFrame({
    'Final value': portfolio_returns,
    'Pct Return': portfolio_percentage_returns,
}).to_csv("data/monte_carlo_results.csv", index=False)

pd.DataFrame({
    'Metric': ['VaR 95%', 'VaR 99%', 'CVaR 95%', 'CVaR 99%', 'Mean Return', 'Worst Case', 'Best Case'],
    'Value': [var_95, var_99, cvar_95, cvar_99,
              np.mean(portfolio_percentage_returns),
              np.min(portfolio_percentage_returns),
              np.max(portfolio_percentage_returns)]
}).to_csv("data/var_summary.csv", index=False)

print("Exported: monte_carlo_results, var_summary")