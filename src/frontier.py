from binance.client import Client
import numpy as np
import pandas as pd
import os
import requests

# Binance API
url = 'https://api.binance.com/api/v3/exchangeInfo'
response = requests.get(url)
exchange_info = response.json()
trading_pairs = [symbol['symbol'] for symbol in exchange_info['symbols']]
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


def walletStats(frames: dict, weights: dict):

    expectedReturn = 0
    expectedVolatility = 0
    for key in weights.keys():
        expectedReturn += weights[key]*(frames[key])[0]
        expectedVolatility += weights[key]*(frames[key])[1]

    return expectedReturn, expectedVolatility


def menu():

    requestData = True

    assets = []
    weights = {}

    while requestData:

        asset = ""
        while asset not in trading_pairs:
            asset = str(input("Enter a pair: "))
            if asset not in trading_pairs:
                print("Invalid asset")
        assets.append(asset)

        weight = -1
        while weight < 0 or weight > 1:
            weight = float(input("Enter the asset weight: "))
            if weight < 0 or weight > 1:
                print("Invalid weight")
            weights[asset] = weight
            totalWeight = 0  # initialize totalWeight to 0
            for key in weights.keys():
                totalWeight += weights[key]
            if totalWeight > 1:
                print("Total weight must be less than 1")
                del weights[asset]
                weight = -1

        answer = ""
        while answer.lower() != 'y' and answer.lower() != 'n':
            answer = str(input("Do you want to add another asset? (y/n): "))
            if answer.lower() != 'y' and answer.lower() != 'n':
                print("Invalid answer")

        if answer.lower() == 'n':
            requestData = False

    data = getData(assets, '1w', '1 Feb, 2023', '22 Feb, 2023')
    marketData = parseMarketData()
    expectedReturn, expectedVolatility = walletStats(data, weights)

    print(
        f"Portfolio Expected Returns:\n{np.round(expectedReturn,4)}\nPortfolio Expected Volatility:\n:{np.round(expectedVolatility,4)}\nComparing with the market:\nMarket Expected Returns:\n{np.round(marketData[0],4)}\nMarket Expected Volatility:\n{np.round(marketData[1],4)}")


menu()
