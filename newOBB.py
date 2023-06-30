import streamlit as st 
from openbb_terminal.sdk import openbb
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.header("Custom Dashboard using OpenBB")

tab1, tab3, tab4, tab5 = st.tabs(["Stocks", "Forex", "Economic Index", "ETF"])

with tab1:    
    choice = st.selectbox(
        label = "Choose a Stock Ticker.",
        options = ('AAPL', 'TSLA', 'AMZN', 'AMD', 'META', 'GM', 'NVDA', 'QQQ', 'MSFT', 'GOOG', 'GOOGL', 'F')
    )
    
    

    col1, col2 = st.columns(2)

    with col1:
        df = openbb.stocks.load(choice, source = 'Polygon')
        st.write("Data for " + str(choice) + " Stock Price")
        st.write(df)

    with col2:
        st.write("Chart for " + str(choice) + " Closing Price")
        fig = go.Figure(
            data = [
                go.Candlestick(
                    open = df['Open'],
                    high = df['High'],
                    low = df['Low'],
                    close = df['Close']
                )
            ]
        )

        st.write(fig)
    
with tab3:
    currencies = tuple(openbb.forex.get_currency_list())
    from_sym = st.selectbox(
        label = "Choose a Currency.",
        options = (currencies),
        index = currencies.index('USD')
    )
    to_sym = st.selectbox(
        label = "Choose a second Currency.",
        options = (currencies),
        index = currencies.index('EUR')
    )
    
    col1, col2 = st.columns(2)

    with col1:
        st.write("Data for " + str(from_sym) + "-" + str(to_sym) + " price")
        df3 = openbb.forex.load(from_symbol = from_sym, to_symbol = to_sym, source = "Polygon")

        st.write(df3)

    with col2:
        st.write("Chart for " + str(from_sym) + "-" + str(to_sym) + " Price")
        fig3 = go.Figure(
            data = [
                go.Candlestick(
                    open = df3['Open'],
                    high = df3['High'],
                    low = df3['Low'],
                    close = df3['Close']
                )
            ]
        )
        st.write(fig3)

with tab4:
    st.write("Data for Top US Economic Indices")
    st.write(openbb.economy.indices())

with tab5:
    etfs = tuple(openbb.etf.symbols()[0])
    choice5 = st.selectbox(
        label = "Choose an ETF to load.",
        options = (etfs)
    )
    
    col1, col2 = st.columns(2)

    with col1:
        st.write("Data for " + str(choice5) + " ETF Price")
        df5 = openbb.etf.load(symbol = f"{choice5}", source = "Polygon")
    
        st.write(df5)
    with col2:
        st.write("Candle Chart for " + str(choice5) + " ETF Price")
        fig4 = go.Figure(
            data = [
                go.Candlestick(
                    open = df5['Open'],
                    high = df5['High'],
                    low = df5['Low'],
                    close = df5['Close']
                )
            ]
        )
        st.write(fig4)