import streamlit as st 
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS 
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback

st.set_page_config(page_title="PDF Analysis", page_icon="📈")

st.title("Analyze any PDF file with ChatGPT :robot_face:")
openai_key = st.secrets["OPENAI_KEY"]
upload_file = st.file_uploader("Load your own PDF file")

if upload_file is not None:
    pdf_reader = PdfReader(upload_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len
    )
    chunks = splitter.split_text(text)

    embeddings = OpenAIEmbeddings(openai_api_key = openai_key)

    knowledge_base = FAISS.from_texts(chunks, embeddings)

    query = st.text_input(
        label = "Any questions?",
        help = "Ask any question based on the loaded file"
    )

    if query:
        docs = knowledge_base.similarity_search(query)

        lang_model = OpenAI(
        openai_api_key = openai_key,
        temperature = 0,
        max_tokens = 300
        )
        chain = load_qa_chain(lang_model, chain_type = "stuff")

        with get_openai_callback() as cb:
            response = chain.run(input_documents = docs, question = query)
            
            st.sidebar.write("Your request costs: " + str(cb.total_cost) + "USD")
        st.write(response)