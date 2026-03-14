"""Command handler for TTS audio mode commands.

Intercepts messages like "audio mode on/off" before they reach
the AI agent, avoiding the need for AI tool slots.
"""

from __future__ import annotations

from typing import Any

from bot_commander.types import BotResponse

from .constants import PLUGIN_DATA_TTS_SERVICE
from .tts_service import TTSService

_ENABLE_COMMANDS = frozenset(
    {
        "audio mode on",
        "audio on",
        "enable audio",
        "enable audio mode",
        "audio modus an",
        "audiomodus an",
        "sprachmodus an",
        "antworte mit audio",
    }
)

_DISABLE_COMMANDS = frozenset(
    {
        "audio mode off",
        "audio off",
        "disable audio",
        "disable audio mode",
        "audio modus aus",
        "audiomodus aus",
        "sprachmodus aus",
    }
)

_TOGGLE_TEXT_COMMANDS = frozenset(
    {
        "toggle text with audio",
        "text with audio",
        "text und audio",
        "text mit audio",
    }
)

_SKIP_ONCE_COMMANDS = frozenset(
    {
        "show me that as text",
        "show as text",
        "text version",
        "as text",
        "zeig mir das als text",
        "als text zeigen",
        "text anzeigen",
    }
)


def tts_command_handler(text: str, user_id: str, plugin_data: dict[str, Any]) -> BotResponse | None:
    """Handle TTS commands. Returns BotResponse to short-circuit, None to continue."""
    service: TTSService | None = plugin_data.get(PLUGIN_DATA_TTS_SERVICE)
    if service is None:
        return None

    normalized = text.lower().strip()

    if normalized in _ENABLE_COMMANDS:
        return BotResponse(text=service.enable_audio_mode(user_id))

    if normalized in _DISABLE_COMMANDS:
        return BotResponse(text=service.disable_audio_mode(user_id))

    if normalized in _TOGGLE_TEXT_COMMANDS:
        return BotResponse(text=service.toggle_text_with_audio(user_id))

    if normalized in _SKIP_ONCE_COMMANDS:
        service.skip_once(user_id)
        return None  # Let AI re-answer, but response processor will skip TTS

    return None
