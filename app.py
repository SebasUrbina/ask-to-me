import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
try:
  from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
  from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader, Settings

st.set_page_config(page_title="Chatea con el CV de Sebastián Urbina", page_icon="🤓", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key

Settings.chunk_size = 4096
Settings.chunk_overlap = 20

st.title("Custom GPT 🤓")
st.write("""
         ¡Hola! Muchas gracias por tu interés en conocerme. El siguiente BOT responde en función de mi base 
         de conocimiento que se generó en base a mi CV, en el contexto de la búsqueda de una oportunidad laboral en [BUDA](https://buda.com/).
        """)
st.info("Puedes saber más de mi en [Github](https://github.com/SebasUrbina) y [LinkedIn](https://www.linkedin.com/in/sebaurbina/)", icon="📃")
st.warning("Las respuestas pueden no ser del todo precisas.", icon="⚠️")
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", 
         "content": "Hola, un gusto, soy Sebastián Urbina"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Cargando información de Sebastián Urbina..."):
        reader = SimpleDirectoryReader(input_dir="./docs", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.0))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="context", verbose=True, system_prompt="Actua como una persona llamada Sebastián Urbina que responde preguntas en base a sus estudios, experiencia laboral y hobbies para una postulación a una empresa llamada Buda.")

if prompt := st.chat_input("Tu pregunta"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("Asistente"):
        with st.spinner("Pensando..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history