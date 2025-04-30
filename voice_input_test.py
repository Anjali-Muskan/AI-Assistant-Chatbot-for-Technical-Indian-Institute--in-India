from voice_input import get_voice_input_lang

# Example: Test with Hindi (hi-IN), Tamil (ta-IN), Gujarati (gu-IN)
selected_lang = "hi-IN"  # Change to test other languages
user_query = get_voice_input_lang(selected_lang)
print("Recognized Voice Input:", user_query)
