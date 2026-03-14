"""Qwen3-TTS provider implementation (multilingual, GPU)."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

SPEED_SLOW_THRESHOLD = 0.8
SPEED_FAST_THRESHOLD = 1.2


def _speed_to_instruct(speed: float) -> str:
    """Convert a speed multiplier to a natural language instruction.

    Qwen3-TTS has no direct speed parameter, so we use the instruct
    field to request speaking pace changes.
    """
    if speed < SPEED_SLOW_THRESHOLD:
        return "Speak slowly and deliberately."
    if speed > SPEED_FAST_THRESHOLD:
        return "Speak at a faster pace."
    return ""


class Qwen3TTSProvider:
    """TTS provider using Qwen3-TTS (multilingual, requires CUDA GPU)."""

    def __init__(self, model_name: str, language: str) -> None:
        import torch
        from qwen_tts import Qwen3TTSModel

        device_map = "cuda:0" if torch.cuda.is_available() else "cpu"
        self._model = Qwen3TTSModel.from_pretrained(model_name, device_map=device_map)
        self._language = language
        device = getattr(self._model, "device", "unknown")
        if str(device) == "cpu":
            logger.warning("Qwen3-TTS running on CPU — inference will be slow")
        else:
            logger.info("Qwen3-TTS running on %s", device)
        logger.info("Qwen3-TTS model loaded: %s (language=%s)", model_name, language)

    @property
    def supported_languages(self) -> tuple[str, ...]:
        """Qwen3-TTS supports 10 languages."""
        return ("zh", "en", "ja", "ko", "de", "fr", "ru", "pt", "es", "it")

    def generate(self, text: str, voice: str, speed: float = 1.0) -> tuple[Any, int]:
        """Generate audio using Qwen3-TTS CustomVoice mode.

        Args:
            text: The text to synthesize.
            voice: Speaker name (Vivian, Serena, Uncle_Fu, Dylan, Eric,
                   Ryan, Aiden, Ono_Anna, Sohee).
            speed: Speech speed multiplier (mapped to instruct text).

        Returns:
            Tuple of (audio_numpy_array, sample_rate).
        """
        instruct = _speed_to_instruct(speed)
        wavs, sample_rate = self._model.generate_custom_voice(
            text=text,
            language=self._language,
            speaker=voice,
            instruct=instruct,
            max_new_tokens=2048,
        )
        return wavs[0], sample_rate
