import pandas as pd
from binance.client import Client
from binance_keys import api_key, secret_key
from datetime import datetime, timedelta
import time
from binance.exceptions import *
from auxiliary_functions import *

symbols = ['BTC','ETH','LTC']
start_n_hours_ago = 48
balance_unit = 'USDT'
first = True

BUY_AMOUNT_USDT = 100

precision = {}
for symbol in symbols:
    precision[symbol] = client.get_symbol_info(f'{symbol}USDT')['quotePrecision']

while True:
    if (datetime.now().second % 10 == 0) or first:
        if (datetime.now().minute == 0 and datetime.now().second == 10) or first:
            # refresh data
            first = False
            df = gather_data(symbols,48)
            states = get_states(df,symbols)
            print('Current state of the market:')
            print(states)
            print('\n')

        try:
            if balance_unit == 'USDT': # looking to buy
                for symbol in symbols:
                    ask_price = float(client.get_orderbook_ticker(symbol = f'{symbol}USDT')['askPrice'])
                    lower_band = df[f'{symbol}_lower_band'].iloc[-1]
                    
                    if ask_price < lower_band and states[symbol] == 'inside': #buy signal
                        ######################
                        print(f'Buy order placed:')
                        buy_order = client.order_limit_buy(symbol=f'{symbol}USDT',
                                                          quantity=truncate(BUY_AMOUNT_USDT / ask_price, precision[symbol]),
                                                          price = ask_price)
                        print(buy_order)

                        start = datetime.now()
                        while True:
                            time.sleep(1)
                            buy_order = client.get_order(symbol=buy_order['symbol'], orderId=buy_order['orderId'])

                            seconds_since_buy = (datetime.now() - start).seconds

                            # resolve buy order
                            if float(buy_order['executedQty']) == 0 and seconds_since_buy > 60*60:
                                # no fill
                                client.cancel_order(symbol=buy_order['symbol'], orderId=buy_order['orderId'])
                                print('Order not filled after 1 hour, cancelled.')
                                print('\n')
                                break

                            if float(buy_order['executedQty']) != 0 and float(buy_order['executedQty']) != float(buy_order['origQty']) and seconds_since_buy > 60*60:
                                # partial fill
                                client.cancel_order(symbol=buy_order['symbol'], orderId=buy_order['orderId'])
                                balance_unit = symbol
                                print('Order partially filled after 1 hour, cancelled the rest and awaiting sell signal.')
                                print('\n')
                                break

                            if float(buy_order['executedQty']) ==  float(buy_order['origQty']):
                                # completely filled
                                balance_unit = symbol
                                print('Order filled:')
                                print(buy_order)
                                print('\n')
                                break
                        
                        ######################

            if balance_unit != 'USDT': # looking to sell
                bid_price = float(client.get_orderbook_ticker(symbol = f'{balance_unit}USDT')['bidPrice'])
                upper_band = df[f'{balance_unit}_upper_band'].iloc[-1]
                if bid_price > upper_band and states[balance_unit] == 'inside': #sell signal
                    ######################
                    client.order_market_sell(symbol=buy_order['symbol'],
                                            quantity=truncate(float(buy_order['executedQty']), precision[buy_order['symbol'].replace('USDT','')]))
                    
                    ######################
                    balance_unit = 'USDT'

            time.sleep(1)
            
        except BinanceAPIException as e:
            print(e.status_code)
            print(e.message)