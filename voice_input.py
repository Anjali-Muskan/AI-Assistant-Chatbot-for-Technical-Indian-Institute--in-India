import speech_recognition as sr

def get_voice_input_lang(lang_code="en-IN"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            return "Sorry, I didn't hear anything. Please try again."

    try:
        # Recognize voice with language-specific code like 'hi-IN'
        query = r.recognize_google(audio, language=lang_code)
        print(f"🗣️ Recognized voice input: {query}")
        return query
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return "Sorry, I couldn't understand the audio."
    except sr.RequestError as e:
        print(f"❌ Request error: {e}")
        return "Sorry, there was a problem with the speech recognition service."
