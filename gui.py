import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from chatbot_core import chat_with_gemini, reset_memory, conversation_history
from gtts import gTTS
import pygame
import os
import tempfile
import threading
import speech_recognition as sr
import datetime
from recommender import recommend_institutes
import pandas as pd
import edge_tts
import asyncio
import re

# Load the sample dataset
institutions_df = pd.read_csv("sample_institutions.csv")

# Convert it to a list of dictionaries for easy iteration
institutions_data = institutions_df.to_dict(orient='records')
print("Sample data keys:", institutions_data[0].keys())

user_profile = {
    "location": "Maharashtra",
    "exam": "JEE Main",
    "category": "General"
}

# Initialize pygame
pygame.mixer.init()

LANGUAGE_NAMES = {
    'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu',
    'bn': 'Bengali', 'gu': 'Gujarati', 'mr': 'Marathi', 'kn': 'Kannada',
    'ml': 'Malayalam', 'pa': 'Punjabi','bho': 'Bhojpuri','mai': 'Maithili'
}
LANG_CODE_FROM_NAME = {v: k for k, v in LANGUAGE_NAMES.items()}

LANGUAGE_TO_EDGE_VOICE = {
    "English": "en-IN-NeerjaNeural",
    "Hindi": "hi-IN-SwaraNeural",
    "Tamil": "ta-IN-PallaviNeural",
    "Telugu": "te-IN-MohanNeural",
    "Gujarati": "gu-IN-DhwaniNeural",
    "Marathi": "mr-IN-AarohiNeural",
    "Bengali": "bn-IN-TanishaaNeural",
    "Bhojpuri": "hi-IN-SwaraNeural",
    "Maithili": "hi-IN-SwaraNeural"
    # Add more as needed
}

# Updated themes with more colorful options
THEMES = {
    "dark": {"bg": "#2C3E50", "fg": "#FFFFFF", "entry_bg": "#34495E",
             "button_bg": "#3498DB", "button_fg": "#FFFFFF",
             "accent_button_bg": "#E74C3C", "accent_button_fg": "#FFFFFF"},
    "light": {"bg": "#ECF0F1", "fg": "#2C3E50", "entry_bg": "#FFFFFF",
              "button_bg": "#3498DB", "button_fg": "#FFFFFF",
              "accent_button_bg": "#E74C3C", "accent_button_fg": "#FFFFFF"}
}

current_theme = "dark"
speech_enabled = True

from gtts import gTTS
from gtts.lang import tts_langs
from unidecode import unidecode
from hashlib import md5
import re

audio_cache = {}


def speak_text(text, lang_code='en'):
    if not speech_enabled:
        return

    try:
        clean_text = re.sub(r'[^\w\s.,!?]', '', text).strip()

        if lang_code != 'en':
            clean_text = transliterate_tricky_words(clean_text)

        phrases = re.split(r'(?<=[.?!])\s+', clean_text)

        audio_files = []

        # Pre-generate all TTS files first
        for phrase in phrases:
            phrase = phrase.strip()
            if not phrase:
                continue

            cache_key = f"{phrase}_{lang_code}"
            cache_filename = os.path.join(tempfile.gettempdir(), md5(cache_key.encode()).hexdigest() + ".mp3")

            if cache_key not in audio_cache or not os.path.exists(cache_filename):
                tts = gTTS(text=phrase, lang=lang_code)
                tts.save(cache_filename)
                audio_cache[cache_key] = cache_filename

            audio_files.append(cache_filename)

        # Play all generated audio smoothly
        for file in audio_files:
            if not speech_enabled:
                break

            pygame.mixer.music.load(file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if not speech_enabled:
                    pygame.mixer.music.stop()
                    break
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()

    except Exception as e:
        print("TTS Error:", e)


def transliterate_tricky_words(text):
    # Example transliteration: replace English names or places with phonetically better forms
    replacements = {
        "JEE": "जेईई",
        "AICTE": "एआईसीटीई",
        "NIRF": "एनआईआरएफ",
        "Maharashtra": "महाराष्ट्र",
        "Tamil Nadu": "तमिलनाडु",
        "Delhi": "दिल्ली",
    }

    for eng, native in replacements.items():
        text = text.replace(eng, native)

    return text


def split_into_sentences(text):
    """Split text into sentences for better TTS processing."""
    return re.split(r'(?<=[.!?])\s+', text)


def open_profile_window():
    def save_profile():
        user_profile["name"] = name_entry.get()
        user_profile["preferred_language"] = lang_var.get()
        user_profile["location"] = location_entry.get()
        user_profile["exam_scores"] = score_entry.get()
        user_profile["category"] = category_entry.get()
        profile_window.destroy()
        chat_area.insert(tk.END, f"👤 Profile saved for {user_profile['name']}\n\n")

    theme = THEMES[current_theme]
    profile_window = tk.Toplevel(root)
    profile_window.title("User Profile")
    profile_window.geometry("400x300")
    profile_window.configure(bg=theme["bg"])

    tk.Label(profile_window, text="Name:", bg=theme["bg"], fg=theme["fg"]).pack(pady=(10, 0))
    name_entry = tk.Entry(profile_window, bg=theme["entry_bg"], fg=theme["fg"])
    name_entry.pack(pady=(0, 5))

    tk.Label(profile_window, text="Preferred Language:", bg=theme["bg"], fg=theme["fg"]).pack()
    lang_var = tk.StringVar(value="English")
    lang_dropdown = ttk.Combobox(profile_window, textvariable=lang_var, state="readonly")
    lang_dropdown["values"] = list(LANG_CODE_FROM_NAME.keys())
    lang_dropdown.pack(pady=(0, 5))

    tk.Label(profile_window, text="Location:", bg=theme["bg"], fg=theme["fg"]).pack()
    location_entry = tk.Entry(profile_window, bg=theme["entry_bg"], fg=theme["fg"])
    location_entry.pack(pady=(0, 5))

    tk.Label(profile_window, text="Entrance Exam Score:", bg=theme["bg"], fg=theme["fg"]).pack()
    score_entry = tk.Entry(profile_window, bg=theme["entry_bg"], fg=theme["fg"])
    score_entry.pack(pady=(0, 5))

    tk.Label(profile_window, text="Category (optional):", bg=theme["bg"], fg=theme["fg"]).pack()
    category_entry = tk.Entry(profile_window, bg=theme["entry_bg"], fg=theme["fg"])
    category_entry.pack(pady=(0, 5))

    save_btn = tk.Button(profile_window, text="Save Profile", command=save_profile,
                         bg=theme["button_bg"], fg=theme["button_fg"])
    save_btn.pack(pady=10)


def recommend_institutions():
    try:
        user_score = int(user_profile["exam_scores"])
    except ValueError:
        chat_area.insert(tk.END, "⚠️ Please enter a valid numeric exam score in your profile.\n")
        return

    recommendations = []
    for inst in institutions_data:
        inst_state = inst.get("State", "").lower()
        inst_cutoff = int(inst.get("Min Cutoff Marks", 1000000))
        inst_category = inst.get("Category", "").lower()

        user_state = user_profile.get("location", "").lower()
        user_category = user_profile.get("category", "").lower()

        if (
                inst_state == user_state and
                user_score >= inst_cutoff and
                (inst_category == user_category or not user_category)
        ):
            msg = (
                f"🏫 {inst['Institute Name']} in {inst['City']}, {inst['State']} "
                f"- Apply by {inst['Application Deadline']}\n"
                f"   🔗 Website: {inst['Website']}\n"
            )
            recommendations.append(msg)

    if recommendations:
        chat_area.insert(tk.END, "🎯 Based on your profile, you can consider:\n")
        for rec in recommendations:
            chat_area.insert(tk.END, rec + "\n")
    else:
        chat_area.insert(tk.END, "❌ No matching institutions found based on your profile.\n")


def apply_theme():
    theme = THEMES[current_theme]
    root.configure(bg=theme["bg"])
    chat_area.configure(bg=theme["entry_bg"], fg=theme["fg"])
    entry.configure(bg=theme["entry_bg"], fg=theme["fg"], insertbackground=theme["fg"])
    context_display.configure(bg=theme["entry_bg"], fg=theme["fg"])
    bottom_frame.configure(bg=theme["bg"])

    # Apply colors to all buttons
    for widget in bottom_frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(bg=theme["button_bg"], fg=theme["button_fg"],
                             activebackground=theme["accent_button_bg"],
                             activeforeground=theme["button_fg"])


def voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            chat_area.insert(tk.END, "🎙️ Listening...\n")
            chat_area.see(tk.END)
            audio = recognizer.listen(source, timeout=5)
            user_input = recognizer.recognize_google(audio)
            entry.delete(0, tk.END)
            entry.insert(0, user_input)
            send_message()
        except Exception as e:
            chat_area.insert(tk.END, f"❌ Voice Error: {e}\n")


def speak_text_edge_tts(text, lang_name):
    if not speech_enabled:
        return

    def run():
        voice = LANGUAGE_TO_EDGE_VOICE.get(lang_name, "en-IN-NeerjaNeural")
        sentences = split_into_sentences(text)

        for sentence in sentences:
            if not speech_enabled:
                break
            if sentence.strip():  # Only process non-empty sentences
                asyncio.run(play_edge_tts_sentence(sentence, voice))

    threading.Thread(target=run).start()


async def play_edge_tts_sentence(text, voice):
    if not speech_enabled or not text.strip():
        return

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        filepath = f.name

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)

    pygame.mixer.init()
    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()

    # Wait for audio to finish playing
    while pygame.mixer.music.get_busy() and speech_enabled:
        await asyncio.sleep(0.1)

    # Stop playing if muted
    if not speech_enabled and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()


def send_message():
    user_input = entry.get().strip()
    if not user_input:
        return

    lang_code = LANG_CODE_FROM_NAME[language_var.get()]
    chat_area.insert(tk.END, f"🧑 You: {user_input}\n")
    chat_area.see(tk.END)
    entry.delete(0, tk.END)

    # Call generate_response with the user input and language code
    generate_response(user_input, lang_code)


def generate_response(user_input, lang_code):
    def fetch_and_type_response():
        # Show "Bot is typing..." placeholder
        typing_index = chat_area.index(tk.END)
        chat_area.insert(tk.END, "\n🤖 Bot is typing...\n")
        chat_area.see(tk.END)
        chat_area.update()

        # Get the response
        bot_response = chat_with_gemini(user_input, lang_code=lang_code)
        print("🔍 Gemini response:", bot_response)

        if not bot_response or bot_response.strip() == "":
            bot_response = "⚠️ I didn't understand that. Can you please rephrase?"

        # Remove the typing placeholder
        chat_area.delete(typing_index, tk.END)
        chat_area.insert(tk.END, "🤖 Bot: ")
        chat_area.see(tk.END)
        chat_area.update()

        # Use the full text for speech to avoid skipping
        full_response = bot_response.strip()
        selected_language_name = language_var.get()

        # Type the entire response first
        for char in full_response:
            chat_area.insert(tk.END, char)
            chat_area.see(tk.END)
            chat_area.update()
            root.after(10)  # Slightly faster typing speed

        # Then speak the full response
        if speech_enabled:
            if selected_language_name in LANGUAGE_TO_EDGE_VOICE:
                speak_text_edge_tts(full_response, selected_language_name)
            else:
                threading.Thread(target=lambda: speak_text(full_response,
                                                           LANG_CODE_FROM_NAME[selected_language_name])).start()

        chat_area.insert(tk.END, "\n\n")
        chat_area.see(tk.END)
        update_context_display()

    threading.Thread(target=fetch_and_type_response).start()


def update_context_display():
    context_display.config(state='normal')
    context_display.delete(1.0, tk.END)
    for i in range(0, len(conversation_history), 2):
        user_msg = conversation_history[i]["parts"][0] if i < len(conversation_history) else ""
        bot_msg = conversation_history[i + 1]["parts"][0] if i + 1 < len(conversation_history) else ""
        context_display.insert(tk.END, f"🧑 {user_msg}\n🤖 {bot_msg}\n\n")
    context_display.config(state='disabled')


def toggle_theme():
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    apply_theme()


def toggle_speech():
    global speech_enabled
    speech_enabled = not speech_enabled
    speech_btn.config(text="🔊 On" if speech_enabled else "🔇 Off")

    # Stop any currently playing audio when muted
    if not speech_enabled and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()


def reset_chat():
    reset_memory()
    chat_area.insert(tk.END, "🧹 Memory cleared.\n\n")
    update_context_display()


def save_chat():
    filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt")],
                                            title="Save Chat History")
    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Chat saved on: {timestamp}\n\n")
            f.write(chat_area.get("1.0", tk.END))
        chat_area.insert(tk.END, "✅ Chat saved successfully.\n")


def clear_chat():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    chat_area.delete(1.0, tk.END)
    context_display.config(state='normal')
    context_display.delete(1.0, tk.END)
    context_display.config(state='disabled')


root = tk.Tk()
root.title("University Chatbot")
root.geometry("850x650")
root.configure(bg=THEMES[current_theme]["bg"])

# Style configuration for ttk widgets
style = ttk.Style()
style.theme_use('clam')

context_display = scrolledtext.ScrolledText(root, height=8, state='disabled', wrap=tk.WORD)
context_display.pack(padx=10, pady=(10, 0), fill=tk.X)

chat_area = scrolledtext.ScrolledText(root, height=15, wrap=tk.WORD)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

bottom_frame = tk.Frame(root, bg=THEMES[current_theme]["bg"])
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

entry = tk.Entry(bottom_frame, font=("Arial", 12), width=50)
entry.grid(row=0, column=0, padx=5)

theme = THEMES[current_theme]

# Create buttons with colorful appearance
send_btn = tk.Button(bottom_frame, text="Send", command=send_message,
                     bg=theme["button_bg"], fg=theme["button_fg"])
send_btn.grid(row=0, column=1, padx=5)

voice_btn = tk.Button(bottom_frame, text="🎤", command=voice_input,
                      bg=theme["button_bg"], fg=theme["button_fg"])
voice_btn.grid(row=0, column=2, padx=5)

speech_btn = tk.Button(bottom_frame, text="🔊 On", command=toggle_speech,
                       bg=theme["button_bg"], fg=theme["button_fg"])
speech_btn.grid(row=0, column=3, padx=5)

theme_btn = tk.Button(bottom_frame, text="🌙 Theme", command=toggle_theme,
                      bg=theme["button_bg"], fg=theme["button_fg"])
theme_btn.grid(row=0, column=4, padx=5)

reset_btn = tk.Button(bottom_frame, text="🧹 Reset", command=reset_chat,
                      bg=theme["button_bg"], fg=theme["button_fg"])
reset_btn.grid(row=0, column=5, padx=5)

save_btn = tk.Button(bottom_frame, text="📝 Save", command=save_chat,
                     bg=theme["button_bg"], fg=theme["button_fg"])
save_btn.grid(row=0, column=6, padx=5)

clear_btn = tk.Button(bottom_frame, text="🧼 Clear", command=clear_chat,
                      bg=theme["button_bg"], fg=theme["button_fg"])
clear_btn.grid(row=0, column=7, padx=5)

profile_btn = tk.Button(bottom_frame, text="👤 Profile", command=open_profile_window,
                        bg=theme["accent_button_bg"], fg=theme["accent_button_fg"])
profile_btn.grid(row=0, column=9, padx=5)

recommend_btn = tk.Button(bottom_frame, text="🎯 Recommend", command=recommend_institutions,
                          bg=theme["accent_button_bg"], fg=theme["accent_button_fg"])
recommend_btn.grid(row=0, column=10, padx=5)

language_var = tk.StringVar()
language_dropdown = ttk.Combobox(bottom_frame, textvariable=language_var, state="readonly")
language_dropdown["values"] = list(LANG_CODE_FROM_NAME.keys())
language_dropdown.grid(row=0, column=8, padx=5)
language_dropdown.set("English")

apply_theme()
update_context_display()
root.mainloop()

