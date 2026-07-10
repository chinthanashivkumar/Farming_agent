"""
RAG Pipeline — Orchestrates retrieval + LLM generation
"""
from typing import List, Dict, Any, Optional
from loguru import logger

from app.rag.vector_store import semantic_search
from app.services.llm_service import generate_response
from app.utils.language_utils import detect_language, translate_to_english, translate_from_english
from app.prompts.templates import build_prompt


class RAGPipeline:
    """
    Full RAG pipeline:
    1. Detect language
    2. Translate query to English
    3. Semantic search in ChromaDB
    4. Build context-aware prompt
    5. Generate LLM response
    6. Translate response back
    7. Return answer + sources
    """

    def run(
        self,
        user_query: str,
        intent: Optional[str] = None,
        farmer_context: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:

        # Step 1: Language detection
        detected_lang = language or detect_language(user_query)
        logger.info(f"Detected language: {detected_lang}")

        # Step 2: Translate to English for embedding search
        english_query = translate_to_english(user_query, detected_lang) if detected_lang != "en" else user_query

        # Step 3: Semantic retrieval
        where_filter = {"category": intent} if intent else None
        retrieved_docs = semantic_search(english_query, where=where_filter)

        # Step 4: Build prompt
        prompt = build_prompt(
            query=english_query,
            retrieved_docs=retrieved_docs,
            intent=intent,
            farmer_context=farmer_context or {},
        )
        logger.debug(f"Prompt length: {len(prompt)} chars, docs retrieved: {len(retrieved_docs)}")

        # Step 5: Generate response
        english_response = generate_response(prompt)

        # Step 6: Translate response back
        final_response = (
            translate_from_english(english_response, detected_lang)
            if detected_lang != "en"
            else english_response
        )

        # Step 7: Format sources
        sources = [
            {
                "source": d["metadata"].get("source", "unknown"),
                "category": d["metadata"].get("category", "general"),
                "relevance": d["relevance_score"],
            }
            for d in retrieved_docs
        ]

        return {
            "response": final_response,
            "language": detected_lang,
            "intent": intent,
            "sources": sources,
            "docs_retrieved": len(retrieved_docs),
        }


# Singleton
_pipeline = RAGPipeline()


def run_rag(
    query: str,
    intent: Optional[str] = None,
    farmer_context: Optional[Dict] = None,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    return _pipeline.run(query, intent, farmer_context, language)
