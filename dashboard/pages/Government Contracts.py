import pandas as pd
from openbb_terminal.sdk import openbb
import streamlit as st
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.callbacks import get_openai_callback


st.set_page_config(page_title="Government Activity", page_icon="🗳️", layout="wide")

st.title("Government Activity Analysis with OpenBB:butterfly: & ChatGPT:robot_face:")

choice = st.selectbox(
    label = "Choose an Option based on today's Open Interest",
    options = ('AAPL', 'TSLA', 'AMZN', 'AMD', 'META', 'GM', 'NVDA', 'QQQ', 'MSFT', 'GOOG', 'GOOGL', 'F')
)

gov_type = st.selectbox(
    label = "Choose the type of Government Institution",
    options = ('congress', 'senate', 'house')
)

cont = st.container()

with cont:
    @st.cache_data(experimental_allow_widgets=True)
    def data_stream():

        st.write("Choose a Dataset to load for your Stock Option")

        col1, col2, col3, col4, col5, col6, col7 = st.columns([1,1,1,1,1,1,1])
        
        if 'data' not in st.session_state:
            st.session_state['data'] = openbb.stocks.gov.contracts(choice)

        if col1.button('Government Contracts'):
            st.session_state['data'] = openbb.stocks.gov.contracts(choice)

        if col2.button('Government Trading'):
            st.session_state['data'] = openbb.stocks.gov.government_trading(gov_type = gov_type, symbol = choice)

        if col3.button('Historical Quarterly Contracts'):
            st.session_state['data'] = openbb.stocks.gov.histcont(choice)

        if col4.button('Corporate Lobbying'):
            st.session_state['data'] = openbb.stocks.gov.lobbying(choice)

        if col5.button('Top Government Buys'):
            st.session_state['data'] = openbb.stocks.gov.topbuys(gov_type)
            
        if col6.button('Top Government Sells'):
            st.session_state['data'] = openbb.stocks.gov.topsells(gov_type)
            
        if col7.button('Top Government Lobbies'):
            st.session_state['data'] = openbb.stocks.gov.toplobbying()


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

if isinstance(data1, pd.DataFrame):
    if not data1.empty:
        data1.to_sql(table_name, conn, if_exists = "replace", index = False)
    else:
        st.write("No data")

else:
    st.write("Error. Invalid data or failed API connection.")

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
