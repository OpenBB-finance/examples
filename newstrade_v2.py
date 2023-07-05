import streamlit as st 
from openbb_terminal.sdk import openbb
import pandas as pd
import plotly.graph_objects as go


cont1, cont2 = st.columns(2)
    
    
ticker = cont1.text_input(
        label = "Add a stock  to track",
        value = "META"
    )
    


def get_news_signal(ticker, *args, **kwargs):
    
    signal = {
        'buy' : "BUY! Sentiment at ",
        'sell' : "SELL Sentiment at "
    }
    
    if ticker is not None:
        latest_article = openbb.stocks.ba.cnews(f"{ticker}")[0]
        
    else:
        st.write("Please add a valid ticker name")
    
    sentiment = openbb.stocks.ba.text_sent(latest_article["summary"])
    
    if sentiment >= 0.5:
        cont2.write(signal['buy'] + str(sentiment))
        cont2.write("Read the news here")
        cont2.write(latest_article["url"])
    elif sentiment <= -0.25:
        cont2.write(signal['sell']  + str(sentiment))
        cont2.write("Read the news here")
        cont2.write(latest_article["url"])
    else:
        cont2.write("No useful signal. Latest news sentiment is at " + str(sentiment))
        cont2.write("Read the news here")
        cont2.write(latest_article["url"])

    return

get_news_signal(ticker)