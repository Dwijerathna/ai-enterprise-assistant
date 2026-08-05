"""Semantic-friendly text chunking utilities."""


def estimate_token_count(text: str) -> int:
    """Estimate token count using whitespace-delimited words."""
    if not text.strip():
        return 0
    return len(text.split())


def _derive_section_title(content: str, fallback: str | None = None) -> str | None:
    first_line = content.split("\n", 1)[0].strip()
    if fallback:
        return fallback
    if len(first_line) <= 120:
        return first_line
    return first_line[:117] + "..."


def create_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
    page_number: int | None = 1,
    section_title: str | None = None,
) -> list[dict[str, int | str | None]]:
    """
    Split text into overlapping chunks, preferring paragraph and sentence boundaries.
    """
    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    paragraphs = [part.strip() for part in text.split("\n") if part.strip()]
    if not paragraphs:
        return []

    chunks: list[dict[str, int | str | None]] = []
    buffer = ""
    chunk_index = 0

    def flush_buffer(content: str) -> None:
        nonlocal chunk_index
        normalized = content.strip()
        if not normalized:
            return
        chunks.append(
            {
                "content": normalized,
                "chunk_index": chunk_index,
                "page_number": page_number,
                "section_title": _derive_section_title(normalized, section_title),
                "token_count": estimate_token_count(normalized),
            }
        )
        chunk_index += 1

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if buffer:
                flush_buffer(buffer)
                buffer = ""

            start = 0
            while start < len(paragraph):
                end = min(start + chunk_size, len(paragraph))
                segment = paragraph[start:end]

                if end < len(paragraph):
                    split_at = max(segment.rfind(". "), segment.rfind(" "))
                    if split_at > chunk_size // 2:
                        end = start + split_at + 1
                        segment = paragraph[start:end]

                flush_buffer(segment)
                if end >= len(paragraph):
                    break
                start = max(end - overlap, start + 1)
            continue

        candidate = f"{buffer}\n{paragraph}".strip() if buffer else paragraph
        if len(candidate) <= chunk_size:
            buffer = candidate
            continue

        flush_buffer(buffer)
        buffer = paragraph

    if buffer:
        flush_buffer(buffer)

    return chunks


def create_chunks_from_pages(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict[str, int | str | None]]:
    """Create chunks from page-aware extracted document sections."""
    all_chunks: list[dict[str, int | str | None]] = []
    next_index = 0

    for page in pages:
        page_chunks = create_chunks(
            text=str(page.get("text", "")),
            chunk_size=chunk_size,
            overlap=overlap,
            page_number=page.get("page_number"),
            section_title=page.get("section_title"),
        )
        for chunk in page_chunks:
            chunk["chunk_index"] = next_index
            next_index += 1
            all_chunks.append(chunk)

    return all_chunks
