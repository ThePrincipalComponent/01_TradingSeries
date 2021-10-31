import pandas as pd
from binance.client import Client
from binance_keys import api_key, secret_key
from datetime import datetime, timedelta
import time
from binance.exceptions import *

client = Client(api_key, secret_key,tld='us')

def sma(data, window):
    return(data.rolling(window = window).mean())

def bollinger_band(data, sma, window, nstd):
    std = data.rolling(window = window).std()
    upper_band = sma + std * nstd
    lower_band = sma - std * nstd
    
    return upper_band, lower_band

def gather_data(symbols,start_n_hours_ago):
    merge = False
    for symbol in symbols:
        klines = client.get_historical_klines(symbol=f'{symbol}USDT', 
                                              interval=client.KLINE_INTERVAL_1HOUR, 
                                              start_str=str(datetime.now()-timedelta(hours=start_n_hours_ago)))
        cols = ['OpenTime',
                f'{symbol}-USD_Open',
                f'{symbol}-USD_High',
                f'{symbol}-USD_Low',
                f'{symbol}-USD_Close',
                f'{symbol}-USD_volume',
                'CloseTime',
                f'{symbol}-QuoteAssetVolume',
                f'{symbol}-NumberOfTrades',
                f'{symbol}-TBBAV',
                f'{symbol}-TBQAV',
                f'{symbol}-ignore']

        df = pd.DataFrame(klines,columns=cols)

        if merge == True:
            dfs = pd.merge(df,dfs,how='inner',on=['OpenTime','CloseTime'])
        else:
            dfs = df
            merge = True

    dfs['OpenTime'] = [datetime.fromtimestamp(ts / 1000) for ts in dfs['OpenTime']]
    dfs['CloseTime'] = [datetime.fromtimestamp(ts / 1000) for ts in dfs['CloseTime']]

    for col in dfs.columns:
        if not 'Time' in col:
            dfs[col] = dfs[col].astype(float)

    for symbol in symbols:
        dfs[f'{symbol}_sma'] = sma(dfs[f'{symbol}-USD_Close'],window=20)
        dfs[f'{symbol}_upper_band'], dfs[f'{symbol}_lower_band'] = bollinger_band(data=dfs[f'{symbol}-USD_Close'],
                                                                                  sma=dfs[f'{symbol}_sma'],
                                                                                  window=20,
                                                                                  nstd=3)

    dfs.dropna(inplace=True)
    
    return dfs

def get_states(df,symbols):
    states = {}

    for symbol in symbols:
        if df[f'{symbol}-USD_Close'].iloc[-1] < df[f'{symbol}_lower_band'].iloc[-1]:
            states[symbol] = 'below'
        elif df[f'{symbol}-USD_Close'].iloc[-1] > df[f'{symbol}_upper_band'].iloc[-1]:
            states[symbol] = 'above'
        else:
            states[symbol] = 'inside'
    
    return states

symbols = ['BTC','ETH','LTC']
start_n_hours_ago = 48

balance_unit = 'USDT'
first = True

while True:
    if (datetime.now().second % 10 == 0) or first:
        if (datetime.now().minute == 17 and datetime.now().second == 10) or first:
            # refresh data
            first = False
            df = gather_data(symbols,48)
            states = get_states(df,symbols)
            print('Current state of the market:')
            print(states)
        try:
            print('\n')
            if balance_unit == 'USDT': # looking to buy
                for symbol in symbols:
                    ask_price = float(client.get_orderbook_ticker(symbol = f'{symbol}USDT')['askPrice'])
                    lower_band = df[f'{symbol}_lower_band'].iloc[-1]
                    print(f'{symbol}: ask price {ask_price} | lower band {lower_band}')
                    if ask_price < lower_band and states[symbol] == 'inside': #buy signal
                        print('buy')
                        balance_unit = symbol
                        break

            if balance_unit != 'USDT': # looking to sell
                bid_price = float(client.get_orderbook_ticker(symbol = f'{balance_unit}USDT')['bidPrice'])
                upper_band = df[f'{balance_unit}_upper_band'].iloc[-1]
                if bid_price > upper_band and states[balance_unit] == 'inside': #sell signal
                    print('sell')
                    balance_unit = 'USDT'

            time.sleep(1)
            
        except BinanceAPIException as e:
            print(e.status_code)
            print(e.message)