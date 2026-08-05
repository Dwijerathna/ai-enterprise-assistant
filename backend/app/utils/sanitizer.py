"""Text cleaning utilities for document ingestion."""

import re


def clean_text(text: str) -> str:
    """
    Normalize extracted document text.

    Removes excessive whitespace, unwanted control characters, and empty lines.
    """
    if not text:
        return ""

    # Remove control characters except common whitespace.
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)

    # Normalize line endings and collapse repeated spaces.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)

    # Remove empty lines and trim each line.
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]

    return "\n".join(lines)
