from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.entities import User, ResearchSource, Conversation
from backend.app.services.research_service import research_service

router = APIRouter(prefix="/research", tags=["Web Research"])

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5
    conversation_id: str = None

@router.post("/search")
def perform_search(
    req: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    results = research_service.search(req.query, max_results=req.max_results)

    # If linked to a conversation, persist research sources
    if req.conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == req.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if conv:
            for r in results:
                src = ResearchSource(
                    conversation_id=conv.id,
                    query=req.query,
                    title=r.get("title", "Untitled"),
                    url=r.get("url", ""),
                    snippet=r.get("snippet", "")
                )
                db.add(src)
            db.commit()

    return {"query": req.query, "results_count": len(results), "results": results}

@router.get("/citations/{conversation_id}")
def get_citations(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    sources = db.query(ResearchSource).filter(
        ResearchSource.conversation_id == conversation_id
    ).all()

    return [{
        "id": s.id,
        "query": s.query,
        "title": s.title,
        "url": s.url,
        "snippet": s.snippet,
        "retrieval_date": s.retrieval_date
    } for s in sources]
