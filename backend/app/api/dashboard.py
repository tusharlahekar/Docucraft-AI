from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.core.database import get_db, active_engine
from backend.app.core.security import get_current_user
from backend.app.core.llm import llm_service
from backend.app.core.vector_store import vector_store
from backend.app.models.entities import (
    User,
    Conversation,
    UploadedDocument,
    GeneratedDocument,
    ResearchSource
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])

@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    # Conversations count
    c_count = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == current_user.id
    ).scalar()

    # Uploaded documents count
    u_count = db.query(func.count(UploadedDocument.id)).filter(
        UploadedDocument.user_id == current_user.id
    ).scalar()

    # Generated documents count
    g_count = db.query(func.count(GeneratedDocument.id)).filter(
        GeneratedDocument.user_id == current_user.id
    ).scalar()

    # Research sources count
    r_count = db.query(func.count(ResearchSource.id)).join(
        Conversation, ResearchSource.conversation_id == Conversation.id
    ).filter(Conversation.user_id == current_user.id).scalar()

    # Recent activities (last 5 conversations)
    recent_convs = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).limit(5).all()

    conversations_list = [{
        "id": c.id,
        "title": c.title,
        "updated_at": c.updated_at
    } for c in recent_convs]

    # Recent generated docs (last 5)
    recent_gens = db.query(GeneratedDocument).filter(
        GeneratedDocument.user_id == current_user.id
    ).order_by(GeneratedDocument.created_at.desc()).limit(5).all()

    generated_list = [{
        "id": g.id,
        "filename": g.filename,
        "file_type": g.file_type,
        "generation_type": g.generation_type,
        "created_at": g.created_at
    } for g in recent_gens]

    # System Health
    llm_health = await llm_service.check_health()
    try:
        chroma_count = vector_store.collection.count()
        chroma_status = "operational"
    except Exception:
        chroma_count = 0
        chroma_status = "degraded"

    db_driver = str(active_engine.url.drivername)

    return {
        "metrics": {
            "total_conversations": c_count or 0,
            "total_uploaded_documents": u_count or 0,
            "total_generated_documents": g_count or 0,
            "total_research_queries": r_count or 0
        },
        "recent_activity": {
            "conversations": conversations_list,
            "generated_documents": generated_list
        },
        "system_health": {
            "llm": llm_health,
            "vector_db": {
                "engine": "ChromaDB",
                "status": chroma_status,
                "total_chunks_indexed": chroma_count
            },
            "database": {
                "driver": db_driver,
                "status": "connected"
            }
        }
    }
