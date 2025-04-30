import google.generativeai as genai
import requests
from deep_translator import GoogleTranslator

# 🔹 SET UP YOUR API KEYS HERE
GEMINI_API_KEY = "AIzaSyATGtYPoxV90YjfkZiXg8L5Cj1H6XtupXk"
GOOGLE_SEARCH_API_KEY = "AIzaSyBP8lUQs9UGpvAENcMQxDrgguIWm-cu1Wc"
GOOGLE_CSE_ID = "f1328f4e12f8f482a"

# 🔹 Configure Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# 🔹 Simple greetings and thank you patterns
GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
THANK_YOU_RESPONSES = ["thank you", "thanks", "thankyou", "thx", "appreciate it"]

# 🔹 Global conversation memory (used for context)
conversation_history = []


def search_university_info(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_SEARCH_API_KEY}&cx={GOOGLE_CSE_ID}"
    try:
        response = requests.get(url)
        data = response.json()
        results = []
        for item in data.get("items", []):
            title = item.get("title", "No title")
            link = item.get("link", "#")
            snippet = item.get("snippet", "No description available.")
            results.append(f"• {title}\n  Link: {link}\n  Info: {snippet}\n")
        return "\n".join(results) if results else "No relevant university information found."
    except requests.exceptions.RequestException as e:
        return f"Error fetching search results: {e}"


def translate_text(text, source_lang="auto", target_lang="en"):
    try:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception as e:
        return f"Translation error: {e}"


def chat_with_gemini(user_query, lang_code="en"):
    try:
        base_lang = lang_code.split("-")[0] if "-" in lang_code else lang_code

        # Translate user input to English
        user_query_en = translate_text(user_query, source_lang="auto", target_lang="en").strip().lower()

        # Append user message to conversation history
        conversation_history.append({"role": "user", "parts": [user_query_en]})

        # Predefined responses
        if any(greet in user_query_en for greet in GREETINGS):
            reply_en = "Hello! 😊 How can I help you with university-related queries today?"
        elif "how are you" in user_query_en:
            reply_en = "I'm doing well, thank you for asking! 😊 I'm here to help you with university-related questions."
        elif any(thank in user_query_en for thank in THANK_YOU_RESPONSES):
            reply_en = "You're welcome! 😊 Let me know if you need more help."
        elif len(user_query_en.split()) < 3:
            reply_en = "Could you provide more details? For example: 'What are the admission requirements for IIT Bombay?'"
        else:
            search_results = search_university_info(user_query_en)
            prompt = f"""
User Query: {user_query_en}

Here is some university-related information:
{search_results}

Please provide a clear, structured, and informative response based on the user's query.
"""
            model = genai.GenerativeModel("gemini-1.5-pro-latest")
            chat = model.start_chat(history=conversation_history)
            response = chat.send_message(prompt)
            reply_en = response.text if response else "Sorry, I couldn't fetch the information."

        # Append bot reply to memory
        conversation_history.append({"role": "model", "parts": [reply_en]})

        # Translate to original user language if needed
        if base_lang != "en":
            reply_translated = translate_text(reply_en, source_lang="en", target_lang=base_lang)
        else:
            reply_translated = reply_en

        return reply_translated

    except Exception as e:
        return f"Unexpected error: {e}"


def reset_memory():
    global conversation_history
    conversation_history.clear()
    return "Memory reset. Ready for a new session."
