"""Tests for plugin registration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from business_assistant.plugins.registry import PluginRegistry

from business_assistant_tts.constants import PLUGIN_DATA_TTS_SERVICE, PLUGIN_NAME


class TestPluginRegistration:
    @patch("business_assistant_tts.plugin.KittenTTSProvider")
    @patch("business_assistant_tts.plugin.add_plugin_logging")
    def test_register_creates_service(
        self, mock_logging: MagicMock, mock_kitten: MagicMock, monkeypatch: object
    ) -> None:
        registry = PluginRegistry()
        from business_assistant_tts.plugin import register

        register(registry)
        assert len(registry.plugins) == 1
        assert registry.plugins[0].name == PLUGIN_NAME
        assert PLUGIN_DATA_TTS_SERVICE in registry.plugin_data

    @patch("business_assistant_tts.plugin.add_plugin_logging")
    def test_register_skips_when_disabled(
        self, mock_logging: MagicMock, monkeypatch: object
    ) -> None:
        import os

        monkeypatch.setattr(os, "environ", {**os.environ, "TTS_PROVIDER": ""})
        registry = PluginRegistry()
        from business_assistant_tts.plugin import register

        register(registry)
        assert len(registry.plugins) == 0
