"""Tests for Qwen3-TTS provider."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import numpy as np
import pytest

# Mock qwen_tts before importing the provider module
_mock_qwen_tts = MagicMock()
sys.modules["qwen_tts"] = _mock_qwen_tts

from business_assistant_tts.providers.qwen3 import (  # noqa: E402
    SPEED_FAST_THRESHOLD,
    SPEED_SLOW_THRESHOLD,
    Qwen3TTSProvider,
    _speed_to_instruct,
)


class TestSpeedToInstruct:
    def test_normal_speed_returns_empty(self) -> None:
        assert _speed_to_instruct(1.0) == ""

    def test_slow_speed_returns_slow_instruction(self) -> None:
        result = _speed_to_instruct(0.5)
        assert "slowly" in result.lower()

    def test_fast_speed_returns_fast_instruction(self) -> None:
        result = _speed_to_instruct(1.5)
        assert "faster" in result.lower()

    def test_boundary_slow_returns_empty(self) -> None:
        assert _speed_to_instruct(SPEED_SLOW_THRESHOLD) == ""

    def test_boundary_fast_returns_empty(self) -> None:
        assert _speed_to_instruct(SPEED_FAST_THRESHOLD) == ""

    def test_just_below_slow_threshold(self) -> None:
        result = _speed_to_instruct(SPEED_SLOW_THRESHOLD - 0.01)
        assert result != ""

    def test_just_above_fast_threshold(self) -> None:
        result = _speed_to_instruct(SPEED_FAST_THRESHOLD + 0.01)
        assert result != ""


@pytest.fixture()
def mock_model() -> MagicMock:
    """Reset and return the mock Qwen3TTSModel for each test."""
    _mock_qwen_tts.Qwen3TTSModel.reset_mock()
    mock_instance = MagicMock()
    _mock_qwen_tts.Qwen3TTSModel.from_pretrained.return_value = mock_instance
    return mock_instance


class TestQwen3TTSProvider:
    def test_supported_languages_returns_ten(self, mock_model: MagicMock) -> None:
        provider = Qwen3TTSProvider("Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", "English")
        langs = provider.supported_languages
        assert len(langs) == 10
        assert "en" in langs
        assert "zh" in langs
        assert "ja" in langs
        assert "de" in langs

    def test_generate_calls_custom_voice(self, mock_model: MagicMock) -> None:
        provider = Qwen3TTSProvider("Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", "English")
        audio = np.zeros(16000, dtype=np.float32)
        mock_model.generate_custom_voice.return_value = ([audio], 24000)

        result_audio, result_sr = provider.generate("Hello", "Vivian", 1.0)

        mock_model.generate_custom_voice.assert_called_once_with(
            text="Hello",
            language="English",
            speaker="Vivian",
            instruct="",
            max_new_tokens=2048,
        )
        assert result_sr == 24000
        assert len(result_audio) == 16000

    def test_generate_passes_language(self, mock_model: MagicMock) -> None:
        provider = Qwen3TTSProvider("Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", "German")
        audio = np.zeros(16000, dtype=np.float32)
        mock_model.generate_custom_voice.return_value = ([audio], 24000)

        provider.generate("Hallo Welt", "Dylan", 1.0)

        call_kwargs = mock_model.generate_custom_voice.call_args
        assert call_kwargs.kwargs["language"] == "German"

    def test_generate_with_slow_speed(self, mock_model: MagicMock) -> None:
        provider = Qwen3TTSProvider("Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", "English")
        audio = np.zeros(16000, dtype=np.float32)
        mock_model.generate_custom_voice.return_value = ([audio], 24000)

        provider.generate("Hello", "Vivian", 0.5)

        call_kwargs = mock_model.generate_custom_voice.call_args
        assert "slowly" in call_kwargs.kwargs["instruct"].lower()

    def test_generate_with_fast_speed(self, mock_model: MagicMock) -> None:
        provider = Qwen3TTSProvider("Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", "English")
        audio = np.zeros(16000, dtype=np.float32)
        mock_model.generate_custom_voice.return_value = ([audio], 24000)

        provider.generate("Hello", "Vivian", 1.5)

        call_kwargs = mock_model.generate_custom_voice.call_args
        assert "faster" in call_kwargs.kwargs["instruct"].lower()
