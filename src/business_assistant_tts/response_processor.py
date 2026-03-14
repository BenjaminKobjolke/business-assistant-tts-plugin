"""Response processor that converts text to audio when audio mode is active."""

from __future__ import annotations

import logging
from typing import Any

from bot_commander.types import BotResponse

from .constants import PLUGIN_DATA_TTS_SERVICE
from .text_sanitizer import sanitize_for_speech
from .tts_service import TTSService

logger = logging.getLogger(__name__)


def tts_response_processor(
    response: BotResponse, user_id: str, plugin_data: dict[str, Any]
) -> BotResponse:
    """Convert text responses to audio when audio mode is enabled.

    Called by the handler for every outgoing response. Returns the
    response unchanged if audio mode is off or if a one-time skip
    is active.
    """
    service: TTSService | None = plugin_data.get(PLUGIN_DATA_TTS_SERVICE)
    if service is None or not service.is_audio_enabled(user_id):
        return response

    if service.should_skip(user_id):
        return response

    if not response.text:
        return response

    try:
        speech_text = sanitize_for_speech(response.text)
        audio_path = service.generate_audio_file(speech_text)
        text = response.text if service.wants_text_with_audio(user_id) else ""
        return BotResponse(text=text, audio_path=audio_path)
    except Exception:
        logger.error("TTS response processing failed, returning text", exc_info=True)
        return response
