import sys
import os
sys.path.append("..")

import streamlit as st
from streamlit.web import cli as stcli
from streamlit import runtime
import datetime as dt
import time
runtime.exists()


# from lib.llm_api_response import get_llm_api_response
# from lib.postgres_setup import upload_to_postgres
from lib.vector_db_setup import get_texts


assistant_avatar = "./icons/assistant_icon.jpg"


### STREAMLIT APP ###


st.set_page_config(
    page_title='Welcome to Open Innovation AI',
    page_icon="../icons/assistant_icon.jpg"
)
with st.expander('RAG details'):
    st.markdown("<h6 style='text-align: right; color: grey;'>Built by Eugene Chernov for <a href='https://openinnovation.ai/'>Open Innovation AI</a></h6>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: left; color:red;'>Version: v0.1 </div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: left; color:red;'>Model: RAG </div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: left; color:red;'>Vector store: chromadb </div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: left; color:red;'>Base model: llama2-7b </div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: left; color:red;'>Finetuning: None </div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: left; color:red;'>Embedding func: --HIDDEN-- </div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: left; color:red;'>GPU: nvidia-A100-40GB </div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: left; color:red;'>Generation temperature: 0.1 </div>", unsafe_allow_html=True)
st.title("RAG chatbot (Open Innovation AI interview task)")

# name_input_container = st.empty()
name = st.text_input("Hi! What's your name?", max_chars=20)
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = ""
if 'start_chat' not in st.session_state:
    st.session_state.start_chat = False

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file and st.session_state.uploaded_file_name == "": # check the file
    st.session_state.uploaded_file_name = f"{name}_{dt.datetime.now().strftime('%Y-%m-%d')}.pdf"
    with open(f'upload/{st.session_state.uploaded_file_name}', 'wb') as f: # save the file
        f.write(uploaded_file.getbuffer())
        
    ### UPLOAD FILE TO CHROMA ###
    try:
        with st.spinner('Preprocessing your data⏳'):
            get_texts(
                file_name="upload/ML Questions.pdf",
                collection_name=f'{name}_{st.session_state.uploaded_file_name}'
            )
        st.write("File successfully uploaded")
        st.session_state.file_uploaded = True
        st.session_state.start_chat = True
    except:
        st.write("Something went wrong while file uploading. Please try again later.")
    finally:
        os.remove(f"upload/{st.session_state.uploaded_file_name}")

def main():
    if st.session_state.start_chat:
        # Start chat history
        if "messages" not in st.session_state.keys():
            # Initial message
            welcome_message = f"Hello {name}! My name is Joseph from Open Innovations AI. I'm a chat-bot and I'm here to assist you with your questions."
            st.session_state.messages = [{"role": "assistant", "content": welcome_message, "avatar": assistant_avatar}]
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"I see that you uploaded file '{uploaded_file.name}'. What are you looking for?",
                "avatar": assistant_avatar
            })

        # Show messages
        for message in st.session_state.messages:
            if message["role"] == "assistant":
                with st.chat_message(message["role"], avatar=message.get("avatar")):
                    st.write(message["content"])
            else:
                with st.chat_message(message["role"], avatar=message.get("avatar")):
                    st.write(message["content"])
        
        # Get message from the user
        prompt = st.chat_input("Enter your question here")
        if prompt:    
            with st.chat_message(name="user"):
                st.write(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Response
            with st.chat_message(name="assistant", avatar=assistant_avatar):
                with st.spinner('Generating response...⏳'):
                    response = prompt + f"GEN TIME: XXX sec" # TEEEEEST
                    st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response, "avatar": assistant_avatar})


    


if __name__ == '__main__':
    if runtime.exists():
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())