import streamlit as st
import requests

st.set_page_config(page_title="AI Youtuber", page_icon="🎥")
st.title("🎥 The Youtuber RAG Bot")
st.write("Ask any question about Data Engineering!")

API_URL = "http://127.0.0.1:8000/chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Your Question:"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating answer..."):
            try:
                payload = {"prompt": prompt}
                response = requests.post(API_URL, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    bot_answer = data.get("response", "Error: Empty response")
                    st.markdown(bot_answer)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": bot_answer}
                    )
                else:
                    error_msg = f"Server Error: {response.status_code}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

            except requests.exceptions.ConnectionError:
                error_msg = "Could not connect to Backend. Don't forget to run 'uvicorn backend.main:app'."
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
