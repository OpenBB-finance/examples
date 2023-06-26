import streamlit as st 
from openbb_terminal.sdk import openbb
import pandas as pd
import plotly.graph_objects as go


st.write("Custom Dashboard using OpenBB")

choice = st.selectbox(label = 'Choose a Stock', options = ('aapl', 'tsla', 'f', 'rivn', 'meta', 'msft', 'gm'))
st.table(data = openbb.stocks.load(choice).tail(5))

df = openbb.stocks.load(choice)
fig = go.Figure(data=[go.Candlestick(
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])

st.write(fig)
