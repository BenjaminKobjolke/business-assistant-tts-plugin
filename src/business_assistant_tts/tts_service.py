"""TTS service — orchestrates audio generation and user state."""

from __future__ import annotations

import gc
import logging
import uuid
from pathlib import Path

import numpy as np
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

MAX_CHUNK_CHARS = 150


def _convert_wav_to_ogg(wav_path: Path, ogg_path: Path) -> None:
    """Convert WAV to OGG using pydub (soundfile OGG crashes on large files)."""
    from pydub import AudioSegment

    audio = AudioSegment.from_wav(str(wav_path))
    audio.export(str(ogg_path), format="ogg")
    wav_path.unlink()


def _free_gpu_memory() -> None:
    """Free GPU memory between TTS chunk generations."""
    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def _split_at_words(text: str, max_chars: int) -> list[str]:
    """Split text at word boundaries to stay under max_chars per chunk."""
    words = text.split()
    chunks: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}" if current else word
        if len(candidate) > max_chars and current:
            chunks.append(current.strip())
            current = word
        else:
            current = candidate
    if current.strip():
        chunks.append(current.strip())
    return chunks


def _split_long_sentences(sentences: list[str]) -> list[str]:
    """Further split sentences that exceed MAX_CHUNK_CHARS at clause boundaries."""
    result: list[str] = []
    for sentence in sentences:
        if len(sentence) <= MAX_CHUNK_CHARS:
            result.append(sentence)
            continue
        # Try comma boundaries first
        parts = sentence.split(", ")
        current = ""
        comma_chunks: list[str] = []
        for part in parts:
            candidate = f"{current}, {part}" if current else part
            if len(candidate) > MAX_CHUNK_CHARS and current:
                comma_chunks.append(current.strip())
                current = part
            else:
                current = candidate
        if current.strip():
            comma_chunks.append(current.strip())
        # Fallback: split any still-too-long chunk at word boundaries
        for chunk in comma_chunks:
            if len(chunk) > MAX_CHUNK_CHARS:
                result.extend(_split_at_words(chunk, MAX_CHUNK_CHARS))
            else:
                result.append(chunk)
    return result


class TTSService:
    """Manages per-user audio mode state and generates audio files."""

    def __init__(self, provider: TTSProvider, settings: TTSSettings) -> None:
        self._provider = provider
        self._settings = settings
        self._audio_users: set[str] = set()
        self._text_with_audio_users: set[str] = set()
        self._skip_once_users: set[str] = set()
        self._text_messages: dict[str, str] = {}
        self._splitter = self._load_splitter()

    @staticmethod
    def _load_splitter():  # type: ignore[no-untyped-def]
        """Load the wtpsplit sentence splitter model."""
        try:
            from wtpsplit import SaT

            splitter = SaT("sat-3l-sm")
            logger.info("Sentence splitter loaded (sat-3l-sm)")
            return splitter
        except Exception:
            logger.warning("wtpsplit not available — text will not be split into sentences")
            return None

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

    def is_skip_pending(self, user_id: str) -> bool:
        """Check if a one-time skip is pending (does NOT consume it)."""
        return user_id in self._skip_once_users

    def should_skip(self, user_id: str) -> bool:
        """Check and consume the one-time skip flag."""
        if user_id in self._skip_once_users:
            self._skip_once_users.discard(user_id)
            return True
        return False

    def queue_text_message(self, user_id: str, text: str) -> None:
        """Queue a text message to be sent alongside the next audio response."""
        existing = self._text_messages.get(user_id, "")
        self._text_messages[user_id] = (existing + "\n\n" + text).strip()

    def consume_text_message(self, user_id: str) -> str | None:
        """Retrieve and clear queued text message for a user."""
        return self._text_messages.pop(user_id, None)

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
        if len(langs) > 1:
            return (
                "You may respond in the user's language. The TTS engine supports: "
                "Chinese, English, Japanese, Korean, German, French, Russian, "
                "Portuguese, Spanish, Italian."
            )
        return ""

    def _split_text(self, text: str) -> list[str]:
        """Split text into sentences using wtpsplit, then break long ones."""
        if self._splitter is None:
            return _split_long_sentences([text])
        sentences = self._splitter.split(text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return [text]
        chunks = _split_long_sentences(sentences)
        logger.info("Split text into %d chunks for TTS", len(chunks))
        return chunks

    def generate_audio_file(self, text: str) -> str:
        """Generate an OGG audio file from text.

        Returns the path to the generated file.

        Raises:
            RuntimeError: If audio generation fails.
        """
        output_dir = Path(self._settings.output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        file_id = uuid.uuid4().hex[:8]
        ogg_path = output_dir / f"tts_{file_id}.ogg"
        wav_path = output_dir / f"tts_{file_id}.wav"

        try:
            sentences = self._split_text(text)
            chunks = []
            sample_rate = 0
            for sentence in sentences:
                audio_chunk, sample_rate = self._provider.generate(
                    sentence, self._settings.voice, self._settings.speed
                )
                chunks.append(audio_chunk)
                _free_gpu_memory()
            audio_data = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]
            # Write WAV first (soundfile OGG crashes on large audio)
            sf.write(str(wav_path), audio_data, sample_rate)
            # Convert to OGG for smaller file size
            _convert_wav_to_ogg(wav_path, ogg_path)
            size = ogg_path.stat().st_size
            logger.info(LOG_AUDIO_GENERATED, ogg_path, size)
            return str(ogg_path)
        except Exception:
            logger.error(LOG_AUDIO_GENERATION_FAILED, exc_info=True)
            raise
