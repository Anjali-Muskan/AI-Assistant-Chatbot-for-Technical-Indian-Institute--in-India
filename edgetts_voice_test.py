import asyncio
import edge_tts
import pygame

async def speak_text(text, voice="hi-IN-SwaraNeural"):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save("output.mp3")

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# Run the async function
if __name__ == "__main__":
    text = "नमस्ते! मैं आपकी मदद कैसे कर सकती हूँ?"
    asyncio.run(speak_text(text))
