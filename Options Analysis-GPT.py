import pandas as pd
from openbb_terminal.sdk import openbb
import streamlit as st
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.callbacks import get_openai_callback


st.set_page_config(page_title="Options Analysis", page_icon="📈")

st.title("Options Analysis with OpenBB:butterfly: & ChatGPT:robot_face:")

unu_df,unu_ts = openbb.stocks.options.unu(limit = 500)
unu_df = unu_df.sort_values(by = 'Vol/OI', ascending = False)

table_name = 'statesdb'
uri = "file:memory?cache=shared&mode=memory"
openai_key = st.secrets["OPENAI_KEY"]

choice = st.selectbox(
    label = "Choose an Option based on today's Open Interest",
    options = (unu_df['Ticker'])
)

@st.cache_data()
def load(choice):
    df = openbb.stocks.options.info(choice)
    return df

    
df = load(choice)
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
    temperature = 0.9,
    max_tokens = 300
)
db_chain = SQLDatabaseChain(llm = lang_model, database = db, verbose = True)


if query:
    with get_openai_callback() as cb:
        response = db_chain.run(query)
        st.sidebar.write("Your request costs: " + str(cb.total_cost) + "USD")
    st.write(response)
