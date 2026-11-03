import logging
import time
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.entities import (
    User,
    Conversation,
    Message,
    GeneratedDocument,
    DocumentVersion,
    AgentExecutionLog
)
from backend.app.schemas.chat import MessageCreate, MessageResponse
from backend.app.agents.graph import multi_agent_app
from backend.app.agents.state import AgentState

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/{conversation_id}/send", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify conversation ownership
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    # 1. Save User Message
    user_msg = Message(
        conversation_id=conversation_id,
        sender="user",
        content=message_in.content,
        attached_doc_ids=message_in.attached_doc_ids or []
    )
    db.add(user_msg)
    db.commit()

    # 2. Prepare LangGraph State
    initial_state: AgentState = {
        "user_id": current_user.id,
        "conversation_id": conversation_id,
        "user_message": message_in.content,
        "attached_doc_ids": message_in.attached_doc_ids or [],
        "intent": "chat",
        "target_format": "none",
        "requires_research": False,
        "requires_rag": False,
        "document_structures": [],
        "rag_context": [],
        "research_results": [],
        "draft_content": {},
        "editing_instructions": {},
        "validation_result": {},
        "generated_doc_info": None,
        "final_response": "",
        "citations": [],
        "execution_logs": [],
        "errors": []
    }

    # 3. Execute LangGraph Multi-Agent Pipeline
    try:
        final_state = multi_agent_app.invoke(initial_state)
    except Exception as e:
        logger.error(f"Multi-agent graph execution failed: {e}", exc_info=True)
        final_state = initial_state
        final_state["final_response"] = f"An error occurred while coordinating agents: {str(e)}"

    # 4. Process Generated Artifact if produced by Agent
    generated_doc_ids = []
    gen_doc = final_state.get("generated_doc_info")
    if gen_doc:
        attached_ids = final_state.get("attached_doc_ids") or []
        source_doc_id = attached_ids[0] if len(attached_ids) > 0 else None
        new_gen_doc = GeneratedDocument(
            user_id=current_user.id,
            conversation_id=conversation_id,
            source_document_id=source_doc_id,
            filename=gen_doc.get("filename"),
            file_type=gen_doc.get("file_type"),
            file_size=gen_doc.get("file_size", 0),
            storage_path=gen_doc.get("storage_path"),
            generation_type=gen_doc.get("generation_type", "created_from_scratch"),
            diff_summary=gen_doc.get("diff_summary") or final_state.get("editing_instructions", {})
        )
        db.add(new_gen_doc)

        if source_doc_id:
            doc_ver = DocumentVersion(
                document_id=source_doc_id,
                version_number=int(time.time()),
                storage_path=gen_doc.get("storage_path"),
                change_description=message_in.content
            )
            db.add(doc_ver)

        db.commit()
        db.refresh(new_gen_doc)
        generated_doc_ids.append(new_gen_doc.id)

    # 5. Persist Agent Execution Logs to DB
    for log_item in final_state.get("execution_logs", []):
        db_log = AgentExecutionLog(
            conversation_id=conversation_id,
            agent_name=log_item.get("agent", "Agent"),
            step_name=log_item.get("step", "Step"),
            input_state_summary={"input": log_item.get("input")},
            output_state_summary={"output": log_item.get("output")},
            execution_time_ms=log_item.get("duration_ms", 0)
        )
        db.add(db_log)

    # 6. Save Assistant Response Message
    assistant_msg = Message(
        conversation_id=conversation_id,
        sender="assistant",
        content=final_state.get("final_response", ""),
        citations=final_state.get("citations", []),
        attached_doc_ids=message_in.attached_doc_ids or [],
        generated_doc_ids=generated_doc_ids,
        agent_logs=final_state.get("execution_logs", [])
    )
    db.add(assistant_msg)

    # Auto-generate or update title if conversation was default
    if conv.title == "New Conversation" and len(message_in.content) > 3:
        clean_title = message_in.content[:32].capitalize()
        conv.title = f"{clean_title}..."
    conv.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(assistant_msg)

    return MessageResponse.model_validate(assistant_msg)
