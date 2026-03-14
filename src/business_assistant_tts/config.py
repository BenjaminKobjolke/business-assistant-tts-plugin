"""TTS plugin configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .constants import (
    DEFAULT_TTS_MODEL,
    DEFAULT_TTS_OUTPUT_DIR,
    DEFAULT_TTS_PROVIDER,
    DEFAULT_TTS_SPEED,
    DEFAULT_TTS_VOICE,
    ENV_TTS_MODEL,
    ENV_TTS_OUTPUT_DIR,
    ENV_TTS_PROVIDER,
    ENV_TTS_SPEED,
    ENV_TTS_VOICE,
)


@dataclass(frozen=True)
class TTSSettings:
    """Immutable TTS configuration."""

    provider: str
    model: str
    voice: str
    output_dir: str
    speed: float


def load_tts_settings() -> TTSSettings | None:
    """Load TTS settings from environment variables.

    Returns None if TTS_PROVIDER is explicitly set to empty string,
    indicating the plugin should be disabled.
    """
    provider = os.getenv(ENV_TTS_PROVIDER, DEFAULT_TTS_PROVIDER)
    if not provider:
        return None

    return TTSSettings(
        provider=provider,
        model=os.getenv(ENV_TTS_MODEL, DEFAULT_TTS_MODEL),
        voice=os.getenv(ENV_TTS_VOICE, DEFAULT_TTS_VOICE),
        output_dir=os.getenv(ENV_TTS_OUTPUT_DIR, DEFAULT_TTS_OUTPUT_DIR),
        speed=float(os.getenv(ENV_TTS_SPEED, str(DEFAULT_TTS_SPEED))),
    )
