import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import pandas as pd

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

def shade_plot(data,x_col,y_col,avg_col,n_splits,range_color=[0.99,1.01],filter_out_count=50):
    xs = np.linspace(data[x_col].min(),data[x_col].max(),n_splits)
    ys = np.linspace(data[y_col].min(),data[y_col].max(),n_splits)
    
    mean = {}
    count = {}
    median = {}
    x_dist = xs[1]-xs[0]
    y_dist = ys[1]-ys[0]
    for y in ys:
        mean[y] = []
        median[y] = []
        count[y] = []
        for x in xs:
            if data[(data[x_col] >= x) & \
                (data[x_col] < x+x_dist) & \
                (data[y_col] >= y) & \
                (data[y_col] < y+y_dist)][avg_col].count() > filter_out_count:
                
                mean[y].append(data[(data[x_col] >= x) & \
                                        (data[x_col] < x+x_dist) & \
                                        (data[y_col] >= y) & \
                                        (data[y_col] < y+y_dist)][avg_col].mean())
                
                median[y].append(data[(data[x_col] >= x) & \
                                        (data[x_col] < x+x_dist) & \
                                        (data[y_col] >= y) & \
                                        (data[y_col] < y+y_dist)][avg_col].mean())
                
            else:
                mean[y].append(1)
                median[y].append(1)
                
            count[y].append(data[(data[x_col] >= x) & \
                                    (data[x_col] < x+x_dist) & \
                                    (data[y_col] >= y) & \
                                    (data[y_col] < y+y_dist)][avg_col].count())
    
    
    fig = px.imshow(pd.DataFrame(mean,index=xs).swapaxes("index", "columns"),
                      color_continuous_scale='RdBu',
                      range_color=range_color,
                      color_continuous_midpoint=1,
                      title='Means')
    
    fig1 = px.imshow(pd.DataFrame(median,index=xs).swapaxes("index", "columns"),
                      color_continuous_scale='RdBu',
                      range_color=range_color,
                      color_continuous_midpoint=1,
                      title='Medians')
    
    fig2 = px.imshow(pd.DataFrame(count,index=xs).swapaxes("index", "columns"),title='Count')
    
    fig.show()
    fig1.show()
    fig2.show()
    