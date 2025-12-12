# import streamlit as st
# import requests

# st.set_page_config(page_title="AI Youtuber", page_icon="🎥")
# st.title("🎥 The Youtuber RAG Bot")
# st.write("Ask any question about Data Engineering!")

# URL = "https://youtube-rag-alisher-de24.azurewebsites.net/api/chat"

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# if prompt := st.chat_input("Your Question:"):
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         with st.spinner("Generating answer..."):
#             try:
#                 payload = {"prompt": prompt}
#                 response = requests.post(URL, json=payload)

#                 if response.status_code == 200:
#                     data = response.json()
#                     bot_answer = data.get("response", "Error: Empty response")
#                     st.markdown(bot_answer)
#                     st.session_state.messages.append(
#                         {"role": "assistant", "content": bot_answer}
#                     )
#                 else:
#                     error_msg = f"Server Error: {response.status_code}"
#                     st.error(error_msg)
#                     st.session_state.messages.append(
#                         {"role": "assistant", "content": error_msg}
#                     )

#             except requests.exceptions.ConnectionError:
#                 error_msg = "Could not connect to Backend. Don't forget to run 'uvicorn backend.main:app'."
#                 st.error(error_msg)
#                 st.session_state.messages.append(
#                     {"role": "assistant", "content": error_msg}
#                 )


import streamlit as st
import requests
import json
import os

# --- SETTINGS ---
# Your Azure Function URL
API_URL = "https://youtube-rag-alisher-de24.azurewebsites.net/api/chat"

# Page config
st.set_page_config(page_title="YouTube RAG Bot", page_icon="🤖")
st.title("🤖 YouTube RAG Bot")

# --- CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT AREA ---
if prompt := st.chat_input("Ask a question about Data Engineering..."):

    # 1. Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Send request to Azure
    with st.chat_message("assistant"):
        with st.spinner("Thinking... (Waiting for Azure response)"):
            try:
                # Sending POST request
                response = requests.post(API_URL, json={"prompt": prompt})

                # --- DEBUG BLOCK (CRITICAL) ---
                if response.status_code == 200:
                    # Success case
                    try:
                        data = response.json()
                        answer_text = data.get(
                            "response", "Error: No 'response' key in JSON"
                        )
                        st.markdown(answer_text)
                        # Save to history
                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer_text}
                        )
                    except json.JSONDecodeError:
                        st.error("Error: Server returned invalid JSON!")
                        st.write("Raw response:")
                        st.code(response.text)
                else:
                    # Error case (404, 500, etc.)
                    st.error(f"Server Error: {response.status_code}")
                    st.write("Here is the raw error from Azure (Logic Error):")
                    st.code(response.text)
                # ------------------------------

            except Exception as e:
                st.error(f"Connection Error: {str(e)}")
