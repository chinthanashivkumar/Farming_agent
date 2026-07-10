"""
AI Chat Routes — Core RAG endpoint
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.rag.rag_pipeline import run_rag
from app.utils.intent_detector import detect_intent
from app.models.chat_history import ChatSession, ChatMessage

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = None
    farmer_context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    response: str
    intent: Optional[str]
    language: str
    sources: List[Dict[str, Any]]
    docs_retrieved: int


@router.post("/", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    # Resolve or create session
    if req.session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == uuid.UUID(req.session_id),
                ChatSession.user_id == uuid.UUID(user_id),
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(
            user_id=uuid.UUID(user_id),
            title=req.message[:60],
            language=req.language or "en",
        )
        db.add(session)
        await db.flush()

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=req.message,
        language=req.language or "en",
    )
    db.add(user_msg)

    # Detect intent
    intent = detect_intent(req.message)

    # Run RAG pipeline
    result = run_rag(
        query=req.message,
        intent=intent if intent != "general" else None,
        farmer_context=req.farmer_context,
        language=req.language,
    )

    # Save AI response
    ai_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=result["response"],
        language=result["language"],
        intent=result["intent"],
        sources=result["sources"],
    )
    db.add(ai_msg)
    await db.commit()

    return ChatResponse(
        session_id=str(session.id),
        message_id=str(ai_msg.id),
        response=result["response"],
        intent=result["intent"],
        language=result["language"],
        sources=result["sources"],
        docs_retrieved=result["docs_retrieved"],
    )


@router.get("/sessions")
async def get_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == uuid.UUID(current_user["user_id"]))
        .order_by(ChatSession.created_at.desc())
        .limit(50)
    )
    sessions = result.scalars().all()
    return [{"id": str(s.id), "title": s.title, "created_at": str(s.created_at)} for s in sessions]


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(ChatMessage)
        .join(ChatSession, ChatMessage.session_id == ChatSession.id)
        .where(
            ChatSession.id == uuid.UUID(session_id),
            ChatSession.user_id == uuid.UUID(current_user["user_id"]),
        )
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "intent": m.intent,
            "sources": m.sources,
            "created_at": str(m.created_at),
        }
        for m in messages
    ]
