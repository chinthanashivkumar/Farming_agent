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

    def run(
        self,
        user_query: str,
        intent: Optional[str] = None,
        farmer_context: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:

        # Step 1: Language — trust the frontend-sent language code first
        detected_lang = language or detect_language(user_query)
        logger.info(f"Language: {detected_lang}")

        # Step 2: Translate query to English for semantic search
        if detected_lang != "en":
            english_query = translate_to_english(user_query, detected_lang)
            if not english_query or english_query.strip() == user_query.strip():
                # translation failed — use original and let the LLM handle it
                english_query = user_query
        else:
            english_query = user_query

        # Step 3: Semantic retrieval
        where_filter = {"category": intent} if intent else None
        retrieved_docs = semantic_search(english_query, where=where_filter)

        # Step 4: Build prompt — pass original non-English query so LLM
        # sees the actual Kannada/Hindi text and knows which language to use
        prompt = build_prompt(
            query=english_query,
            original_query=user_query if detected_lang != "en" else None,
            retrieved_docs=retrieved_docs,
            intent=intent,
            farmer_context=farmer_context or {},
            language=detected_lang,
        )
        logger.debug(f"Prompt chars: {len(prompt)}, docs: {len(retrieved_docs)}")

        # Step 5: Generate response from LLM
        llm_response = generate_response(prompt)
        logger.debug(f"LLM raw response (first 200): {llm_response[:200]}")

        # Step 6: If the LLM ignored the language instruction and replied in
        # English, force-translate the response to the target language.
        final_response = llm_response
        if detected_lang != "en":
            from app.utils.language_utils import looks_english
            if looks_english(llm_response):
                logger.info(f"LLM replied in English despite {detected_lang} instruction — translating.")
                translated = translate_from_english(llm_response, detected_lang)
                if translated and translated.strip():
                    final_response = translated

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
