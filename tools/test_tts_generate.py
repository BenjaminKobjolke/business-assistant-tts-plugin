"""Generate a test TTS audio file to verify the provider works."""

import os

import soundfile as sf
from kittentts import KittenTTS

MODEL = os.getenv("TTS_MODEL", "KittenML/kitten-tts-mini-0.8")
VOICE = os.getenv("TTS_VOICE", "Jasper")
TEXT = "Hello, how may I assist you today?"
OUTPUT_FILE = "test_output.wav"

print(f"Loading model: {MODEL}")
model = KittenTTS(MODEL)

print(f"Generating audio: \"{TEXT}\" (voice={VOICE})")
audio = model.generate(TEXT, voice=VOICE)

sf.write(OUTPUT_FILE, audio, 24000)
print(f"Saved to {OUTPUT_FILE}")
