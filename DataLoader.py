import yfinance as yf
import pandas as pd

def load_data(tickers, start_date, end_date, interval):
    df_open = pd.DataFrame()
    df_high = pd.DataFrame()
    df_low = pd.DataFrame()
    df_close = pd.DataFrame()
    df_volume = pd.DataFrame()

    for ticker in tickers:
        df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        df_open[ticker] = df["Open"]
        df_high[ticker] = df["High"]
        df_low[ticker] = df["Low"]
        df_close[ticker] = df["Close"]
        df_volume[ticker] = df["Volume"]
    
    df_open.sort_index(inplace=True)
    df_high.sort_index(inplace=True)
    df_low.sort_index(inplace=True)
    df_close.sort_index(inplace=True)
    df_volume.sort_index(inplace=True)

    return df_open, df_high, df_low, df_close, df_volume



"""
# Define parameters
tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "META"]
start_date = "2020-01-01"
end_date = "2021-01-01"
interval = "1d"  # Change as needed (e.g., "5m", "1h", etc.)

# Load data into separate DataFrames
df_open, df_high, df_low, df_close, df_volume = load_data(tickers, start_date, end_date, interval)

# Print the DataFrames
print("Open Prices:")
print(df_open.head(), "\n")

print("High Prices:")
print(df_high.head(), "\n")

print("Low Prices:")
print(df_low.head(), "\n")

print("Close Prices:")
print(df_close.head(), "\n")

print("Volume:")
print(df_volume.head(), "\n")"
"""