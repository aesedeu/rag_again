import streamlit as st
from streamlit.web import cli as stcli
from streamlit import runtime
runtime.exists()
import sys
# from lib.llm_api_response import get_llm_api_response
# from lib.postgres_setup import upload_to_postgres
import time
import click

assistant_avatar = "./icons/assistant_icon.jpg"

st.set_page_config(
    page_title='Welcome to Open Innovation AI',
    page_icon="../icons/assistant_icon.jpg"
)
st.title("RAG chatbot (Open Innovation AI interview task)")
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

name_input_container = st.empty()
name = st.text_input("Hi! What's your name?", max_chars=20)


def main():
    if name != "": # check the name
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file: # check the file
            with open(f'{uploaded_file.name}', 'wb') as f: # save the file
                f.write(uploaded_file.getbuffer())
            
            # Start chat history
            if "messages" not in st.session_state.keys():
                # Initial message
                welcome_message = f"Hello {name}! My name is Joseph from Open Innovations AI. I'm a chat-bot and I'm here to assist you with your questions. I see that you uploaded file '{uploaded_file.name}'. What are you looking for?"
                st.session_state.messages = [{"role": "assistant", "content": welcome_message, "avatar": assistant_avatar}]

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