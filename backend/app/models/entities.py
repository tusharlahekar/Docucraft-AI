import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, BigInteger, 
    DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    uploaded_documents = relationship("UploadedDocument", back_populates="user", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDocument", back_populates="user", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    uploaded_documents = relationship("UploadedDocument", back_populates="conversation")
    generated_documents = relationship("GeneratedDocument", back_populates="conversation")
    research_sources = relationship("ResearchSource", back_populates="conversation", cascade="all, delete-orphan")
    agent_logs = relationship("AgentExecutionLog", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    citations = Column(JSON, default=list)  # list of {title, url, snippet}
    attached_doc_ids = Column(JSON, default=list)  # list of doc ids
    generated_doc_ids = Column(JSON, default=list)  # list of generated doc ids
    agent_logs = Column(JSON, default=list)  # execution trail
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # 'docx', 'pptx', 'xlsx', 'pdf'
    file_size = Column(BigInteger, nullable=False)
    storage_path = Column(String(500), nullable=False)
    parsed_status = Column(String(20), default="pending")  # 'pending', 'processing', 'completed', 'failed'
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    user = relationship("User", back_populates="uploaded_documents")
    conversation = relationship("Conversation", back_populates="uploaded_documents")
    doc_metadata = relationship("DocumentMetadata", back_populates="document", uselist=False, cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    derived_documents = relationship("GeneratedDocument", back_populates="source_document")

class DocumentMetadata(Base):
    __tablename__ = "document_metadata"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), unique=True, nullable=False)
    structure_summary = Column(JSON, default=dict)  # structured JSON of headings, tables, slides, styles
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    document = relationship("UploadedDocument", back_populates="doc_metadata")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)
    chroma_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    document = relationship("UploadedDocument", back_populates="chunks")

class GeneratedDocument(Base):
    __tablename__ = "generated_documents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    source_document_id = Column(String(36), ForeignKey("uploaded_documents.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # 'docx', 'pptx', 'xlsx'
    file_size = Column(BigInteger, default=0)
    storage_path = Column(String(500), nullable=False)
    generation_type = Column(String(50), default="created_from_scratch")  # 'created_from_scratch', 'edited_from_source'
    diff_summary = Column(JSON, default=dict)  # changes description
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    user = relationship("User", back_populates="generated_documents")
    conversation = relationship("Conversation", back_populates="generated_documents")
    source_document = relationship("UploadedDocument", back_populates="derived_documents")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)
    change_description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    document = relationship("UploadedDocument", back_populates="versions")

class ResearchSource(Base):
    __tablename__ = "research_sources"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    query = Column(Text, nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    snippet = Column(Text, nullable=True)
    retrieval_date = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="research_sources")

class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    step_name = Column(String(100), nullable=False)
    input_state_summary = Column(JSON, default=dict)
    output_state_summary = Column(JSON, default=dict)
    execution_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="agent_logs")
