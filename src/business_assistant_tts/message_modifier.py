"""Message modifier that injects speech formatting context when audio mode is active."""

from __future__ import annotations

from typing import Any

from .constants import PLUGIN_DATA_TTS_SERVICE
from .tts_service import TTSService

_AUDIO_MODE_PREFIX = (
    "[AUDIO MODE ACTIVE — Your response will be converted to speech. "
    "Write in flowing, conversational sentences. No bullet points, no lists, "
    "no markdown, no IDs, no code. "
    "If you need to share URLs, links, images, or clickable content, call the "
    "post_text tool — URLs are automatically extracted and sent as separate "
    "messages for image preview rendering. "
    "Keep each sentence under 30 words. Avoid cramming multiple data points "
    "into one sentence. Split complex information across separate short sentences. "
    "Use natural speech patterns. {lang_instruction}]\n"
)


def tts_message_modifier(text: str, user_id: str, plugin_data: dict[str, Any]) -> str:
    """Prepend speech formatting instructions when audio mode is active."""
    service: TTSService | None = plugin_data.get(PLUGIN_DATA_TTS_SERVICE)
    if service is None or not service.is_audio_enabled(user_id):
        return text
    if service.is_skip_pending(user_id):
        return text
    prefix = _AUDIO_MODE_PREFIX.format(lang_instruction=service.language_instruction)
    return prefix + text
