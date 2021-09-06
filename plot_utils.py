import plotly.graph_objects as go

def plot_initial(plot_df, symbol):
    fig = go.Figure(data=[go.Candlestick(x=plot_df['OpenTime'],
                open=plot_df[f'{symbol}-USD_Open'],
                high=plot_df[f'{symbol}-USD_High'],
                low=plot_df[f'{symbol}-USD_Low'],
                close=plot_df[f'{symbol}-USD_Close'])])

    fig.update_layout(xaxis_rangeslider_visible=False)

    fig.add_trace(go.Scatter(x=plot_df['OpenTime'], 
                             y=plot_df[f'{symbol}_sma'],
                             type='scatter', 
                             mode='lines',
                             line=dict(color='lightgrey'),
                             name='sma'))

    fig.add_trace(go.Scatter(x=plot_df['OpenTime'], 
                             y=plot_df[f'{symbol}_lower_band'],
                             type='scatter', 
                             mode='lines',
                             line=dict(color='grey'),
                             name='lower_band'))

    fig.add_trace(go.Scatter(x=plot_df['OpenTime'], 
                             y=plot_df[f'{symbol}_upper_band'],
                             type='scatter', 
                             mode='lines',
                             line=dict(color='grey'),
                             name='upper_band'))

    return fig.show()

def plot_results(plot_df, symbol, buys, sells):
    fig = go.Figure(data=[go.Candlestick(x=plot_df['OpenTime'],
                open=plot_df[f'{symbol}-USD_Open'],
                high=plot_df[f'{symbol}-USD_High'],
                low=plot_df[f'{symbol}-USD_Low'],
                close=plot_df[f'{symbol}-USD_Close'])])

    fig.update_layout(xaxis_rangeslider_visible=False)

    fig.add_trace(go.Scatter(x=plot_df['OpenTime'], 
                             y=plot_df[f'{symbol}_sma'],
                             type='scatter', 
                             mode='lines',
                             line=dict(color='lightgrey'),
                             name='sma'))

    fig.add_trace(go.Scatter(x=plot_df['OpenTime'], 
                             y=plot_df[f'{symbol}_lower_band'],
                             type='scatter', 
                             mode='lines',
                             line=dict(color='grey'),
                             name='lower_band'))

    fig.add_trace(go.Scatter(x=plot_df['OpenTime'], 
                             y=plot_df[f'{symbol}_upper_band'],
                             type='scatter', 
                             mode='lines',
                             line=dict(color='grey'),
                             name='upper_band'))

    fig.add_trace(go.Scatter(x=[buy[1] for buy in buys if buy[0] == symbol], 
                             y=[buy[2] for buy in buys if buy[0] == symbol],
                             type='scatter', 
                             mode='markers',
                             marker=dict(symbol='x',color='blue'),
                             name='buys'))

    fig.add_trace(go.Scatter(x=[sell[1] for sell in sells if sell[0] == symbol], 
                             y=[sell[2] for sell in sells if sell[0] == symbol],
                             type='scatter', 
                             mode='markers',
                             marker=dict(symbol='x',color='orange'),
                             name='sells'))

    fig.update_xaxes(range = [plot_df['OpenTime'].iloc[0],plot_df['OpenTime'].iloc[-1]])
    fig.update_yaxes(range = [min(plot_df[f'{symbol}-USD_Low'])*.99,max(plot_df[f'{symbol}-USD_High'])*1.01])

    return fig.show()