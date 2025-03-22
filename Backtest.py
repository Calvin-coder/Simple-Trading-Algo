import pandas as pd
import numpy as np
from scipy.stats import linregress

def calculate_metrics(portfolio_values, benchmark_values, risk_free_rate= 0.02):
    """
    Calculate performance metrics: Alpha, Delta, Sharpe Ratio, and Win Rate.
    """
    portfolio_values = np.array(portfolio_values).flatten()
    benchmark_values = np.array(benchmark_values).flatten()
    
    if len(portfolio_values) < 2 or len(benchmark_values) < 2:
        return 0, 0, 0, 0
        
    min_length = min(len(portfolio_values), len(benchmark_values))
    portfolio_values = portfolio_values[:min_length]
    benchmark_values = benchmark_values[:min_length]
    
    portfolio_returns = np.diff(portfolio_values) / portfolio_values[:-1]
    benchmark_returns = np.diff(benchmark_values) / benchmark_values[:-1]
    
    if len(portfolio_returns) < 2 or len(benchmark_returns) < 2:
        return 0, 0, 0, 0
    
    excess_returns = portfolio_returns - risk_free_rate
    if np.std(excess_returns) == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    
    try:
        slope, intercept, _, _, _ = linregress(benchmark_returns, portfolio_returns)
        alpha = intercept * 252  # Annualized alpha
    except Exception:
        alpha = 0
    
    try:
        delta = np.corrcoef(portfolio_returns, benchmark_returns)[0, 1]
    except Exception:
        delta = 0
    
    win_rate = np.sum(portfolio_returns > 0) / len(portfolio_returns)
    
    return alpha, delta, sharpe_ratio, win_rate

def backtest_multi_asset(asset_data, common_index, strategy_function, benchmark_data, initial_capital):
    """
    Backtest a strategy across multiple assets and calculate performance metrics.
    """
    portfolio_df = pd.DataFrame(index=common_index)
    
    # Initialize tracking structures for positions and portfolio value
    positions = {ticker: 0 for ticker in asset_data}
    previous_positions = {ticker: 0 for ticker in asset_data}
    cash = initial_capital
    trades = 0
    portfolio_values = []
    
    # Run the strategy for each asset and store the results
    for ticker in asset_data:
        result_df = strategy_function(asset_data[ticker])
        portfolio_df[f"{ticker}_Price"] = asset_data[ticker]["Close"]
        portfolio_df[f"{ticker}_Position"] = result_df["Position"]
    
    # Simulate the backtest
    for current_time in common_index:
        buy_list = []
        sell_list = []
        
        for ticker in asset_data:
            current_position = portfolio_df.loc[current_time, f"{ticker}_Position"]
            if current_position != previous_positions[ticker]:
                if previous_positions[ticker] == 0 and current_position == 1:
                    buy_list.append(ticker)
                elif previous_positions[ticker] == 1 and current_position == 0:
                    sell_list.append(ticker)
            previous_positions[ticker] = current_position
        
        # Execute sell trades
        for ticker in sell_list:
            price = portfolio_df.loc[current_time, f"{ticker}_Price"]
            if isinstance(positions[ticker], dict) and "shares" in positions[ticker]:
                cash += positions[ticker]["shares"] * price
                positions[ticker] = 0
                trades += 1
        
        # Execute buy trades
        if buy_list:
            allocation = cash / len(buy_list)
            for ticker in buy_list:
                price = portfolio_df.loc[current_time, f"{ticker}_Price"]
                shares = allocation / price
                positions[ticker] = {"shares": shares, "entry_price": price}
                cash -= allocation
                trades += 1
        
        # Update portfolio value
        portfolio_value = cash
        for ticker in asset_data:
            if isinstance(positions[ticker], dict) and "shares" in positions[ticker]:
                price = portfolio_df.loc[current_time, f"{ticker}_Price"]
                portfolio_value += positions[ticker]["shares"] * price
        
        portfolio_values.append(portfolio_value)
    
    if not portfolio_values:
        return 0, initial_capital, 0, 0, 0, 0
        
    final_portfolio_value = portfolio_values[-1]
    
    # Prepare benchmark values array for metrics calculation
    if isinstance(benchmark_data, pd.Series):
        benchmark_values = benchmark_data.values
    else:
        benchmark_values = np.array(benchmark_data)
    
    if len(benchmark_values) > len(portfolio_values):
        benchmark_values = benchmark_values[:len(portfolio_values)]
    elif len(benchmark_values) < len(portfolio_values):
        portfolio_values = portfolio_values[:len(benchmark_values)]
    
    alpha, delta, sharpe_ratio, win_rate = calculate_metrics(portfolio_values, benchmark_values)
    
    return trades, final_portfolio_value, alpha, delta, sharpe_ratio, win_rate
