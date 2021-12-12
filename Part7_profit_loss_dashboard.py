import pandas as pd
from binance.client import Client
from binance_keys import api_key, secret_key
import warnings
from datetime import datetime,timedelta
import plotly.express as px
import numpy as np

warnings.filterwarnings('ignore')

track_last_n_days = 45

#initialize vars
client = Client(api_key, secret_key,tld='us')

symbols = ['ADA','ATOM','BAT','BNB','SOL','DOGE','UNI','VET','BTC','ONT','ETC','FIL','MKR','ETH','LTC','ZRX','NEO']

syms = []
for symbol in symbols:
    syms.append(pd.DataFrame(client.get_all_orders(symbol=f'{symbol}USDT')))
df = pd.concat(syms)

df['time'] = [datetime.fromtimestamp(ts / 1000) for ts in df['time']]
df = df[df['time'] > datetime.now()-timedelta(days=track_last_n_days)]
df.sort_values('time',inplace=True)

trades = [] # [first date/time, symbol, avg sell price / avg buy price, prof / loss usd]
symbol = df['symbol'].iloc[0]
buy_fills = []
sell_fills = []
for i in range(len(df)):
    if df['symbol'].iloc[i] != symbol:
        # avg out trade
        if len(buy_fills) > 0 and len(sell_fills) > 0:
            total_buy_usd = np.sum([float(buy[2])*float(buy[3]) for buy in buy_fills])
            total_sell_usd = np.sum([float(sell[2])*float(sell[3]) for sell in sell_fills])

            total_buy_crypto = np.sum([float(buy[2]) for buy in buy_fills])
            total_sell_crypto = np.sum([float(sell[2]) for sell in sell_fills])
            
            avg_buy_price = total_buy_usd / total_buy_crypto
            avg_sell_price = total_sell_usd / total_sell_crypto

            trades.append([buy_fills[0][1], # first date/time
                          symbol,
                          np.round(avg_sell_price / avg_buy_price,4), 
                          total_sell_usd - total_buy_usd])
        
        buy_fills = []
        sell_fills = []
        symbol = df['symbol'].iloc[i]
                       
    # aggregate all fills for each trade
    if df['side'].iloc[i] == 'BUY':
        buy_fills.append([df['symbol'].iloc[i],df['time'].iloc[i],df['executedQty'].iloc[i],df['price'].iloc[i]])
        
    if df['side'].iloc[i] == 'SELL':
        if df['type'].iloc[i] == 'MARKET':
            sell_fills.append([df['symbol'].iloc[i],
                               df['time'].iloc[i],
                               df['executedQty'].iloc[i],
                               str(float(df['cummulativeQuoteQty'].iloc[i]) / float(df['executedQty'].iloc[i]))])
        else:
            sell_fills.append([df['symbol'].iloc[i],
                               df['time'].iloc[i],
                               df['executedQty'].iloc[i],
                               df['price'].iloc[i]])
            
results = pd.DataFrame(trades,columns=['time','symbol','profit_loss_percent','profit_loss_usd'])
results['datetime'] = '~' + results['time'].astype(str) # so plotly doesnt interpret as dt
results['profit'] = results['profit_loss_usd'] > 0
results['cumulative_prof_loss_usd'] = results['profit_loss_usd'].cumsum()
prof_loss_usd = np.round(sum(list(results['profit_loss_usd'])),2)

bar_plot = px.bar(results, 
                x='datetime',
                y='profit_loss_usd',
                hover_data=['symbol','time','profit_loss_percent'],
                color='profit',
                color_discrete_map={False:"red",True:"green"},
                text='symbol',
                title=f'Overall Profit/Loss: ${prof_loss_usd}',
                category_orders={'datetime':list(results['datetime'])},
                height=800)

line_plot = px.line(results,
                    x='time',
                    y='cumulative_prof_loss_usd',
                    hover_data=['symbol','time','profit_loss_percent'],
                    markers=True,
                    title=f'Overall Profit/Loss: ${prof_loss_usd}')