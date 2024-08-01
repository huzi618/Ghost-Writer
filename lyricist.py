__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.retrievers.self_query.chroma import ChromaTranslator

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains.query_constructor.base import StructuredQueryOutputParser,get_query_constructor_prompt

import streamlit as st
from modify import MODIFIED_CSS

from scraper import Corpus
from fields import METADATA_FIELD_INFO
from filters import ALLOWED_COMPARATORS,EXAMPLES
from prompts import CHAT_PROMPT_TEMPLATE

load_dotenv()

os.getenv('LANGCHAIN_TRACING_V2')
os.getenv('LANGCHAIN_ENDPOINT')
os.getenv('LANGCHAIN_API_KEY')
os.getenv('OPENAI_API_KEY')

artists=['Steven-wilson','Tamino','Ed-sheeran','Billie-eilish','Bob-dylan', 'Billy-joel', 'Neil-young', 'Pink-floyd', 'Marvin-gaye', 'Stevie-wonder', 'David-bowie','Bob-marley']
db=Corpus(artists=artists)

st.set_page_config(page_title="Ghost Writer: AI Lyricist", layout='centered',page_icon='assets/song-lyrics.ico')

def colored_box(content, color="#f0f0f0"):
    
    return f"""
    <div style="
        background-color: {color};
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
        color: black;
    ">
        {content}
    </div>
    """

def initialize():

    if 'initialized' not in st.session_state:

        st.session_state.vectorstore = db.vector_store

        st.session_state.llm = ChatOpenAI(model='gpt-4-turbo', temperature=1)
        st.session_state.query_llm = ChatOpenAI(model='gpt-4-turbo', temperature=0)

        document_content_description = "Lyrics of songs from different writers"

        constructor_prompt = get_query_constructor_prompt(
            document_content_description,
            METADATA_FIELD_INFO,
            allowed_comparators=ALLOWED_COMPARATORS,
            examples=EXAMPLES,
        )

        output_parser = StructuredQueryOutputParser.from_components()
        st.session_state.query_constructor = constructor_prompt | st.session_state.query_llm | output_parser

        st.session_state.retriever = SelfQueryRetriever(
            query_constructor=st.session_state.query_constructor,
            vectorstore=st.session_state.vectorstore,
            structured_query_translator=ChromaTranslator(),
            search_kwargs={'k': 5},
            verbose=True
        )
        
        

        st.session_state.rag_chain = ({"context": st.session_state.retriever, "question": RunnablePassthrough()}
                                        | CHAT_PROMPT_TEMPLATE
                                        | st.session_state.llm
                                        | StrOutputParser())

        temp_artists = [' '.join([str.capitalize(name) for name in artist.split('-')]) for artist in artists]
        st.session_state.available_artists = temp_artists
        st.session_state.initialized=True

def invoke_chain(query, chosen_artist):

    final_query = query + f". Write the lyrics using {chosen_artist}'s style of writing, Make sure they are original"
    response = st.session_state.rag_chain.invoke(final_query)
    return '\n'.join(response.split('\n'))


def gui():
    
    st.markdown(MODIFIED_CSS, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="centered-logo">
        <img src="https://raw.githubusercontent.com/huzi618/Ghost-Writer/main/assets/output-onlinepngtools.png" alt="Logo" width="800"> <!-- Adjust width as needed -->
    </div>
""", unsafe_allow_html=True)
    st.markdown("""
        <div class="centered-heading">
            <h2>Your AI Powered Lyricist</h2>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("my_form", border=False):

        text = st.text_area(
            label='Enter Text',
            value= "Describe Your Song!",
            label_visibility='hidden'
         )
        
        selected_artist=st.selectbox(label='Artists',index=None,placeholder="Choose Artist Style", options=st.session_state.available_artists, label_visibility='hidden')
        submitted = st.form_submit_button("Write!", use_container_width=True, type='primary')
        
        if submitted:
            with st.spinner("Writing Your Lyrics....."):
                result = invoke_chain(text, selected_artist)
                st.markdown(colored_box(result),unsafe_allow_html=True)
        
if __name__=='__main__':
    initialize()
    gui()

