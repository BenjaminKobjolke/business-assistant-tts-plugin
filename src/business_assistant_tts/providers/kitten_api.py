"""KittenTTS API provider — calls the KittenTTS HTTP server."""

from __future__ import annotations

import io
import logging
from typing import Any

import httpx
import soundfile as sf

logger = logging.getLogger(__name__)

HEALTH_CHECK_TIMEOUT = 5.0
GENERATE_TIMEOUT = 120.0


class KittenTTSAPIProvider:
    """TTS provider using the KittenTTS HTTP API (English only)."""

    def __init__(self, api_url: str) -> None:
        self._api_url = api_url.rstrip("/")
        self._check_server_reachable()
        logger.info("KittenTTS API configured: %s", self._api_url)

    def _check_server_reachable(self) -> None:
        """Verify the KittenTTS server is reachable on startup."""
        url = f"{self._api_url}/api/ui/initial-data"
        try:
            resp = httpx.get(url, timeout=HEALTH_CHECK_TIMEOUT)
            resp.raise_for_status()
        except httpx.ConnectError as exc:
            msg = f"KittenTTS API not reachable at {self._api_url}. Is the server running?"
            raise RuntimeError(msg) from exc
        except httpx.HTTPStatusError as exc:
            msg = f"KittenTTS API health check failed ({exc.response.status_code})"
            raise RuntimeError(msg) from exc

    @property
    def supported_languages(self) -> tuple[str, ...]:
        """KittenTTS only supports English."""
        return ("en",)

    def _post_tts(self, payload: dict[str, Any], timeout: float) -> httpx.Response:
        """Send a TTS request and return the response."""
        url = f"{self._api_url}/tts"
        resp = httpx.post(url, json=payload, timeout=timeout)
        if resp.status_code >= 400:
            content_type = resp.headers.get("content-type", "")
            if content_type.startswith("application/json"):
                detail = resp.json().get("detail", resp.text)
            else:
                detail = resp.text
            msg = f"KittenTTS API error ({resp.status_code}): {detail}"
            raise RuntimeError(msg)
        return resp

    def generate(self, text: str, voice: str, speed: float = 1.0) -> tuple[Any, int]:
        """Generate audio via the API, returning a numpy array and sample rate.

        This is the TTSProvider protocol fallback. The primary path is
        generate_audio_bytes() which avoids the numpy round-trip.
        """
        payload = {
            "text": text,
            "voice": voice,
            "output_format": "wav",
            "split_text": False,
            "speed": speed,
        }
        resp = self._post_tts(payload, timeout=GENERATE_TIMEOUT)
        audio_data, sample_rate = sf.read(io.BytesIO(resp.content))
        return audio_data, sample_rate

    def generate_audio_bytes(
        self, text: str, voice: str, speed: float, output_format: str
    ) -> bytes:
        """Generate audio via the API, returning raw audio bytes.

        The API handles text splitting internally, so the full text
        is sent in a single request.
        """
        payload = {
            "text": text,
            "voice": voice,
            "output_format": output_format,
            "split_text": True,
            "speed": speed,
        }
        resp = self._post_tts(payload, timeout=GENERATE_TIMEOUT)
        return resp.content
