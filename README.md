# Business Assistant TTS Plugin

Text-to-speech plugin for [Business Assistant v2](https://github.com/BenjaminKobjolke/business-assistant-v2). Converts AI responses to voice audio using configurable TTS providers.

## Features

- Toggle audio mode per user ("audio mode on/off")
- Speech-optimized output: AI adapts responses for natural listening
- Text sanitizer strips markdown/symbols before TTS
- "Show me that as text" for one-time text fallback
- Optional "text + audio" mode
- Provider abstraction for easy TTS engine swapping

## Supported Providers

- **KittenTTS** (local, English only, no GPU required)
- **KittenTTS API** (HTTP server, English only, no local model loading) — requires [Kitten-TTS-Server](https://github.com/devnen/Kitten-TTS-Server)
- **Qwen3-TTS** (local, multilingual, requires CUDA GPU)

## Installation

1. Install the KittenTTS wheel:

```bash
pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl
```

2. Add to `business-assistant-v2/pyproject.toml`:

```toml
dependencies = [
    ...,
    "business-assistant-tts-plugin",
]

[tool.uv.sources]
business-assistant-tts-plugin = { path = "D:/GIT/BenjaminKobjolke/business-assistant-tts-plugin", editable = true }
```

3. Run `uv sync` in business-assistant-v2

4. Add to `.env`:

```env
PLUGINS=...,business_assistant_tts
TTS_PROVIDER=kitten
TTS_VOICE=Jasper
```

5. Restart the bot (full restart, not restart.flag)

### KittenTTS API Setup (optional)

Uses [Kitten-TTS-Server](https://github.com/devnen/Kitten-TTS-Server) as an HTTP backend instead of loading the model locally.

1. Install and start the Kitten-TTS-Server (default port 8005)

2. Update `.env`:

```env
TTS_PROVIDER=kitten_api
TTS_VOICE=expr-voice-5-m
TTS_OUTPUT_FORMAT=opus
```

3. Restart the bot. The plugin verifies the server is reachable on startup and exits with an error if not.

### Qwen3-TTS Setup (optional)

1. Add `qwen-tts` and `huggingface-hub` pin to `business-assistant-v2/pyproject.toml` dependencies:

```toml
"qwen-tts",
"huggingface-hub>=0.34,<1.0",
```

2. Run `uv sync` in business-assistant-v2

3. Update `.env` to use Qwen3:

```env
TTS_PROVIDER=qwen3
TTS_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
TTS_VOICE=Vivian
TTS_LANGUAGE=English
```

4. Restart the bot

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `TTS_PROVIDER` | No | `kitten` | TTS provider name (`kitten`, `kitten_api`, or `qwen3`). Set empty to disable. |
| `TTS_MODEL` | No | `KittenML/kitten-tts-mini-0.8` | Model name/path |
| `TTS_VOICE` | No | `Jasper` | Voice name |
| `TTS_OUTPUT_DIR` | No | `data/tts_output` | Temp directory for generated audio |
| `TTS_SPEED` | No | `1.0` | Speech speed multiplier (0.5–2.0) |
| `TTS_LANGUAGE` | No | `English` | Language for TTS synthesis (Qwen3 only) |
| `TTS_API_URL` | No | `http://localhost:8005` | KittenTTS API server URL (`kitten_api` only) |
| `TTS_OUTPUT_FORMAT` | No | `opus` | Audio output format: `opus`, `wav`, or `mp3` (`kitten_api` only) |

### Available KittenTTS Voices (local)

Bella, Jasper, Luna, Bruno, Rosie, Hugo, Kiki, Leo

### Available KittenTTS API Voices

expr-voice-2-m, expr-voice-2-f, expr-voice-3-m, expr-voice-3-f, expr-voice-4-m, expr-voice-4-f, expr-voice-5-m, expr-voice-5-f

### Available Qwen3-TTS Voices

Vivian, Serena, Uncle_Fu, Dylan, Eric, Ryan, Aiden, Ono_Anna, Sohee

### Supported Qwen3-TTS Languages

Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian

## Usage

- "audio mode on" — enables voice responses
- "audio mode off" — back to text
- "show me that as text" — get last response as formatted text (one-time)
- "toggle text with audio" — receive both text and audio

## Dependencies

- `soundfile` — WAV file writing
- `httpx` — HTTP client for KittenTTS API provider
- `kittentts` — KittenTTS engine (installed separately via wheel, local provider only)
- `qwen-tts` — Qwen3-TTS engine (optional, install via `tools/install_qwen3.bat`)
