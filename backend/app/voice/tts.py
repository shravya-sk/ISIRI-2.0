import edge_tts
import pygame
import tempfile
import os

VOICE = "en-US-AriaNeural"

async def speak(text):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        filename = f.name

    communicate = edge_tts.Communicate(text=text, voice=VOICE)
    await communicate.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)

    pygame.mixer.quit()
    os.remove(filename)