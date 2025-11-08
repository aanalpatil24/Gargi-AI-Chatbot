import streamlit as st
import requests
import json
import logging

# ---------------------------
# 🌐 Backend API Configuration
# ---------------------------
FLASK_API_URL = st.secrets.get("FLASK_API_URL", "http://127.0.0.1:5000")

# ---------------------------
# 🧩 Page Setup
# ---------------------------
st.set_page_config(
    page_title="Gargi AI Chatbot",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------
# 🎨 Custom CSS Styling (clean ChatGPT-like UI)
# ---------------------------
st.markdown("""
    <style>
        html, body {
            background-color: #ffffff;
            color: #000000;
            margin: 0;
            padding: 0;
        }

        .main {
            max-width: 750px;
            margin: auto;
            background-color: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 0 15px rgba(0,0,0,0.05);
        }

        .stChatInput {
            background-color: #f9f9f9 !important;
            border-radius: 12px !important;
            border: 1px solid #ddd !important;
        }

        .stChatMessage {
            border-radius: 10px;
            padding: 0.8rem;
            margin: 0.3rem 0;
            line-height: 1.5;
        }

        .stChatMessage[data-testid="stChatMessageUser"] {
            background-color: #f1f1f1;
            color: #000;
            text-align: right;
        }

        .stChatMessage[data-testid="stChatMessageAssistant"] {
            background-color: #000;
            color: #fff;
        }

        .block-container {
            padding-top: 1.5rem;
        }

        .title {
            text-align: center;
            font-size: 2.3rem;
            font-weight: 700;
            color: #000;
            margin-top: 1.2rem;      /* Added for visibility */
            margin-bottom: 0.6rem;   /* Fixed margin value */
        }

        .caption {
            text-align: center;
            color: #666;
            font-size: 1rem;
            margin-bottom: 2rem;
        }

        /* Make chat messages narrower and visually balanced */
        [data-testid="stChatMessage"] > div {
            max-width: 80%;
        }

        /* Center clear chat button */
        .stButton > button {
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            background-color: #000 !important;
            color: white !important;
            border: none;
        }

        .stButton > button:hover {
            background-color: #333 !important;
        }

    </style>
""", unsafe_allow_html=True)

# ---------------------------
# 🧠 Title and Caption
# ---------------------------
st.markdown('<div class="title">🤖 Gargi AI</div>', unsafe_allow_html=True)
st.markdown('<div class="caption">Your Personal AI Assistant — powered by Flask & Streamlit</div>', unsafe_allow_html=True)

# ---------------------------
# 💬 Initialize Chat History
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------
# 🧹 Clear Chat Button
# ---------------------------
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------
# ✍️ Chat Input and Stream Response
# ---------------------------
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        try:
            payload = {
                "message": prompt,
                "history": st.session_state.messages[:-1]
            }

            response = requests.post(
                f"{FLASK_API_URL}/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=True,
                timeout=180
            )
            response.raise_for_status()

            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        try:
                            data = json.loads(decoded[6:])
                            if data.get("type") == "stop":
                                break
                            if data.get("type") == "error":
                                st.error(data["content"])
                                break
                            chunk = data.get("content", "")
                            full_response += chunk
                            message_placeholder.markdown(full_response + " ▌")
                        except json.JSONDecodeError:
                            logging.warning(f"JSON decode failed: {decoded}")

            message_placeholder.markdown(full_response)
            if full_response:
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.exceptions.ConnectionError:
            st.error("❌ Unable to connect to Flask backend. Make sure it's running.")
