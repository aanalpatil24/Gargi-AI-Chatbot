## 🤖 Gargi AI Chatbot
This project is a full-stack, intelligent chatbot application. It features a simple, clean chat interface and is powered by Google Gemini's models.
It is built with a Flask backend providing an API, and a Streamlit frontend providing the user interface.

## Definition
Gargi is a web application that provides a conversational AI interface. Users can have a conversation with an AI assistant, which will respond intelligently. The chat history is maintained only for the current session and will be cleared if you close the browser tab or click "Clear Chat History".

## Tech Stack
<details>
  <Summary>Click on Tech Stack</Summary>
This project integrates several modern technologies to create a complete application:

### Backend (API Server):
Flask: A lightweight Python web framework used to create the REST API.
Gunicorn: A production-ready web server used to run the Flask app.

### Frontend (User Interface):
Streamlit: An open-source Python library used to build the web app interface.

### AI & NLP:
Google (Gemini): The core large language model (LLM) that generates the chatbot's intelligent responses.
Hugging Face transformers: Used for Natural Language Processing (NLP). Specifically, it runs a sentiment analysis model on the user's input to provide context to the AI.

### Utility Libraries:
requests: Used by Streamlit to communicate with the Flask API.
python-dotenv: Manages environment variables (like your API key) securely.

</details>

## Features
<details>
  <Summary>Click on Features</Summary>
  
1. Conversational AI: Have a back-and-forth conversation with an AI
   assistant.
2. Session-Only Memory: The chatbot remembers the context of your
   current conversation.
3. Clear Chat: A button in the sidebar allows you to clear the
   history and start fresh.
4. Light/Dark Mode Toggle: Built-in with Streamlit. Go to ☰ >
   App settings to change your theme.
5. Context-Aware AI: The backend uses Hugging Face for sentiment
   analysis to give the AI context about your "mood."
6. Scalable Backend: The Flask API is separate from the UI so that it can
   be deployed and scaled independently.
   
</details>

## Setup & Installation (Local)
<details>
  <Summary>Click on Setup & Installation</Summary>
  
1. Create a .env file:
You need a Gemini API key from Google AI Studio.
Go to Google AI Studio. Create a new API key.
Create a file named .env in the same directory as app.py.

GOOGLE_API_KEY='Your-Google-Key-Here'

2. Install Dependencies:
It is highly recommended to use a virtual environment.

3. Create a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

4. Install all required packages:
pip install -r requirements.txt

</details>

## How to Run (Localhost)
<details>
  <Summary>Click on How to Run</Summary>
You must run both servers in two separate terminals.

Terminal 1: Run the Flask API Server
python app.py
You should see output like:
Hugging Face sentiment model loaded.
* Running on http://127.....

Terminal 2: Run the Streamlit UI
streamlit run streamlit_app.py
Streamlit will open your browser to http://localhost:.... 
You can now start chatting with Gargi.
</details>
