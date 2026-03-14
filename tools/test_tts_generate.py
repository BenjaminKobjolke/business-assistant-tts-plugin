"""Generate a test TTS audio file using the active provider from env vars."""

import soundfile as sf

from business_assistant_tts.config import load_tts_settings
from business_assistant_tts.constants import DEFAULT_TTS_PROVIDER

TEXT = "Hello, how may I assist you today?"
OUTPUT_FILE = "test_output.ogg"

settings = load_tts_settings()
if settings is None:
    print("TTS is disabled (TTS_PROVIDER is empty).")
    raise SystemExit(1)

print(f"Provider: {settings.provider}")
print(f"Model: {settings.model}")
print(f"Voice: {settings.voice}")

if settings.provider == "kitten":
    from business_assistant_tts.providers.kitten import KittenTTSProvider

    provider = KittenTTSProvider(settings.model)
elif settings.provider == "qwen3":
    from business_assistant_tts.providers.qwen3 import Qwen3TTSProvider

    provider = Qwen3TTSProvider(settings.model, settings.language)
    print(f"Language: {settings.language}")
else:
    print(f"Unknown provider: {settings.provider}")
    raise SystemExit(1)

print(f'Generating audio: "{TEXT}" (voice={settings.voice})')
audio, sample_rate = provider.generate(TEXT, settings.voice, settings.speed)

sf.write(OUTPUT_FILE, audio, sample_rate, format="OGG", subtype="VORBIS")
print(f"Saved to {OUTPUT_FILE}")
