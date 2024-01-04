'''from dotenv import load_dotenv
import os
from llama_index.callbacks import LlamaDebugHandler, CallbackManager
import pinecone
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.chat_engine.types import ChatMode
from llama_index.indices.postprocessor import SentenceEmbeddingOptimizer
from llama_index.vector_stores import PineconeVectorStore
import streamlit as st

from node_postprocessors.duplicate_postprocessing import (DuplicateRemoverNodePostprocessor)

load_dotenv()

print("Streamlit")

llama_debug = LlamaDebugHandler(print_trace_on_end=True)
callback_manager = CallbackManager(handlers=[llama_debug])
service_context = ServiceContext.from_defaults(callback_manager=callback_manager)


@st.cache_resource(show_spinner=False)
def get_index() -> VectorStoreIndex:
    pinecone.init(
        api_key=os.environ["PINECONE_API_KEY"],
        environment=os.environ["PINECONE_ENVIRONMENT"],
    )

    pinecone_index = pinecone.Index(index_name="llamaindex-documentation-helper")
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store, service_context=service_context
    )


index = get_index()

if "chat_engine" not in st.session_state.keys():
    postprocessor = SentenceEmbeddingOptimizer(
        embed_model=service_context.embed_model,
        percentile_cutoff=0.5,
        threshold_cutoff=0.7,
    )

    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode=ChatMode.CONTEXT,
        verbose=True,
        node_postprocessors=[postprocessor, DuplicateRemoverNodePostprocessor()],
    )


st.set_page_config(
    page_title="Chat bot",
    page_icon="./UTK-logo.png",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

#col1, col2, col3 = st.columns([3, 6, 3])

#with col2:
#    st.image("./MARCI.jpg")

st.title("My Chatbot")

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ask me a question"
        }
    ]

if prompt := st.chat_input("Your Question"):
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(message=prompt)
            st.write(response.response)
            nodes = [node for node in response.source_nodes]
            for col, node, i in zip(st.columns(len(nodes)), nodes, range(len(nodes))):
                with col:
                    st.header(f"Source Node {i+1}: score= {node.score}")
                    st.write(node.text)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message)
'''