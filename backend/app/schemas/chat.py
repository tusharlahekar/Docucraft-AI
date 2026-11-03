from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class MessageCreate(BaseModel):
    content: str
    attached_doc_ids: Optional[List[str]] = []

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender: str
    content: str
    citations: Optional[List[Dict[str, Any]]] = []
    attached_doc_ids: Optional[List[str]] = []
    generated_doc_ids: Optional[List[str]] = []
    agent_logs: Optional[List[Dict[str, Any]]] = []
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class ConversationUpdate(BaseModel):
    title: str

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageResponse]] = []

    class Config:
        from_attributes = True
