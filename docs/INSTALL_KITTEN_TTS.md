# Install KittenTTS Provider

Install the TTS plugin with the KittenTTS provider into Business Assistant v2.

## Prerequisites

- Python 3.11+
- Business Assistant v2 project

## Steps

### 1. Add the plugin dependency

In `business-assistant-v2/pyproject.toml`, add:

```toml
[project]
dependencies = [
    ...,
    "business-assistant-tts-plugin",
]

[tool.uv.sources]
business-assistant-tts-plugin = { path = "D:/GIT/BenjaminKobjolke/business-assistant-tts-plugin", editable = true }
```

### 2. Install the KittenTTS wheel

```bash
pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl
```

### 3. Sync dependencies

```bash
cd business-assistant-v2
uv sync
```

### 4. Configure environment

Add to `.env` in `business-assistant-v2`:

```env
PLUGINS=...,business_assistant_tts
TTS_PROVIDER=kitten
TTS_VOICE=Jasper
```

### 5. Restart the bot

Full restart required (not restart.flag).

## Configuration

| Variable | Default | Description |
|---|---|---|
| `TTS_PROVIDER` | `kitten` | Set to `kitten` |
| `TTS_MODEL` | `KittenML/kitten-tts-mini-0.8` | Model name |
| `TTS_VOICE` | `Jasper` | Voice name (see below) |
| `TTS_SPEED` | `1.0` | Speech speed multiplier (0.5-2.0) |
| `TTS_OUTPUT_DIR` | `data/tts_output` | Directory for generated audio files |

## Available Voices

Bella, Jasper, Luna, Bruno, Rosie, Hugo, Kiki, Leo

## Language Support

English only. When audio mode is active, the AI will always respond in English.
