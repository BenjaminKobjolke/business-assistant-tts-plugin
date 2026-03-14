"""KittenTTS provider implementation."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

SAMPLE_RATE = 24000


class KittenTTSProvider:
    """TTS provider using KittenTTS local model (English only, CPU)."""

    def __init__(self, model_name: str) -> None:
        from kittentts import KittenTTS

        self._model = KittenTTS(model_name)
        logger.info("KittenTTS model loaded: %s", model_name)

    @property
    def supported_languages(self) -> tuple[str, ...]:
        """KittenTTS only supports English."""
        return ("en",)

    def generate(self, text: str, voice: str, speed: float = 1.0) -> tuple[Any, int]:
        """Generate audio using KittenTTS.

        Args:
            text: The text to synthesize.
            voice: Voice name (Bella, Jasper, Luna, Bruno, Rosie, Hugo, Kiki, Leo).
            speed: Speech speed multiplier (0.5–2.0).

        Returns:
            Tuple of (audio_numpy_array, sample_rate).
        """
        audio = self._model.generate(text, voice=voice, speed=speed)
        return audio, SAMPLE_RATE
