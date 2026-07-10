"""
Document Loader & Chunker — Ingests PDFs, DOCX, TXT into ChromaDB
"""
import os
import uuid
import re
from typing import List, Dict, Tuple
from pathlib import Path
from loguru import logger

from app.core.config import settings
from app.rag.vector_store import add_documents


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Split text into overlapping chunks."""
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP

    # Clean whitespace
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if len(chunk.strip()) > 30:  # skip tiny chunks
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def load_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_pdf(filepath: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        logger.warning(f"PDF load error {filepath}: {e}")
        return ""


def load_docx(filepath: str) -> str:
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        logger.warning(f"DOCX load error {filepath}: {e}")
        return ""


def ingest_file(filepath: str, source_tag: str, category: str):
    """Load a file and add chunks to ChromaDB."""
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        text = load_pdf(filepath)
    elif ext in (".docx", ".doc"):
        text = load_docx(filepath)
    else:
        text = load_txt(filepath)

    if not text.strip():
        logger.warning(f"Empty content: {filepath}")
        return 0

    chunks = chunk_text(text)
    docs, metadatas, ids = [], [], []

    for i, chunk in enumerate(chunks):
        docs.append(chunk)
        metadatas.append({
            "source": source_tag,
            "file": Path(filepath).name,
            "category": category,
            "chunk_index": i,
        })
        ids.append(f"{source_tag}_{i}_{uuid.uuid4().hex[:8]}")

    add_documents(docs, metadatas, ids)
    logger.info(f"Ingested {len(chunks)} chunks from {Path(filepath).name} [{category}]")
    return len(chunks)


def ingest_directory(directory: str = None):
    """Ingest all documents from the data/documents directory."""
    directory = directory or os.path.join(os.path.dirname(__file__), "../../data/documents")
    directory = os.path.abspath(directory)

    CATEGORY_MAP = {
        "crop": "crop_recommendation",
        "soil": "soil_analysis",
        "pest": "pest_management",
        "fertilizer": "fertilizer",
        "irrigation": "irrigation",
        "market": "market_prices",
    }

    total = 0
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if not os.path.isfile(fpath):
            continue
        name_lower = fname.lower()
        category = "general"
        for key, val in CATEGORY_MAP.items():
            if key in name_lower:
                category = val
                break
        source_tag = Path(fname).stem.replace(" ", "_").lower()
        total += ingest_file(fpath, source_tag, category)

    logger.info(f"Total chunks ingested: {total}")
    return total
