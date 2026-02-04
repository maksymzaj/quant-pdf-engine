from time import strftime

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import scipy.stats as stats


start_date=st.date_input("Start Sample", value=pd.to_datetime("2020-01-01"))
end_date=st.date_input("End Sample", value=pd.to_datetime("today"))
ticker=st.text_input("Ticker Symbol", value="AAPL")
@st.cache_data
def load_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end )
    if df.empty:
        return None

    daily_returns = df['Close'].pct_change().dropna().squeeze()
    return daily_returns

real_returns=load_data(ticker,start_date,end_date)
if real_returns is None:
    st.error("No data")
    st.stop()

lowest= real_returns.min()
highest= real_returns.max()

x_axis= np.linspace(lowest, highest, 100)

window_size=30

y_axis=real_returns.index[window_size:]

y_axis=y_axis.strftime('%Y-%d-%m')

X,Y=np.meshgrid(x_axis,y_axis)
z_data=[]
for i in range(window_size, len(real_returns)):
    current_data=real_returns[i-window_size:i]
    kde= stats.gaussian_kde(current_data)
    z_height=kde(x_axis)
    z_data.append(z_height)

fig=go.Figure(data=go.Surface(z=z_data, x=x_axis, y=y_axis))
fig.update_layout(title=f"Rolling Probability Surface: {ticker}",
                  scene=dict(xaxis_title="Returns",
                             yaxis_title="Time (Days)",
                             zaxis_title="Probability Density"))
st.plotly_chart(fig, use_container_width=True)