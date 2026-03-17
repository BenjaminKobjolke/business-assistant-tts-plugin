"""Tests for the TTS response processor."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest
from bot_commander.types import BotResponse

from business_assistant_tts.config import TTSSettings
from business_assistant_tts.constants import PLUGIN_DATA_TTS_SERVICE
from business_assistant_tts.response_processor import tts_response_processor
from business_assistant_tts.tts_service import TTSService


@pytest.fixture()
def mock_provider() -> MagicMock:
    provider = MagicMock(spec=["generate", "supported_languages"])
    provider.generate.return_value = (np.zeros(24000, dtype=np.float32), 24000)
    provider.supported_languages = ("en",)
    return provider


@pytest.fixture()
def service(mock_provider: MagicMock, tmp_path: str) -> TTSService:
    settings = TTSSettings(
        provider="kitten",
        model="test",
        voice="Jasper",
        language="English",
        output_dir=str(tmp_path),
        speed=1.0,
        api_url="http://localhost:8005",
        output_format="opus",
    )
    return TTSService(mock_provider, settings)


@pytest.fixture()
def plugin_data(service: TTSService) -> dict:
    return {PLUGIN_DATA_TTS_SERVICE: service}


class TestResponseProcessor:
    def test_passthrough_when_audio_off(self, plugin_data: dict) -> None:
        response = BotResponse(text="Hello")
        result = tts_response_processor(response, "user1", plugin_data)
        assert result.text == "Hello"
        assert result.audio_path == ""

    def test_converts_to_audio_when_enabled(self, plugin_data: dict, service: TTSService) -> None:
        service.enable_audio_mode("user1")
        response = BotResponse(text="Hello world")
        result = tts_response_processor(response, "user1", plugin_data)
        assert result.text == ""
        assert result.audio_path.endswith(".ogg")

    def test_keeps_text_when_text_with_audio(self, plugin_data: dict, service: TTSService) -> None:
        service.enable_audio_mode("user1")
        service.toggle_text_with_audio("user1")
        response = BotResponse(text="Hello world")
        result = tts_response_processor(response, "user1", plugin_data)
        assert result.text == "Hello world"
        assert result.audio_path.endswith(".ogg")

    def test_skip_once_returns_text(self, plugin_data: dict, service: TTSService) -> None:
        service.enable_audio_mode("user1")
        service.skip_once("user1")
        response = BotResponse(text="Detailed text")
        result = tts_response_processor(response, "user1", plugin_data)
        assert result.text == "Detailed text"
        assert result.audio_path == ""

    def test_skip_once_consumed(self, plugin_data: dict, service: TTSService) -> None:
        service.enable_audio_mode("user1")
        service.skip_once("user1")
        response = BotResponse(text="First")
        tts_response_processor(response, "user1", plugin_data)
        # Second call should generate audio again
        response2 = BotResponse(text="Second")
        result = tts_response_processor(response2, "user1", plugin_data)
        assert result.audio_path.endswith(".ogg")

    def test_empty_text_passthrough(self, plugin_data: dict, service: TTSService) -> None:
        service.enable_audio_mode("user1")
        response = BotResponse(text="")
        result = tts_response_processor(response, "user1", plugin_data)
        assert result.text == ""
        assert result.audio_path == ""

    def test_no_service_passthrough(self) -> None:
        response = BotResponse(text="Hello")
        result = tts_response_processor(response, "user1", {})
        assert result.text == "Hello"

    def test_provider_failure_returns_text(
        self, plugin_data: dict, service: TTSService, mock_provider: MagicMock
    ) -> None:
        service.enable_audio_mode("user1")
        mock_provider.generate.side_effect = RuntimeError("fail")
        response = BotResponse(text="Hello")
        result = tts_response_processor(response, "user1", plugin_data)
        assert result.text == "Hello"
        assert result.audio_path == ""
