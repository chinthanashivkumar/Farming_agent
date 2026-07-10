"""
RAG Pipeline — Orchestrates retrieval + LLM generation
"""
from typing import Dict, Any, Optional
from loguru import logger

from app.rag.vector_store import semantic_search
from app.services.llm_service import generate_response
from app.utils.language_utils import detect_language, translate_to_english, translate_from_english
from app.prompts.templates import build_prompt


class RAGPipeline:

    def run(
        self,
        user_query: str,
        intent: Optional[str] = None,
        farmer_context: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:

        # Step 1: Use the language the user selected in the UI
        detected_lang = language or detect_language(user_query)
        logger.info(f"Language: {detected_lang}")

        # Step 2: Translate query to English so semantic search works properly
        if detected_lang != "en":
            try:
                english_query = translate_to_english(user_query, detected_lang)
                # if translation returned same text or empty, keep original
                if not english_query or english_query.strip() == user_query.strip():
                    english_query = user_query
            except Exception:
                english_query = user_query
        else:
            english_query = user_query

        # Step 3: Semantic retrieval from ChromaDB
        where_filter = {"category": intent} if intent else None
        retrieved_docs = semantic_search(english_query, where=where_filter)

        # Step 4: Build prompt — LLM is instructed to reply in the target language
        prompt = build_prompt(
            query=english_query,
            original_query=user_query if detected_lang != "en" else None,
            retrieved_docs=retrieved_docs,
            intent=intent,
            farmer_context=farmer_context or {},
            language=detected_lang,
        )
        logger.debug(f"Prompt chars: {len(prompt)}, docs retrieved: {len(retrieved_docs)}")

        # Step 5: LLM generates response
        llm_response = generate_response(prompt)
        logger.info(f"LLM response preview: {llm_response[:120]!r}")

        # Step 6: ALWAYS translate to the target language for non-English.
        # We do NOT rely on the LLM obeying the language instruction — Granite 13B
        # is an English-first model and will often reply in English regardless.
        # deep_translator (Google Translate) is the reliable guarantee here.
        final_response = llm_response
        if detected_lang != "en":
            try:
                translated = translate_from_english(llm_response, detected_lang)
                if translated and translated.strip():
                    final_response = translated
                    logger.info(f"Translated response to {detected_lang}: {final_response[:80]!r}")
                else:
                    logger.warning(f"Translation returned empty — keeping LLM response")
            except Exception as e:
                logger.error(f"Translation failed: {e} — keeping LLM response in English")

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


_pipeline = RAGPipeline()


def run_rag(
    query: str,
    intent: Optional[str] = None,
    farmer_context: Optional[Dict] = None,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    return _pipeline.run(query, intent, farmer_context, language)
