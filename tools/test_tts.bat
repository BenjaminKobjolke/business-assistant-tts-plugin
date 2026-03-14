@echo off
cd /d "%~dp0.."
uv run python tools/test_tts_generate.py
