import streamlit as st
import requests
import json
import logging

# --- Configuration ---
FLASK_API_URL = st.secrets.get("FLASK_API_URL", "https://gargi-backend-qkvg.onrender.com")

st.set_page_config(
    page_title="Gargi AI Chatbot",
    layout="centered"
)
st.title("🤖 Gargi AI")
st.caption("Your intelligent AI assistant.")
st.caption("Gargi can make mistakes. Please cross check for references.")
# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI Elements ---
# --- Custom CSS to fix input border ---
st.markdown(
    """
    <style>
    .stTextInput > div > div > input:focus {
        border-color: white !important;
        box-shadow: 0 0 0 2px white !important;
    }
    .stChatInput > div > div > textarea:focus {
        border-color: white !important;
        box-shadow: 0 0 0 2px white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Display prior messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# "Clear Chat" button
if st.button("Clear Chat History", type="secondary"):
    st.session_state.messages = []
    st.rerun()

# --- Chat Input Logic ---
if prompt := st.chat_input("What's on your mind?"):
    # 1. Add user message to local state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get streaming response from Flask API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            payload = {
                "message": prompt,
                "history": st.session_state.messages[:-1]
            }
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(
                f"{FLASK_API_URL}/chat", 
                json=payload, 
                headers=headers, 
                stream=True,
                timeout=180
            )
            
            response.raise_for_status()
            
            full_response = ""
            
            # Iterate over the streaming response
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        try:
                            data = json.loads(decoded_line[6:])
                            
                            if data.get("type") == "stop":
                                break
                            
                            if data.get("type") == "error":
                                st.error(f"Error from API: {data['content']}")
                                full_response = ""
                                st.session_state.messages.pop()
                                break

                            chunk = data.get("content", "")
                            full_response += chunk
                            message_placeholder.markdown(full_response + " ▌")
                        
                        except json.JSONDecodeError:
                            logging.warning(f"Failed to decode JSON from stream: {decoded_line}")
            
            message_placeholder.markdown(full_response)
            
            # Add final response to history
            if full_response:
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to the backend API. Is the Flask server running?")
            st.session_state.messages.pop()
        except requests.exceptions.HTTPError as e:
            st.error(f"Error from API: {e.response.status_code} - {e.response.text}")
            st.session_state.messages.pop()
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.session_state.messages.pop()
