import streamlit as st
from chatbot_core import get_response  # replace with your real function
from gtts import gTTS
import pygame
import tempfile
import os

# Set page config
st.set_page_config(page_title="University Chatbot", layout="wide")

st.title("🎓 AI-powered University Assistance Chatbot")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "mute" not in st.session_state:
    st.session_state.mute = False

# Sidebar controls
st.sidebar.title("Settings")
language = st.sidebar.selectbox("Choose Language", ["en", "hi", "ta", "te", "bn"])
st.session_state.mute = st.sidebar.checkbox("🔇 Mute Bot Voice", value=False)

# Chat display
for i, (user_msg, bot_msg) in enumerate(st.session_state.history):
    st.chat_message("user", avatar="👤").write(user_msg)
    st.chat_message("bot", avatar="🤖").write(bot_msg)

# User input
user_input = st.chat_input("Type your question here...")

if user_input:
    response = get_response(user_input, language)  # Modify based on your logic
    st.session_state.history.append((user_input, response))

    # Display the new message
    st.chat_message("user", avatar="👤").write(user_input)
    st.chat_message("bot", avatar="🤖").write(response)

    # Voice output
    if not st.session_state.mute:
        try:
            tts = gTTS(text=response, lang=language)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                pygame.mixer.init()
                pygame.mixer.music.load(fp.name)
                pygame.mixer.music.play()
        except Exception as e:
            st.error(f"Voice error: {e}")
