import os
import logging
import json
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import google.generativeai as genai
from transformers import pipeline
from dotenv import load_dotenv

# --- 1. Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"status": "Gargi AI backend is live on Render!"})

# --- 2. Client Setup ---
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    logging.error("CRITICAL: GOOGLE_API_KEY is missing from .env file!")
else:
    genai.configure(api_key=API_KEY)
    logging.info("Google GenerativeAI configured successfully.")

# --- 3. NLP Setup ---
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
sentiment_analyzer = None
try:
    logging.info(f"Loading Hugging Face model: {SENTIMENT_MODEL}...")
    sentiment_analyzer = pipeline("sentiment-analysis", model=SENTIMENT_MODEL)
    logging.info("Hugging Face sentiment model loaded.")
except Exception as e:
    logging.error(f"Failed to load Hugging Face model: {e}")

# --- 4. Streaming Generator ---
def generate_stream(gemini_history, user_message, system_instruction):
    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction
        )

        # Start a chat session
        chat_session = model.start_chat(history=gemini_history)

        response_stream = chat_session.send_message(user_message, stream=True)

        for chunk in response_stream:
            if chunk.text:
                yield f"data: {json.dumps({'content': chunk.text})}\n\n"
        
        yield f"data: {json.dumps({'type': 'stop'})}\n\n"

    except Exception as e:
        logging.error(f"Stream error: {e}")
        error_msg = "Invalid Google GenerativeAI API Key" if "API_KEY" in str(e) else str(e)
        yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"

# --- 5. Main Endpoint ---
@app.route('/chat', methods=['POST'])
def chat():
    if not API_KEY:
        return jsonify({"error": "Server missing API Key"}), 503
        
    data = request.json
    user_msg = data.get("message")
    history = data.get("history", [])

    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    # --- A. Perform Sentiment Analysis ---
    sentiment = "unknown"
    if sentiment_analyzer:
        try:
            result = sentiment_analyzer(user_msg)
            sentiment = result[0]['label']
            logging.info(f"Sentiment analyzed as: {sentiment}")
        except Exception as e:
            logging.warning(f"Sentiment analysis failed: {e}")

    # --- B. Create Dynamic System Instruction ---
    # --- B. Create Dynamic System Instruction ---
    system_instruction = (
        f"Your name is strictly Gargi. You are a helpful AI assistant. "
        f"If asked who you are, you must only say you are Gargi, an AI assistant. "
        f"Never mention you are a Google or Gemini model. "
        f"The user's current sentiment seems to be: {sentiment}. "
        f"Adjust your tone accordingly."
    )

    # --- C. Convert History to Gemini Format ---
    gemini_history = []
    for msg in history:
        role = 'model' if msg['role'] == 'assistant' else 'user'
        gemini_history.append({'role': role, 'parts': [msg['content']]})

    # --- D. Start Streaming Response ---
    return Response(stream_with_context(generate_stream(
        gemini_history, 
        user_msg, 
        system_instruction
    )), mimetype='text/event-stream')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"Starting Gargi AI backend on port {port}")
    app.run(host="0.0.0.0", port=port)
