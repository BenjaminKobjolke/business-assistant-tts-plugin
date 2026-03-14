"""Sanitize text for natural speech output.

Strips markdown, symbols, and formatting artifacts that the AI
might include despite system prompt instructions.
"""

from __future__ import annotations

import re

# Markdown link: [text](url) → text
_RE_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")

# Markdown image: ![alt](url) → alt
_RE_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]+\)")

# Code blocks: ```...``` → empty
_RE_CODE_BLOCK = re.compile(r"```[\s\S]*?```")

# Inline code: `text` → text
_RE_INLINE_CODE = re.compile(r"`([^`]+)`")

# Bold/italic: **text**, *text*, __text__, _text_
_RE_BOLD = re.compile(r"\*\*(.+?)\*\*")
_RE_ITALIC = re.compile(r"\*(.+?)\*")
_RE_BOLD_UNDER = re.compile(r"__(.+?)__")
_RE_ITALIC_UNDER = re.compile(r"(?<!\w)_(.+?)_(?!\w)")

# Strikethrough: ~~text~~ → text
_RE_STRIKETHROUGH = re.compile(r"~~(.+?)~~")

# Headings: # text → text
_RE_HEADING = re.compile(r"^#{1,6}\s+", re.MULTILINE)

# URLs: https://... or http://...
_RE_URL = re.compile(r"https?://\S+")

# Bullet/list prefixes: - item, * item, 1. item
_RE_LIST_PREFIX = re.compile(r"^\s*(?:[-*]|\d+\.)\s+", re.MULTILINE)

# Multiple whitespace/newlines → single space
_RE_MULTI_WHITESPACE = re.compile(r"\s+")

# Symbol replacements
_SYMBOL_MAP = {
    "&": " and ",
    "@": " at ",
    "%": " percent ",
    "+": " plus ",
    "=": " equals ",
    "<": " less than ",
    ">": " greater than ",
}


def sanitize_for_speech(text: str) -> str:
    """Clean text for TTS by removing formatting and replacing symbols.

    Args:
        text: Raw text potentially containing markdown and symbols.

    Returns:
        Clean text suitable for speech synthesis.
    """
    result = text

    # Remove code blocks first (before other patterns match inside them)
    result = _RE_CODE_BLOCK.sub("", result)

    # Markdown images and links
    result = _RE_MD_IMAGE.sub(r"\1", result)
    result = _RE_MD_LINK.sub(r"\1", result)

    # Inline code
    result = _RE_INLINE_CODE.sub(r"\1", result)

    # Bold/italic/strikethrough
    result = _RE_BOLD.sub(r"\1", result)
    result = _RE_BOLD_UNDER.sub(r"\1", result)
    result = _RE_ITALIC.sub(r"\1", result)
    result = _RE_ITALIC_UNDER.sub(r"\1", result)
    result = _RE_STRIKETHROUGH.sub(r"\1", result)

    # Headings
    result = _RE_HEADING.sub("", result)

    # URLs
    result = _RE_URL.sub("", result)

    # List prefixes
    result = _RE_LIST_PREFIX.sub("", result)

    # Symbol replacements
    for symbol, replacement in _SYMBOL_MAP.items():
        result = result.replace(symbol, replacement)

    # Collapse whitespace
    result = _RE_MULTI_WHITESPACE.sub(" ", result)

    return result.strip()
