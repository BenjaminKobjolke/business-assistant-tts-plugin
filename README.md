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
| `TTS_PROVIDER` | No | `kitten` | TTS provider name (`kitten` or `qwen3`). Set empty to disable. |
| `TTS_MODEL` | No | `KittenML/kitten-tts-mini-0.8` | Model name/path |
| `TTS_VOICE` | No | `Jasper` | Voice name |
| `TTS_OUTPUT_DIR` | No | `data/tts_output` | Temp directory for generated audio |
| `TTS_SPEED` | No | `1.0` | Speech speed multiplier (0.5–2.0) |
| `TTS_LANGUAGE` | No | `English` | Language for TTS synthesis (Qwen3 only) |

### Available KittenTTS Voices

Bella, Jasper, Luna, Bruno, Rosie, Hugo, Kiki, Leo

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
- `kittentts` — KittenTTS engine (installed separately via wheel)
- `qwen-tts` — Qwen3-TTS engine (optional, install via `tools/install_qwen3.bat`)
