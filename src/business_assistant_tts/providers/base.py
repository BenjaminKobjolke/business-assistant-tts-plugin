"""Base protocol for TTS providers."""

from __future__ import annotations

from typing import Any, Protocol


class TTSProvider(Protocol):
    """Protocol for text-to-speech providers.

    Implementations must return a numpy-compatible audio array
    and its sample rate.
    """

    @property
    def supported_languages(self) -> tuple[str, ...]:
        """Return language codes this provider supports (e.g. ('en',))."""
        ...

    def generate(self, text: str, voice: str, speed: float = 1.0) -> tuple[Any, int]:
        """Generate audio from text.

        Args:
            text: The text to synthesize.
            voice: The voice name to use.
            speed: Speech speed multiplier (0.5–2.0).

        Returns:
            Tuple of (audio_data, sample_rate) where audio_data is a
            numpy array and sample_rate is in Hz.
        """
        ...
