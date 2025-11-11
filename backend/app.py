import os
import logging
import json
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv

# --- 1. Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
CORS(app)

app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["DEBUG"] = True


@app.route("/")
def home():
    return jsonify({"status": "Gargi AI backend live on Render!"})

@app.route("/favicon.ico")
def favicon():
    return "", 204

# --- 2. Deferred (Lazy) Imports ---
def get_genai_client():
    import google.generativeai as genai
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logging.error("CRITICAL: GOOGLE_API_KEY missing!")
        raise ValueError("GOOGLE_API_KEY not found in environment.")
    genai.configure(api_key=api_key)
    logging.info("Google GenerativeAI configured successfully.")
    return genai

def get_sentiment_pipeline():
    try:
        from transformers import pipeline
        logging.info("Loading Hugging Face sentiment model lazily...")
        return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    except Exception as e:
        logging.warning(f"Failed to load sentiment model: {e}")
        return None

sentiment_analyzer = None

# --- 3. Streaming Generator ---
def generate_stream(gemini_history, user_message, system_instruction):
    try:
        genai = get_genai_client()
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction
        )

        chat_session = model.start_chat(history=gemini_history)
        response_stream = chat_session.send_message(user_message, stream=True)

        for chunk in response_stream:
            if chunk.text:
                yield f"data: {json.dumps({'content': chunk.text})}\n\n"
        
        yield f"data: {json.dumps({'type': 'stop'})}\n\n"

    except Exception as e:
        logging.error(f"Stream error: {e}")
        err = "Invalid Google GenerativeAI API Key" if "API_KEY" in str(e) else str(e)
        yield f"data: {json.dumps({'type': 'error', 'content': err})}\n\n"

# --- 4. Main Endpoint ---
@app.route("/chat", methods=["POST"]) 
def chat():
    global sentiment_analyzer
    try:
      data = request.json or {}
      user_msg = data.get("message")
      history = data.get("history", [])

      if not user_msg:
        return jsonify({"error": "No message provided"}), 400

      # --- A. Sentiment Analysis (lazy load) ---
      sentiment = "unknown"
      if sentiment_analyzer is None:
        sentiment_analyzer = get_sentiment_pipeline()

      if sentiment_analyzer:
        try:
            result = sentiment_analyzer(user_msg)
            sentiment = result[0]['label']
            logging.info(f"Sentiment analyzed as: {sentiment}")
        except Exception as e:
            logging.warning(f"Sentiment analysis failed: {e}")

      # --- B. System Instruction ---
      system_instruction = (
        f"Your name is Gargi, a helpful AI assistant. "
        f"Never reveal model origin. "
        f"User sentiment seems {sentiment}. Adjust tone accordingly."
      )

      # --- C. Format History for Gemini ---
      gemini_history = [
        {'role': 'model' if m['role'] == 'assistant' else 'user', 'parts': [m['content']]}
        for m in history
       ]

       # --- D. Stream Response ---
      return Response(stream_with_context(generate_stream(
        gemini_history,
        user_msg,
        system_instruction
      )), mimetype='text/event-stream')
    
    except Exception as e:
     logging.error(f"Chat route error: {e}", exc_info=True)
     return jsonify({"error": str(e)}), 500

# --- 5. Entrypoint ---
if __name__ == "__main__":
 port = int(os.environ.get("PORT", 8080))
 logging.info(f"Starting Flask app on 0.0.0.0:{port}")
 app.run(host="0.0.0.0", port=port)
