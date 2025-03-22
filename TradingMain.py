from Backtest import backtest_multi_asset
from DataLoader import load_data
from TradingAlgo import mean_reversion_strategy
import yfinance as yf

# Define tickers and date range
tickers = ["AAPL", "MSFT", "AMZN"]
start_date = "2024-01-01"
end_date = "2025-01-01"
interval = "1h"
initial_capital = 100

# Unpack the returned tuple to get df_close
_, _, _, df_close, _ = load_data(tickers, start_date, end_date, interval)

# Use df_close as your combined DataFrame
combined_df = df_close

# Convert the combined DataFrame into a dictionary for each ticker.
asset_data = {}
for ticker in combined_df.columns:
    df = combined_df[[ticker]].copy()
    df = df.rename(columns={ticker: "Close"})
    asset_data[ticker] = df

# The common index is simply the index of the combined DataFrame
common_index = combined_df.index

# Load benchmark data S&P 500 and reindex it to the common index
benchmark_data = yf.download('^GSPC', start=start_date, end=end_date, interval=interval)['Close']
benchmark_data = benchmark_data.reindex(common_index).ffill()

# Run the backtest with the mean reversion strategy
trades, final_portfolio_value, alpha, delta, sharpe_ratio, win_rate = backtest_multi_asset(
    asset_data, common_index, mean_reversion_strategy, benchmark_data, initial_capital
)

# Print out the results
print(f"Total Trades: {trades}")
print(f"Final Portfolio Value: ${final_portfolio_value:.2f}")
print(f"Alpha: {alpha:.4f}")
print(f"Delta: {delta:.4f}")
print(f"Sharpe Ratio: {sharpe_ratio:.4f}")
print(f"Win Rate: {win_rate:.2%}")
