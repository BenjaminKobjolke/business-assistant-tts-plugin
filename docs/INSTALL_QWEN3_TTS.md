# Install Qwen3-TTS Provider

Install the TTS plugin with the Qwen3-TTS provider into Business Assistant v2.

## Prerequisites

- Python 3.11+
- NVIDIA GPU with CUDA support
- CUDA toolkit installed
- [SoX](http://sox.sourceforge.net/) installed and on PATH
- Business Assistant v2 project

## Steps

### 1. Add dependencies to main project

In `business-assistant-v2/pyproject.toml`, add to the `[project] dependencies` list:

```toml
[project]
dependencies = [
    ...,
    "business-assistant-tts-plugin",
    "qwen-tts",
    "huggingface-hub>=0.34,<1.0",
    "torch",
    "torchaudio",
]

[tool.uv.sources]
business-assistant-tts-plugin = { path = "D:/GIT/BenjaminKobjolke/business-assistant-tts-plugin", editable = true }
torch = { index = "pytorch-cu128" }
torchaudio = { index = "pytorch-cu128" }

[[tool.uv.index]]
name = "pytorch-cu128"
url = "https://download.pytorch.org/whl/cu128"
explicit = true
```

The `huggingface-hub` pin is required because `transformers` (pulled in by `qwen-tts`) requires `<1.0`.

The `torch` and `torchaudio` sources must point to the PyTorch CUDA index. Without this, `uv` installs the CPU-only version and the model runs on CPU (very slow). On startup, the plugin logs whether it is running on GPU or CPU.

### 2. Sync dependencies

```bash
cd business-assistant-v2
uv sync
```

### 3. Verify CUDA

```bash
cd business-assistant-v2
uv run python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Should print `True` and your GPU name (e.g. `NVIDIA GeForce RTX 3060`).

### 4. Configure environment

Add to `.env` in `business-assistant-v2`:

```env
PLUGINS=...,business_assistant_tts
TTS_PROVIDER=qwen3
TTS_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
TTS_VOICE=Vivian
TTS_LANGUAGE=English
```

### 5. Restart the bot

Full restart required (not restart.flag).

## Configuration

| Variable | Default | Description |
|---|---|---|
| `TTS_PROVIDER` | `kitten` | Set to `qwen3` |
| `TTS_MODEL` | `KittenML/kitten-tts-mini-0.8` | Set to `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice` (faster) or `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice` (higher quality) |
| `TTS_VOICE` | `Jasper` | Voice name (see below) |
| `TTS_SPEED` | `1.0` | Speech speed multiplier (0.5-2.0) |
| `TTS_LANGUAGE` | `English` | Language for synthesis (see below) |
| `TTS_OUTPUT_DIR` | `data/tts_output` | Directory for generated audio files |

## Available Models

| Model | Parameters | Quality (WER) | Speed |
|---|---|---|---|
| `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice` | 0.6B | 0.92 | Faster |
| `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice` | 1.7B | 0.77 | Slower |

## Available Voices

Vivian, Serena, Uncle_Fu, Dylan, Eric, Ryan, Aiden, Ono_Anna, Sohee

## Supported Languages

Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian

When audio mode is active, the AI may respond in the user's language if it is in the supported list.
