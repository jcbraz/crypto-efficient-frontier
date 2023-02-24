from binance.client import Client
import numpy as np
import pandas as pd
import pandas_datareader as pdr
import matplotlib.pyplot as plt
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
        mean_return = np.round(np.mean(df['daily_return']),4)
        std_return = np.std(df['daily_return'])
        annualized_volatility = np.round(std_return * np.sqrt(365),4)

        returns.append(mean_return)
        returns.append(annualized_volatility)
        frames[asset] = returns

    return frames


def parseMarketData():
    df = pd.read_csv('../data/^CMC200.csv')
    df['Close'] = pd.to_numeric(df['Close'])
    df['daily_return'] = df['Close'].pct_change()

    mean_return = np.round(np.mean(df['daily_return']),4)
    std_return = np.std(df['daily_return'])
    annualized_volatility = np.round(std_return * np.sqrt(365),4)

    return mean_return, annualized_volatility


def walletStats(frames: dict, weights: dict):

    expectedReturn = 0
    expectedVolatility = 0
    for key in weights.keys():
        expectedReturn += weights[key]*(frames[key])[0]
        expectedVolatility += weights[key]*(frames[key])[1]

    return expectedReturn, expectedVolatility

    

    

assets = ['LDOBUSD','OPBUSD']
weights = {'LDOBUSD': 0.8, 'OPBUSD': 0.2 }


data = getData(assets, '1w', '1 Feb, 2023', '22 Feb, 2023')
marketData = parseMarketData()
expectedReturn, expectedVolatility = walletStats(data, weights)
# print(expectedReturn, expectedVolatility)
# print(isInEfficientFrontier([marketData[0]], [marketData[1]], expectedReturn, expectedVolatility))

