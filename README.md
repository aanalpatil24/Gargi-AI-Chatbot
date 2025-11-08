## 🤖 Gargi AI Powered Chatbot

This project is a full-stack, intelligent chatbot application. It features a simple, clean chat interface and is powered by OpenAI's GPT models.

It is built with a Python backend (Flask) providing an API, and a Python frontend (Streamlit) providing the user interface.

## 📜 Definition

Gargi is a web application that provides a conversational AI interface. Users can have a conversation with an AI assistant, which will respond intelligently. The chat history is maintained only for the current session and will be cleared if you close the browser tab or click "Clear Chat History".

## 🛠️ Tech Stack

This project integrates several modern technologies to create a complete application:

# ** Backend (API Server): **

Flask: A lightweight Python web framework used to create the REST API.

Gunicorn: A production-ready web server used to run the Flask app.

# ** Frontend (User Interface): **

Streamlit: An open-source Python library used to build the web app interface.

# ** AI & NLP: **

OpenAI (ChatGPT): The core large language model (LLM) that generates the chatbot's intelligent responses.

Hugging Face transformers: Used for Natural Language Processing (NLP). Specifically, it runs a sentiment analysis model on the user's input to provide context to the AI.

# ** Utility Libraries: **

requests: Used by Streamlit to communicate with the Flask API.

python-dotenv: Manages environment variables (like your API key) securely.

## ✨ Features

Conversational AI: Have a back-and-forth conversation with an AI assistant.

Session-Only Memory: The chatbot remembers the context of your current conversation.

Clear Chat: A button in the sidebar allows you to clear the history and start fresh.

Light/Dark Mode Toggle: Built-in with Streamlit. Go to ☰ > Settings in the app to change your theme.

Context-Aware AI: The backend uses Hugging Face for sentiment analysis to give the AI context about your "mood."

Scalable Backend: The Flask API is separate from the UI, so it can be deployed and scaled independently.

## 🛠️ Setup & Installation (Local)

1. Create a .env file

You still need your OpenAI API key. Create a file named .env in the same directory as app.py.

OPENAI_API_KEY='sk-YourSuperSecretApiKeyHere'


2. Install Dependencies

It is highly recommended to use a virtual environment.

3. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

4. Install all required packages
pip install -r requirements.txt


## 🚀 How to Run (Localhost)

You must run both servers in two separate terminals.

Terminal 1: Run the Flask API Server

python app.py


You should see output like:
Hugging Face sentiment model loaded.
* Running on http://127.0.0.1:5000

Terminal 2: Run the Streamlit UI

streamlit run streamlit_app.py


Streamlit will open your browser to http://localhost:8501. You can now start chatting with Gargi.

## 🌎 How to Deploy to the Internet (from Scratch)

This guide shows how to deploy your app for free using GitHub, Render (for the Flask API), and Streamlit Community Cloud (for the UI).

Step 0: Push Your Code to GitHub

Create a new repository on GitHub.

Add your files (app.py, streamlit_app.py, requirements.txt, README.md, .env).

IMPORTANT: Add .env to a .gitignore file so you don't expose your API key.

# .gitignore
.env
venv/
__pycache__/


Push your code to the new repository.

Step 1: Deploy the Flask Backend (API) on Render

Sign Up: Go to Render.com and create an account (you can sign in with your GitHub account).

New Web Service:

On your dashboard, click "New +" -> "Web Service".

Connect your GitHub account and select the repository you just created.

Settings:

Name: Give it a name (e.g., gargi-api). This will be part of your URL.

Root Directory: Leave this blank if app.py is in the main folder.

Environment: Select Python 3.

Build Command: pip install -r requirements.txt

Start Command: gunicorn app:app (This is why we added gunicorn!)

Add Environment Variable (Your API Key):

Go to the "Environment" tab for your new service.

Under "Secret Files", you can skip this, but under "Environment Variables":

Click "Add Environment Variable".

Key: OPENAI_API_KEY

Value: Paste your sk-YourSuperSecretApiKeyHere

Deploy:

Click "Create Web Service". Render will start building and deploying your API.

Once it's "Live", copy your new API's URL. It will look something like this:
https://gargi-api.onrender.com

Step 2: Deploy the Streamlit Frontend (UI) on Streamlit Cloud

Sign Up: Go to share.streamlit.io and create an account (you can sign in with your GitHub account).

New App:

Click "New app" from your workspace.

Repository: Select the same GitHub repository.

Branch: main (or your default branch).

Main file path: streamlit_app.py

Add Secret (Your API URL):

Click the "Advanced settings..." dropdown.

Go to the "Secrets" section.

Paste the following, replacing the URL with the one you got from Render in Step 1:

FLASK_API_URL = "[https://gargi-api.onrender.com/chat](https://gargi-api.onrender.com/chat)"


IMPORTANT: Make sure to add /chat to the end of your Render URL!

Click "Save".

Deploy:

Click "Deploy!". Streamlit will build your app.

In a minute or two, your app will be live and accessible to anyone on the internet! It's now fully deployed.