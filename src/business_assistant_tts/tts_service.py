"""TTS service — orchestrates audio generation and user state."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

import soundfile as sf

from .config import TTSSettings
from .constants import (
    LOG_AUDIO_GENERATED,
    LOG_AUDIO_GENERATION_FAILED,
    RESP_AUDIO_ALREADY_OFF,
    RESP_AUDIO_ALREADY_ON,
    RESP_AUDIO_DISABLED,
    RESP_AUDIO_ENABLED,
    RESP_SKIP_ONCE,
    RESP_TEXT_WITH_AUDIO_OFF,
    RESP_TEXT_WITH_AUDIO_ON,
)
from .providers.base import TTSProvider

logger = logging.getLogger(__name__)


class TTSService:
    """Manages per-user audio mode state and generates audio files."""

    def __init__(self, provider: TTSProvider, settings: TTSSettings) -> None:
        self._provider = provider
        self._settings = settings
        self._audio_users: set[str] = set()
        self._text_with_audio_users: set[str] = set()
        self._skip_once_users: set[str] = set()

    def enable_audio_mode(self, user_id: str) -> str:
        """Enable audio mode for a user."""
        if user_id in self._audio_users:
            return RESP_AUDIO_ALREADY_ON
        self._audio_users.add(user_id)
        return RESP_AUDIO_ENABLED

    def disable_audio_mode(self, user_id: str) -> str:
        """Disable audio mode for a user."""
        if user_id not in self._audio_users:
            return RESP_AUDIO_ALREADY_OFF
        self._audio_users.discard(user_id)
        self._text_with_audio_users.discard(user_id)
        self._skip_once_users.discard(user_id)
        return RESP_AUDIO_DISABLED

    def is_audio_enabled(self, user_id: str) -> bool:
        """Check if audio mode is enabled for a user."""
        return user_id in self._audio_users

    def toggle_text_with_audio(self, user_id: str) -> str:
        """Toggle sending text alongside audio for a user."""
        if user_id in self._text_with_audio_users:
            self._text_with_audio_users.discard(user_id)
            return RESP_TEXT_WITH_AUDIO_OFF
        self._text_with_audio_users.add(user_id)
        return RESP_TEXT_WITH_AUDIO_ON

    def wants_text_with_audio(self, user_id: str) -> bool:
        """Check if user wants text alongside audio."""
        return user_id in self._text_with_audio_users

    def skip_once(self, user_id: str) -> str:
        """Set a one-time TTS skip for the next response."""
        self._skip_once_users.add(user_id)
        return RESP_SKIP_ONCE

    def should_skip(self, user_id: str) -> bool:
        """Check and consume the one-time skip flag."""
        if user_id in self._skip_once_users:
            self._skip_once_users.discard(user_id)
            return True
        return False

    @property
    def language_instruction(self) -> str:
        """Return an AI instruction based on provider language support."""
        langs = self._provider.supported_languages
        if langs == ("en",):
            return (
                "Always respond in English when audio mode is active, even if "
                "the user writes in another language. The TTS engine only "
                "supports English."
            )
        return ""

    def generate_audio_file(self, text: str) -> str:
        """Generate an OGG audio file from text.

        Returns the path to the generated file.

        Raises:
            RuntimeError: If audio generation fails.
        """
        output_dir = Path(self._settings.output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"tts_{uuid.uuid4().hex[:8]}.ogg"

        try:
            audio_data, sample_rate = self._provider.generate(
                text, self._settings.voice, self._settings.speed
            )
            sf.write(
                str(output_path), audio_data, sample_rate,
                format="OGG", subtype="VORBIS",
            )
            size = output_path.stat().st_size
            logger.info(LOG_AUDIO_GENERATED, output_path, size)
            return str(output_path)
        except Exception:
            logger.error(LOG_AUDIO_GENERATION_FAILED, exc_info=True)
            raise
