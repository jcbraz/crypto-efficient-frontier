import numpy as np
import pandas as pd
from binance.client import Client
import os

client = Client(os.environ.get("BINANCE_API_KEY"),
                os.environ.get("BINANCE_API_SECRET"))


def getData(assets: list, interval: str, start: str, end: str):

    frames = {}

    for asset in assets:

        returns = []

        data = client.get_historical_klines(asset, interval, start, end)
        df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                          'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

        df.drop(columns=['open_time', 'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'], inplace=True)

        df['close'] = pd.to_numeric(df['close'])
        df['daily_return'] = df['close'].pct_change()
        mean_return = np.round(np.mean(df['daily_return']), 4)
        std_return = np.std(df['daily_return'])
        annualized_volatility = np.round(std_return * np.sqrt(365), 4)

        returns.append(mean_return)
        returns.append(annualized_volatility)
        frames[asset] = returns

    return frames


def parseMarketData():
    df = pd.read_csv('../data/^CMC200.csv')
    df['Close'] = pd.to_numeric(df['Close'])
    df['daily_return'] = df['Close'].pct_change()

    mean_return = np.round(np.mean(df['daily_return']), 4)
    std_return = np.std(df['daily_return'])
    annualized_volatility = np.round(std_return * np.sqrt(365), 4)

    return mean_return, annualized_volatility


def calculateBeta(frames: dict, marketRentability: float, marketVolatility: float) -> dict:

    betas = {}

    for asset, returns in frames.items():
        asset_mean_return = returns[0]
        covariance = np.cov(asset_mean_return, marketRentability)[0][1]
        beta = covariance / marketVolatility
        betas[asset] = beta

    return betas


assets = ['LDOBUSD', 'ETHBUSD']
data = getData(assets, '1w', '1 Jan, 2021', '22 Feb, 2023')
rent, vol = parseMarketData()
print(calculateBeta(data, rent, vol))
