import hashlib
from pathlib import Path

import fitz  # PyMuPDF

from app.config import settings


def extract_text_by_page(pdf_path: str) -> list[dict]:
    """Extract text from each page of a PDF."""
    doc = fitz.open(pdf_path)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            pages.append({"page": page_num + 1, "text": text.strip()})
    doc.close()
    return pages


def chunk_text(
    pages: list[dict],
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP,
) -> list[dict]:
    """Split page texts into overlapping chunks using recursive character splitting."""
    separators = ["\n\n", "\n", ". ", " "]
    chunks = []
    chunk_index = 0

    for page_data in pages:
        page_num = page_data["page"]
        text = page_data["text"]

        page_chunks = _recursive_split(text, chunk_size, separators)

        for i, chunk_text_content in enumerate(page_chunks):
            if not chunk_text_content.strip():
                continue
            chunks.append(
                {
                    "text": chunk_text_content.strip(),
                    "metadata": {
                        "page_number": page_num,
                        "chunk_index": chunk_index,
                    },
                }
            )
            chunk_index += 1

        # Handle overlap: if there are chunks from this page, carry overlap into next
        # This is simplified — overlap is within-page only to keep page attribution clean
    return chunks


def _recursive_split(text: str, chunk_size: int, separators: list[str]) -> list[str]:
    """Recursively split text by trying separators in order of preference."""
    if len(text) <= chunk_size:
        return [text]

    # Find the best separator that exists in the text
    separator = ""
    for sep in separators:
        if sep in text:
            separator = sep
            break

    if not separator:
        # No separator found, hard split
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size - settings.CHUNK_OVERLAP)]

    parts = text.split(separator)
    chunks = []
    current_chunk = ""

    for part in parts:
        candidate = current_chunk + separator + part if current_chunk else part
        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # If a single part exceeds chunk_size, split it further
            if len(part) > chunk_size:
                sub_chunks = _recursive_split(
                    part, chunk_size, separators[separators.index(separator) + 1 :]
                )
                chunks.extend(sub_chunks)
                current_chunk = ""
            else:
                current_chunk = part

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def generate_collection_name(filename: str) -> str:
    """Generate a stable collection name from a filename."""
    name_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
    safe_name = "".join(c if c.isalnum() else "_" for c in Path(filename).stem)[:20]
    return f"{safe_name}_{name_hash}"


def process_pdf(pdf_path: str, filename: str | None = None) -> dict:
    """Full pipeline: PDF -> extracted pages -> chunks with metadata."""
    if filename is None:
        filename = Path(pdf_path).name

    pages = extract_text_by_page(pdf_path)
    chunks = chunk_text(pages)
    collection_name = generate_collection_name(filename)

    # Add source filename to all chunk metadata
    for chunk in chunks:
        chunk["metadata"]["source_filename"] = filename

    return {
        "collection_name": collection_name,
        "chunks": chunks,
        "total_pages": len(pages),
        "total_chunks": len(chunks),
    }
