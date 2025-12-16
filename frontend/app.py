import streamlit as st
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

url = f"https://youtube-rag-alisher-de24.azurewebsites.net/chat?code={os.getenv('FUNCTION_APP_API')}"

st.set_page_config(page_title="YouTube RAG Bot", page_icon="🤖")
st.title("🤖 YouTube RAG Bot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about Data Engineering..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(url, json={"prompt": prompt})

                if response.status_code == 200:
                    try:
                        data = response.json()
                        answer_text = data.get("response", "Error: No 'response' key")
                        st.markdown(answer_text)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer_text}
                        )
                    except json.JSONDecodeError:
                        st.error("Incorrect format: not JSON!")
                        st.code(response.text)
                else:
                    st.error(f"Server error: {response.status_code}")
                    st.write(f"URL: `{url}`")
                    st.write("Server response:")
                    st.code(response.text)

            except Exception as e:
                st.error(f"Connection error: {str(e)}")
