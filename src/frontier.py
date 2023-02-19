from binance.client import Client
import pandas as pd
import os


def getData(assets: list, interval: str, start: str, end: str):

    client = Client(os.environ.get("BINANCE_API_KEY"),
                    os.environ.get("BINANCE_API_SECRET"))
    frames = {}
    returns = []

    for asset in assets:
        data = client.get_historical_klines(asset, interval, start, end)
        df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                          'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

        df.drop(columns=['open_time', 'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'], inplace=True)

        df = df.apply(pd.to_numeric)
        df['pct_change'] = df['close'].pct_change()
        meanValues = df['pct_change'].mean()
        covariance = df.cov()
        returns.append(meanValues)
        returns.append(covariance)
        frames[asset] = returns

    return frames



frames = getData(["MATICBUSD", "ETHBUSD"], "1w", "1 Jan, 2022", "8 Feb, 2022")
print(frames)
