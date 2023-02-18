from binance.client import Client
import pandas as pd
import os


def getData(assets: list, interval: str, start: str, end: str):
    client = Client(os.environ.get("BINANCE_API_KEY"),
                    os.environ.get("BINANCE_API_SECRET"))
    frames = {}

    for asset in assets:
        data = client.get_historical_klines(asset, interval, start, end)
        df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                          'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

        df.drop(columns=['open_time', 'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'], axis=1, inplace=True)

        df = df.apply(pd.to_numeric)
        df['close_pct_change'] = df['close'].pct_change()
        frames[asset] = df

    return frames


print(getData(["MATICBUSD", "ETHBUSD"], "1w", "1 Jan, 2022", "8 Feb, 2022"))
