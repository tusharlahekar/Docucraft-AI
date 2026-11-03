from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    parsed_status: str
    created_at: datetime
    metadata_summary: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class DocumentGenerateRequest(BaseModel):
    file_type: str  # 'docx', 'pptx', 'xlsx'
    title: str
    subtitle: Optional[str] = None
    prompt: Optional[str] = None
    conversation_id: Optional[str] = None

class DocumentEditRequest(BaseModel):
    document_id: str
    instructions: str
    replacements: Optional[Dict[str, str]] = None
    conversation_id: Optional[str] = None

class GeneratedDocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    generation_type: str
    diff_summary: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
