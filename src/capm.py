import pandas as pd
import numpy as np
import requests

# Binance API endpoint and parameters
api_url = 'https://api.binance.com/api/v3/klines'
symbol = 'BTCUSDT'
interval = '1d'
limit = 365

# Fetch market data from Binance API
params = {'symbol': symbol, 'interval': interval, 'limit': limit}
response = requests.get(api_url, params=params)
raw_data = response.json()

# Create pandas DataFrame with market data
market_data = pd.DataFrame(raw_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                               'close_time', 'quote_asset_volume', 'num_trades',
                                               'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                                               'ignore'])
market_data = market_data.astype({'timestamp': 'int64'})
market_data['date'] = pd.to_datetime(market_data['timestamp'], unit='ms')
market_data.set_index('date', inplace=True)

# Load crypto asset data from CSV file
df = pd.read_csv('../data/^CMC200.csv')
df.insert(0, 'date', pd.to_datetime(market_data['timestamp'], unit='ms'))
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# Join the two DataFrames using pd.concat()
df_merged = pd.concat([df, market_data], axis=1, join='inner')

# Calculate the daily returns of both assets
df_merged['crypto_returns'] = df_merged['close'].pct_change()
df_merged['market_returns'] = df_merged['close'].pct_change()

# Calculate the CAPM parameters
beta = np.cov(df_merged['crypto_returns'], df_merged['market_returns'])[0, 1] / np.var(df_merged['market_returns'])
risk_free_rate = 0.05  # Replace with your preferred risk-free rate
market_returns = df_merged['market_returns'].mean()

# Calculate the expected returns using the CAPM formula
df_merged['expected_returns'] = risk_free_rate + beta * (market_returns - risk_free_rate)

# Print the expected returns for the last 5 days
print(df_merged['expected_returns'].tail())
