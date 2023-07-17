import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openbb_terminal.sdk import openbb
import streamlit as st
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.callbacks import get_openai_callback


st.set_page_config(page_title="Options Analysis", page_icon="📈", layout="wide")

st.title("Options Analysis with OpenBB:butterfly: & ChatGPT:robot_face:")

unu_df, unu_ts = openbb.stocks.options.unu(limit = 500)

unu_df = unu_df.sort_values(by = 'Vol/OI', ascending = False)
choice = st.selectbox(
    label = "Choose an Option based on today's Open Interest",
    options = (unu_df['Ticker'])
)

cont = st.container()

with cont:
    @st.cache_data(experimental_allow_widgets=True)
    def data_stream():

        st.write("Choose a Dataset to load for your Stock Option")

        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
        expiry = datetime.today() + relativedelta(months=1)

        if 'data' not in st.session_state:
            st.session_state['data'] = openbb.stocks.options.info(choice)

        if col1.button('Put-Call Ratio'):
            st.session_state['data'] = openbb.stocks.options.pcr(choice)

        if col2.button('Options Info'):
            st.session_state['data'] = openbb.stocks.options.info(choice)

        if col3.button('Options Chains'):
            st.session_state['data'] = openbb.stocks.options.chains(choice)

        if col4.button('EOD Chain', help = "Requires Intrinio API Key :closed_lock_with_key:"):
            st.session_state['data'] = openbb.stocks.options.eodchain(choice)

        if col5.button('Volatility Surface'):
            st.session_state['data'] = openbb.stocks.options.vsurf(choice)


data_stream()

data1 = st.session_state['data']
st.write(data1)

table_name = 'statesdb'
uri = "file:memory?cache=shared&mode=memory"
openai_key = st.secrets["OPENAI_KEY"]

query = st.text_input(
    label = "Any questions?",
    help = "Ask any question based on the loaded dataset")

conn = sqlite3.connect(uri, uri=True)


data1.to_sql(table_name, conn, if_exists = "replace", index = False)

db_eng = create_engine(
    url = 'sqlite:///file:memdb1?mode=memory&cache=shared',
    poolclass = StaticPool,
    creator = lambda: conn
)
db = SQLDatabase(engine = db_eng)

lang_model = OpenAI(
    openai_api_key = openai_key,
    temperature = 0.9,
    max_tokens = 300
)
db_chain = SQLDatabaseChain(llm = lang_model, database = db, verbose = True)


if query:
    with get_openai_callback() as cb:
        response = db_chain.run(query)
        st.sidebar.write("Your request costs: " + str(cb.total_cost) + "USD")
    st.write(response)
