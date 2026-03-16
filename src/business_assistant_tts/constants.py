"""Centralized string constants for the TTS plugin."""

# Plugin metadata
PLUGIN_NAME = "tts"
PLUGIN_DESCRIPTION = "Text-to-speech audio responses"

# Environment variable names
ENV_TTS_PROVIDER = "TTS_PROVIDER"
ENV_TTS_MODEL = "TTS_MODEL"
ENV_TTS_VOICE = "TTS_VOICE"
ENV_TTS_OUTPUT_DIR = "TTS_OUTPUT_DIR"
ENV_TTS_SPEED = "TTS_SPEED"
ENV_TTS_LANGUAGE = "TTS_LANGUAGE"

# Defaults
DEFAULT_TTS_PROVIDER = "kitten"
DEFAULT_TTS_MODEL = "KittenML/kitten-tts-mini-0.8"
DEFAULT_TTS_VOICE = "Jasper"
DEFAULT_TTS_OUTPUT_DIR = "data/tts_output"
DEFAULT_TTS_SPEED = 1.0
DEFAULT_TTS_LANGUAGE = "English"

# Qwen3 defaults
DEFAULT_QWEN3_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"
DEFAULT_QWEN3_VOICE = "Vivian"

# Plugin data keys
PLUGIN_DATA_TTS_SERVICE = "tts_service"

# Log messages
LOG_PLUGIN_REGISTERED = "TTS plugin registered (provider=%s)"
LOG_PLUGIN_SKIPPED = "TTS plugin: provider not available, skipping registration"
LOG_AUDIO_GENERATED = "Generated TTS audio: %s (%d bytes)"
LOG_AUDIO_GENERATION_FAILED = "TTS audio generation failed"

# Tool responses
RESP_AUDIO_ENABLED = "Audio mode enabled. I'll respond with voice messages now."
RESP_AUDIO_DISABLED = "Audio mode disabled. Switching back to text responses."
RESP_AUDIO_ALREADY_ON = "Audio mode is already enabled."
RESP_AUDIO_ALREADY_OFF = "Audio mode is already disabled."
RESP_TEXT_WITH_AUDIO_ON = "Text with audio enabled. You'll receive both text and voice."
RESP_TEXT_WITH_AUDIO_OFF = "Text with audio disabled. You'll receive voice only."
RESP_SKIP_ONCE = "Next response will be text only."

# System prompt (no tools — commands handled via command handler hook)
SYSTEM_PROMPT_TTS = """TTS (text-to-speech) audio mode is available. It is controlled by \
chat commands (NOT AI tools — do not look for TTS tools):
- "audio mode on" / "audio modus an" — enable voice responses
- "audio mode off" / "audio modus aus" — disable voice responses
- "show me that as text" / "zeig mir das als text" — one-time text fallback
- "toggle text with audio" — receive both text and voice

If a user asks for audio or voice responses, tell them to type "audio mode on" \
(or "audio modus an" in German). Do NOT try to call any tool for this.

When you see "[AUDIO MODE ACTIVE" at the start of a message, the user has audio \
mode enabled and your response will be converted to speech. Follow the instructions \
in that prefix carefully.

When audio mode is active and you need to share URLs, links, or visual content, \
call the `post_text` tool once per URL. Each call becomes a separate text message \
so the chat client can render image previews. The user will see the text messages \
and hear the audio."""
