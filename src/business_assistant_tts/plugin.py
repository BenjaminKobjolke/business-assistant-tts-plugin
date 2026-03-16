"""Plugin registration — TTS with command handler hooks and post_text tool."""

from __future__ import annotations

import logging

from business_assistant.agent.deps import Deps
from business_assistant.config.log_setup import add_plugin_logging
from business_assistant.plugins.registry import PluginInfo, PluginRegistry
from pydantic_ai import RunContext, Tool

from .command_handler import tts_command_handler
from .config import TTSSettings, load_tts_settings
from .constants import (
    LOG_PLUGIN_REGISTERED,
    LOG_PLUGIN_SKIPPED,
    PLUGIN_DATA_TTS_SERVICE,
    PLUGIN_DESCRIPTION,
    PLUGIN_NAME,
    SYSTEM_PROMPT_TTS,
)
from .message_modifier import tts_message_modifier
from .providers.base import TTSProvider
from .providers.kitten import KittenTTSProvider
from .response_processor import tts_response_processor
from .tts_service import TTSService

logger = logging.getLogger(__name__)


def _create_provider(settings: TTSSettings) -> TTSProvider:
    """Create the TTS provider based on settings."""
    if settings.provider == "kitten":
        return KittenTTSProvider(settings.model)
    if settings.provider == "qwen3":
        from .providers.qwen3 import Qwen3TTSProvider

        return Qwen3TTSProvider(settings.model, settings.language)
    msg = f"Unknown TTS provider: {settings.provider}"
    raise ValueError(msg)


def _post_text(ctx: RunContext[Deps], text: str) -> str:
    """Post a text message to the user alongside the audio response.

    Use this when you need to share URLs, links, images, or any content
    the user needs to see or click while in audio mode.
    """
    service: TTSService = ctx.deps.plugin_data[PLUGIN_DATA_TTS_SERVICE]
    service.queue_text_message(ctx.deps.user_id, text)
    return "Text message queued — will be sent alongside your audio response."


def register(registry: PluginRegistry) -> None:
    """Register the TTS plugin with the plugin registry."""
    add_plugin_logging(PLUGIN_NAME, "business_assistant_tts")

    settings = load_tts_settings()
    if settings is None:
        logger.info(LOG_PLUGIN_SKIPPED)
        return

    provider = _create_provider(settings)
    service = TTSService(provider, settings)

    info = PluginInfo(
        name=PLUGIN_NAME,
        description=PLUGIN_DESCRIPTION,
        system_prompt_extra=SYSTEM_PROMPT_TTS,
    )

    tools = [Tool(_post_text, name="post_text")]
    registry.register(info, tools)
    registry.plugin_data[PLUGIN_DATA_TTS_SERVICE] = service
    registry.register_command_handler(tts_command_handler)
    registry.register_message_modifier(tts_message_modifier)
    registry.register_response_processor(tts_response_processor)

    logger.info(LOG_PLUGIN_REGISTERED, settings.provider)
