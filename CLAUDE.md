# Business Assistant TTS Plugin

## Project Overview
Text-to-speech plugin for Business Assistant v2. Converts AI text responses to voice audio files.

## Architecture
- Plugin system: registers tools via `register()` in `plugin.py`, following the business-assistant-v2 plugin pattern
- Provider pattern: `TTSProvider` protocol in `providers/base.py`, implementations in `providers/`
- Response processor: `tts_response_processor` hooks into handler.py's response pipeline
- Text sanitizer: strips markdown/symbols before TTS in `text_sanitizer.py`

## Key Files
- `src/business_assistant_tts/plugin.py` — Entry point, tool definitions
- `src/business_assistant_tts/tts_service.py` — Audio mode state, audio generation
- `src/business_assistant_tts/response_processor.py` — Response hook
- `src/business_assistant_tts/text_sanitizer.py` — Markdown/symbol stripping
- `src/business_assistant_tts/providers/kitten.py` — KittenTTS provider

## Coding Rules
- Follow rules from `D:\GIT\BenjaminKobjolke\claude-code\coding-rules\COMMON_RULES.md`
- Follow rules from `D:\GIT\BenjaminKobjolke\claude-code\coding-rules\PYTHON_RULES.md`
- Max 300 lines per file
- All constants in `constants.py`
- Frozen dataclasses for config
- Type hints on all public APIs
- pytest for tests

## Commands
- Install: `uv sync`
- Tests: `uv run pytest tests/ -v`
- Lint: `uv run ruff check src/ tests/`
- Format: `uv run ruff format src/ tests/`
