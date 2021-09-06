import pandas as pd
from plot_utils import plot_results

df = pd.read_csv('BTC_ETH_LTC_Jan2721_Jul2121_1h.csv')

def sma(data, window):
    return(data.rolling(window = window).mean())

def bollinger_band(data, sma, window, nstd):
    std = data.rolling(window = window).std()
    upper_band = sma + std * nstd
    lower_band = sma - std * nstd
    
    return upper_band, lower_band

symbols = ['BTC','ETH','LTC']

nstd = 3

for symbol in symbols:
    df[f'{symbol}_sma'] = sma(df[f'{symbol}-USD_Open'], 20)
    df[f'{symbol}_upper_band'], df[f'{symbol}_lower_band'] = bollinger_band(df[f'{symbol}-USD_Open'], df[f'{symbol}_sma'], 20, nstd)
    
df.dropna(inplace=True)

class TradingEnv:
    def __init__(self, balance_amount, balance_unit, trading_fee_multiplier):
        self.balance_amount = balance_amount
        self.balance_unit = balance_unit
        self.buys = []
        self.sells = []
        self.trading_fee_multiplier = trading_fee_multiplier
        
    def buy(self, symbol, buy_price, time):
        self.balance_amount = (self.balance_amount / buy_price) * self.trading_fee_multiplier
        self.balance_unit = symbol
        self.buys.append([symbol, time, buy_price])
        
    def sell(self, sell_price, time):
        self.balance_amount = self.balance_amount * sell_price * self.trading_fee_multiplier
        self.sells.append( [self.balance_unit, time, sell_price] )
        self.balance_unit = 'USDT'

# VIP level 0, paying fees with BNB = 0.075%
env = TradingEnv(balance_amount=100,balance_unit='USDT', trading_fee_multiplier=0.99925)

for i in range(len(df)):
    if env.balance_unit == 'USDT':
        for symbol in symbols:
            if df[f'{symbol}-USD_Low'].iloc[i] < df[f'{symbol}_lower_band'].iloc[i]: #buy signal
                env.buy(symbol, df[f'{symbol}_lower_band'].iloc[i], df['OpenTime'].iloc[i])
                break
                
    if env.balance_unit != 'USDT':
        if df[f'{env.balance_unit}-USD_High'].iloc[i] > df[f'{env.balance_unit}_upper_band'].iloc[i]: #sell signal
            env.sell(df[f'{env.balance_unit}_upper_band'].iloc[i], df['OpenTime'].iloc[i])

if env.balance_unit != 'USDT':
    env.sell(df[f'{env.balance_unit}-USD_Close'].iloc[-1], df['OpenTime'].iloc[-1])

print(f'num buys: {len(env.buys)}')
print(f'num sells: {len(env.sells)}')
print(f'ending balance: {env.balance_amount} {env.balance_unit}')

plot_results(df, 'LTC', env.buys, env.sells)