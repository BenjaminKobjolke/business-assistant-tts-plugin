"""Tests for the text sanitizer."""

from business_assistant_tts.text_sanitizer import sanitize_for_speech


class TestSanitizeForSpeech:
    def test_strips_bold(self) -> None:
        assert sanitize_for_speech("This is **bold** text") == "This is bold text"

    def test_strips_italic(self) -> None:
        assert sanitize_for_speech("This is *italic* text") == "This is italic text"

    def test_strips_underscore_bold(self) -> None:
        assert sanitize_for_speech("This is __bold__ text") == "This is bold text"

    def test_strips_strikethrough(self) -> None:
        assert sanitize_for_speech("This is ~~removed~~ text") == "This is removed text"

    def test_strips_inline_code(self) -> None:
        assert sanitize_for_speech("Run `npm install` now") == "Run npm install now"

    def test_strips_code_blocks(self) -> None:
        text = "Before\n```python\nprint('hi')\n```\nAfter"
        assert sanitize_for_speech(text) == "Before After"

    def test_strips_headings(self) -> None:
        assert sanitize_for_speech("## My Heading") == "My Heading"

    def test_strips_urls(self) -> None:
        text = "Visit https://example.com/path for more"
        assert sanitize_for_speech(text) == "Visit for more"

    def test_converts_markdown_links(self) -> None:
        text = "Click [here](https://example.com) to continue"
        assert sanitize_for_speech(text) == "Click here to continue"

    def test_converts_markdown_images(self) -> None:
        text = "See ![photo](https://example.com/img.png) above"
        assert sanitize_for_speech(text) == "See photo above"

    def test_strips_list_prefixes(self) -> None:
        text = "- Item one\n- Item two\n* Item three"
        result = sanitize_for_speech(text)
        assert "-" not in result
        assert "*" not in result
        assert "Item one" in result

    def test_strips_numbered_list(self) -> None:
        text = "1. First\n2. Second"
        result = sanitize_for_speech(text)
        assert "1." not in result
        assert "First" in result

    def test_replaces_ampersand(self) -> None:
        assert "and" in sanitize_for_speech("salt & pepper")

    def test_replaces_at_sign(self) -> None:
        assert "at" in sanitize_for_speech("email @ domain")

    def test_replaces_percent(self) -> None:
        assert "percent" in sanitize_for_speech("50%")

    def test_collapses_whitespace(self) -> None:
        text = "Hello   \n\n   world"
        assert sanitize_for_speech(text) == "Hello world"

    def test_strips_edges(self) -> None:
        assert sanitize_for_speech("  hello  ") == "hello"

    def test_empty_string(self) -> None:
        assert sanitize_for_speech("") == ""

    def test_plain_text_unchanged(self) -> None:
        text = "This is a normal sentence."
        assert sanitize_for_speech(text) == text
