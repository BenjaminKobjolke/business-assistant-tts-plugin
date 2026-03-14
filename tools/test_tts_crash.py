"""Reproduce TTS crash with the text that caused it in production."""

import gc
import os

import numpy as np
import soundfile as sf

os.environ.setdefault("TTS_PROVIDER", "qwen3")
os.environ.setdefault("TTS_MODEL", "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice")
os.environ.setdefault("TTS_VOICE", "Vivian")
os.environ.setdefault("TTS_LANGUAGE", "English")

from business_assistant_tts.config import load_tts_settings
from business_assistant_tts.tts_service import _split_long_sentences

CRASH_TEXT = (
    "Klar. Frederic Ruth schreibt, dass eure App für die Gemeinde "
    "weiterhin sehr wertvoll ist. Er fragt, ob ihr eingeschränkte "
    "Nutzerrollen hinzufügen könnt. Gewünscht ist ein Redakteur, "
    "der nur Entwürfe erstellen darf. Außerdem möchte er eine "
    "Admin-Ebene, in der ihr solche Redakteure mit Passwort anlegen könnt."
)

OUTPUT_FILE = "test_crash_output.ogg"

settings = load_tts_settings()
if settings is None:
    print("TTS is disabled.")
    raise SystemExit(1)

print(f"Provider: {settings.provider}")
print(f"Model: {settings.model}")
print(f"Voice: {settings.voice}")
print(f"Language: {settings.language}")

# Load provider
if settings.provider == "qwen3":
    from business_assistant_tts.providers.qwen3 import Qwen3TTSProvider

    provider = Qwen3TTSProvider(settings.model, settings.language)
else:
    print("This test is for qwen3 provider")
    raise SystemExit(1)

# Split text
try:
    from wtpsplit import SaT

    splitter = SaT("sat-3l-sm")
    sentences = splitter.split(CRASH_TEXT)
    sentences = [s.strip() for s in sentences if s.strip()]
except ImportError:
    sentences = [CRASH_TEXT]

chunks = _split_long_sentences(sentences)
print(f"\nSplit into {len(chunks)} chunks:")
for i, chunk in enumerate(chunks):
    print(f"  [{i}] ({len(chunk)} chars): {chunk[:80]}...")

# Generate each chunk
audio_chunks = []
sample_rate = 0
for i, chunk in enumerate(chunks):
    print(f"\nGenerating chunk {i + 1}/{len(chunks)}...")
    try:
        import torch

        if torch.cuda.is_available():
            mem = torch.cuda.memory_allocated() / 1024 / 1024
            print(f"  GPU memory before: {mem:.0f} MB")

        audio, sample_rate = provider.generate(chunk, settings.voice, settings.speed)
        audio_chunks.append(audio)
        print(f"  OK — {len(audio)} samples")

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
            mem = torch.cuda.memory_allocated() / 1024 / 1024
            print(f"  GPU memory after cleanup: {mem:.0f} MB")
    except Exception as e:
        print(f"  FAILED: {e}")
        raise

# Concatenate
print(f"\nConcatenating {len(audio_chunks)} chunks...")
audio_data = np.concatenate(audio_chunks) if len(audio_chunks) > 1 else audio_chunks[0]
print(f"Total samples: {len(audio_data)}, sample rate: {sample_rate}")

# Write WAV first (soundfile OGG crashes on large audio), then convert to OGG
wav_file = OUTPUT_FILE.replace(".ogg", ".wav")
print(f"Writing WAV: {wav_file}")
sf.write(wav_file, audio_data, sample_rate)
print("WAV OK")

print("Converting to OGG...")
from pydub import AudioSegment

audio_seg = AudioSegment.from_wav(wav_file)
audio_seg.export(OUTPUT_FILE, format="ogg")
import os

os.unlink(wav_file)
print(f"Saved to {OUTPUT_FILE}")
