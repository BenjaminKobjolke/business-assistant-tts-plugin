@echo off
cd /d "%~dp0.."
set TTS_PROVIDER=qwen3
set TTS_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
set TTS_VOICE=Vivian
set TTS_LANGUAGE=English
uv run python tools/test_tts_crash.py
pause
