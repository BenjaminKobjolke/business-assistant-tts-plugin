"""Tests for TTSService."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest

from business_assistant_tts.config import TTSSettings
from business_assistant_tts.constants import (
    RESP_AUDIO_ALREADY_OFF,
    RESP_AUDIO_ALREADY_ON,
    RESP_AUDIO_DISABLED,
    RESP_AUDIO_ENABLED,
    RESP_SKIP_ONCE,
    RESP_TEXT_WITH_AUDIO_OFF,
    RESP_TEXT_WITH_AUDIO_ON,
)
from business_assistant_tts.tts_service import TTSService


@pytest.fixture()
def settings() -> TTSSettings:
    return TTSSettings(
        provider="kitten",
        model="test-model",
        voice="Jasper",
        output_dir="",
        speed=1.0,
        language="English",
    )


@pytest.fixture()
def mock_provider() -> MagicMock:
    provider = MagicMock()
    provider.generate.return_value = (np.zeros(24000, dtype=np.float32), 24000)
    provider.supported_languages = ("en",)
    return provider


@pytest.fixture()
def service(mock_provider: MagicMock, settings: TTSSettings, tmp_path: str) -> TTSService:
    s = TTSSettings(
        provider=settings.provider,
        model=settings.model,
        voice=settings.voice,
        output_dir=str(tmp_path),
        speed=settings.speed,
        language=settings.language,
    )
    return TTSService(mock_provider, s)


class TestAudioMode:
    def test_enable(self, service: TTSService) -> None:
        assert service.enable_audio_mode("user1") == RESP_AUDIO_ENABLED
        assert service.is_audio_enabled("user1")

    def test_enable_already_on(self, service: TTSService) -> None:
        service.enable_audio_mode("user1")
        assert service.enable_audio_mode("user1") == RESP_AUDIO_ALREADY_ON

    def test_disable(self, service: TTSService) -> None:
        service.enable_audio_mode("user1")
        assert service.disable_audio_mode("user1") == RESP_AUDIO_DISABLED
        assert not service.is_audio_enabled("user1")

    def test_disable_already_off(self, service: TTSService) -> None:
        assert service.disable_audio_mode("user1") == RESP_AUDIO_ALREADY_OFF

    def test_disable_clears_related_flags(self, service: TTSService) -> None:
        service.enable_audio_mode("user1")
        service.toggle_text_with_audio("user1")
        service.skip_once("user1")
        service.disable_audio_mode("user1")
        assert not service.wants_text_with_audio("user1")
        assert not service.should_skip("user1")


class TestTextWithAudio:
    def test_toggle_on(self, service: TTSService) -> None:
        assert service.toggle_text_with_audio("user1") == RESP_TEXT_WITH_AUDIO_ON
        assert service.wants_text_with_audio("user1")

    def test_toggle_off(self, service: TTSService) -> None:
        service.toggle_text_with_audio("user1")
        assert service.toggle_text_with_audio("user1") == RESP_TEXT_WITH_AUDIO_OFF
        assert not service.wants_text_with_audio("user1")


class TestSkipOnce:
    def test_skip_once(self, service: TTSService) -> None:
        assert service.skip_once("user1") == RESP_SKIP_ONCE
        assert service.should_skip("user1")

    def test_skip_consumed(self, service: TTSService) -> None:
        service.skip_once("user1")
        service.should_skip("user1")
        assert not service.should_skip("user1")


class TestGenerateAudio:
    def test_generates_wav_file(self, service: TTSService, mock_provider: MagicMock) -> None:
        path = service.generate_audio_file("Hello world")
        assert path.endswith(".ogg")
        mock_provider.generate.assert_called_once_with("Hello world", "Jasper", 1.0)

    def test_generation_failure_raises(self, service: TTSService, mock_provider: MagicMock) -> None:
        mock_provider.generate.side_effect = RuntimeError("model error")
        with pytest.raises(RuntimeError, match="model error"):
            service.generate_audio_file("fail")
