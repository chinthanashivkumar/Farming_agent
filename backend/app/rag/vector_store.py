"""
RAG Vector Store — ChromaDB with Sentence Transformers
"""
import os
from typing import List, Dict, Any, Optional
from loguru import logger
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import numpy as np

from app.core.config import settings


_client: Optional[chromadb.PersistentClient] = None
_collection = None
_embedder: Optional[SentenceTransformer] = None


async def init_vector_store():
    """Initialize ChromaDB and embedding model on startup."""
    global _client, _collection, _embedder

    logger.info("🔄 Loading embedding model...")
    _embedder = SentenceTransformer(settings.EMBEDDING_MODEL, device=settings.EMBEDDING_DEVICE)

    logger.info("🔄 Initializing ChromaDB...")
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    _client = chromadb.PersistentClient(
        path=settings.CHROMA_PERSIST_DIR,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    _collection = _client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    logger.info(f"✅ Vector store ready. Documents: {_collection.count()}")


def get_collection():
    return _collection


def get_embedder():
    return _embedder


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts."""
    return _embedder.encode(texts, normalize_embeddings=True).tolist()


def add_documents(
    docs: List[str],
    metadatas: List[Dict[str, Any]],
    ids: List[str],
):
    """Add documents to ChromaDB."""
    embeddings = embed_texts(docs)
    _collection.add(
        documents=docs,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )
    logger.info(f"Added {len(docs)} documents to vector store.")


def semantic_search(
    query: str,
    n_results: int = None,
    where: Optional[Dict] = None,
) -> List[Dict[str, Any]]:
    """Retrieve top-k relevant documents for a query."""
    n_results = n_results or settings.TOP_K_RESULTS
    query_embedding = embed_texts([query])[0]

    kwargs = dict(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    if where:
        kwargs["where"] = where

    results = _collection.query(**kwargs)

    docs_out = []
    for i, (doc, meta, dist) in enumerate(
        zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
    ):
        relevance = float(1 - dist)          # cosine distance → similarity
        if relevance >= settings.MIN_RELEVANCE_SCORE:
            docs_out.append({
                "content": doc,
                "metadata": meta,
                "relevance_score": round(relevance, 4),
                "rank": i + 1,
            })

    return docs_out
