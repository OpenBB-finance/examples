import streamlit as st 
from openbb_terminal.sdk import openbb
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.callbacks import get_openai_callback


st.set_page_config(
    page_title="OpenBB-GPT",
    page_icon=":butterfly::robot_face:",
)

st.title("Dashboard powered by OpenBB :butterfly: & ChatGPT :robot_face:")
ticker = st.selectbox(
    label = "Choose a dataset to load",
    options = (
        "anes96",
        "cancer",
        "ccard",
        "cancer_china",	
        "co2",	
        "committee",
        "copper",
        "cpunish",
        "danish_data",
        "elnino",
        "engel",
        "fair",
        "fertility",
        "grunfeld",
        "heart",
        "interest_inflation",
        "longley",
        "macrodata",
        "modechoice",
        "nile",
        "randhie",
        "scotland",
        "spector",
        "stackloss",
        "star98",
        "statecrim",
        "strikes",
        "sunspots",
        "wage_panel"
    )
)

uploaded_file = st.file_uploader("...Or load your own custom CSV dataset")
    

table_name = 'statesdb'
uri = "file:memory?cache=shared&mode=memory"
openai_key = st.secrets["OPENAI_KEY"]

@st.cache_data()
def load(ticker):
    df = openbb.econometrics.load(ticker)
    return df
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)
else:
    df = load(ticker)
    st.write(df)

query = st.text_input(
    label = "Any questions?",
    help = "Ask any question based on the loaded dataset")
conn = sqlite3.connect(uri, uri=True)
df.to_sql(table_name, conn, if_exists = 'replace', index = False)

db_eng = create_engine(
    url = 'sqlite:///file:memdb1?mode=memory&cache=shared',
    poolclass = StaticPool,
    creator = lambda: conn
)
db = SQLDatabase(engine = db_eng)

lang_model = OpenAI(
    openai_api_key = openai_key,
    temperature = 0,
    max_tokens = 300
)
db_chain = SQLDatabaseChain(llm = lang_model, database = db, verbose = True)


if query:
    with get_openai_callback() as cb:
        response = db_chain.run(query)
        st.sidebar.write("Your request costs: " + str(cb.total_cost) + "USD")
    st.write(response)

    