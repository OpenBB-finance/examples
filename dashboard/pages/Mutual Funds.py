import pandas as pd
from openbb_terminal.sdk import openbb
import streamlit as st
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.callbacks import get_openai_callback


st.set_page_config(page_title="Economy Analysis", page_icon="📈", layout="wide")

st.title("Economy Analysis with OpenBB:butterfly: & ChatGPT:robot_face:")


choice = st.selectbox(
    label = "Choose an Option based on today's Open Interest",
    options = ('Vanguard', 'Capital', 'BlackRock', 'Morningstar', 'Invesco', 'Fidelity', 'Goldman Sachs', 'Value Line', 'HSBC', 'PRBLX', 'SSAQX', 'USBOX')
)

dat = openbb.funds.load(choice)
cont = st.container()

with cont:
    @st.cache_data(experimental_allow_widgets=True)
    def data_stream():

        st.write("Choose a Dataset to load")

        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

        if 'data' not in st.session_state:
            st.session_state['data'] = openbb.funds.carbon(dat)

        if col1.button('Carbon Metrics'):
            st.session_state['data'] = openbb.funds.carbon(dat)

        if col2.button('Exclusion Policy'):
            st.session_state['data'] = openbb.funds.exclusion(dat)

        if col3.button('Historical Performance'):
            st.session_state['data'] = openbb.funds.historical(dat, start_date = '2020-01-01', end_date = '2023-06-31')

        if col4.button('Holdings'):
            st.session_state['data'] = openbb.funds.holdings(dat)

        if col5.button('Sector Data'):
            st.session_state['data'] = openbb.funds.sector(dat)

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
