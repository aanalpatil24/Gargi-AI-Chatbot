import os
import json
import logging
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
from transformers import pipeline
from openai import OpenAI

# -------------------------------------------------------------------
# 🧩 CONFIGURATION
# -------------------------------------------------------------------
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
OPENAI_MODEL = "gpt-4-turbo"

# -------------------------------------------------------------------
# 🚀 FLASK INITIALIZATION
# -------------------------------------------------------------------
app = Flask(__name__)
CORS(app)
logging.info("✅ Flask app initialized with CORS enabled.")

# -------------------------------------------------------------------
# 🔑 OPENAI CLIENT INITIALIZATION
# -------------------------------------------------------------------
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")

if not api_key:
    logging.error("❌ OPENAI_API_KEY not found in .env file.")
    client = None
else:
    try:
        client = OpenAI(api_key=api_key)
        logging.info(f"✅ OpenAI client initialized for project={project_id or 'default'}")

        # Optional validation check
        try:
            client.models.list()
            logging.info("✅ OpenAI API key validated successfully.")
        except Exception as e:
            logging.warning(f"⚠️ Validation warning: {e}")

    except Exception as e:
        logging.error(f"❌ Failed to initialize OpenAI client: {e}")
        client = None

# -------------------------------------------------------------------
# 🧠 SENTIMENT ANALYZER (Hugging Face)
# -------------------------------------------------------------------
sentiment_analyzer = None
try:
    sentiment_analyzer = pipeline("sentiment-analysis", model=SENTIMENT_MODEL)
    logging.info("✅ Sentiment model loaded successfully.")
except Exception as e:
    logging.warning(f"⚠️ Could not load sentiment model: {e}")

# -------------------------------------------------------------------
# 💬 STREAMING FUNCTION
# -------------------------------------------------------------------
def generate_stream(openai_messages):
    """Streams responses from OpenAI in text/event-stream format."""
    try:
        stream = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=openai_messages,
            stream=True
        )

        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.get("content"):
                yield f"data: {json.dumps({'content': delta['content']})}\n\n"

        # Notify Streamlit frontend that stream has ended
        yield f"data: {json.dumps({'type': 'stop'})}\n\n"

    except Exception as e:
        logging.error(f"❌ AI stream failed: {e}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'content': 'AI stream failed. Please verify API credentials or internet connection.'})}\n\n"

# -------------------------------------------------------------------
# 💭 MAIN CHAT ENDPOINT
# -------------------------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({"error": "Server not initialized properly."}), 503

    data = request.get_json() or {}
    user_message = data.get("message")
    history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "No message provided."}), 400

    # Sentiment analysis
    sentiment = "unknown"
    if sentiment_analyzer:
        try:
            sentiment = sentiment_analyzer(user_message)[0]["label"]
            logging.info(f"🧠 Detected sentiment: {sentiment}")
        except Exception as e:
            logging.warning(f"⚠️ Sentiment analysis failed: {e}")

    # Construct OpenAI message history
    system_prompt = (
        f"You are Gargi, a helpful and empathetic AI assistant. "
        f"The user's sentiment appears to be {sentiment.lower()}."
    )

    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": user_message}
    ]

    logging.info(f"📤 Sending {len(messages)} messages to OpenAI...")

    try:
        return Response(
            stream_with_context(generate_stream(messages)),
            mimetype="text/event-stream"
        )
    except Exception as e:
        logging.error(f"❌ Error in /chat route: {e}", exc_info=True)
        return jsonify({"error": "Internal server error."}), 500

# -------------------------------------------------------------------
# 🏁 ENTRY POINT
# -------------------------------------------------------------------
if __name__ == "__main__":
    logging.info("🚀 Starting Gargi AI Flask backend...")
    app.run(host="0.0.0.0", port=5000)
