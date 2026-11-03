import os
import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.core.vector_store import vector_store
from backend.app.models.entities import (
    User,
    UploadedDocument,
    DocumentMetadata,
    DocumentChunk
)
from backend.app.schemas.document import DocumentResponse
from backend.app.services.document_parser import document_parser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".docx", ".pptx", ".xlsx", ".pdf"}

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: DOCX, PPTX, XLSX, PDF."
        )

    # Secure storage filename
    doc_id = str(uuid.uuid4())
    stored_filename = f"{doc_id}{file_ext}"
    storage_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

    # Save to disk
    try:
        contents = await file.read()
        file_size = len(contents)
        if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit.")

        with open(storage_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Could not store uploaded file.")

    # Create UploadedDocument entity
    db_doc = UploadedDocument(
        id=doc_id,
        user_id=current_user.id,
        conversation_id=conversation_id if conversation_id and conversation_id != "null" else None,
        filename=file.filename,
        file_type=file_ext.strip("."),
        file_size=file_size,
        storage_path=storage_path,
        parsed_status="processing"
    )
    db.add(db_doc)
    db.commit()

    # Deep Document Parsing & Layout Analysis
    try:
        full_text, metadata_summary, raw_chunks = document_parser.parse_document(
            file_path=storage_path,
            file_type=file_ext.strip(".")
        )

        # Store Document Metadata in DB
        db_meta = DocumentMetadata(
            document_id=doc_id,
            structure_summary=metadata_summary
        )
        db.add(db_meta)

        # Index chunks in ChromaDB & DB
        chroma_chunks = []
        for idx, rc in enumerate(raw_chunks):
            c_id = f"{doc_id}_chunk_{idx}"
            chunk_text = rc.get("text", "")
            chunk_meta = rc.get("metadata", {})
            chunk_meta.update({
                "document_id": doc_id,
                "user_id": current_user.id,
                "filename": file.filename,
                "file_type": file_ext.strip(".")
            })

            chroma_chunks.append({
                "id": c_id,
                "text": chunk_text,
                "metadata": chunk_meta
            })

            db_chunk = DocumentChunk(
                document_id=doc_id,
                user_id=current_user.id,
                chunk_index=idx,
                content=chunk_text,
                metadata_json=chunk_meta,
                chroma_id=c_id
            )
            db.add(db_chunk)

        # Add to ChromaDB vector collection
        if chroma_chunks:
            vector_store.add_chunks(chroma_chunks)

        db_doc.parsed_status = "completed"
        db.commit()
        db.refresh(db_doc)

    except Exception as exc:
        logger.error(f"Error parsing document structure: {exc}", exc_info=True)
        db_doc.parsed_status = "failed"
        metadata_summary = {"error": str(exc)}
        db.commit()

    res = DocumentResponse(
        id=db_doc.id,
        filename=db_doc.filename,
        file_type=db_doc.file_type,
        file_size=db_doc.file_size,
        parsed_status=db_doc.parsed_status,
        created_at=db_doc.created_at,
        metadata_summary=metadata_summary
    )
    return res

@router.get("", response_model=List[DocumentResponse])
@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    docs = db.query(UploadedDocument).filter(
        UploadedDocument.user_id == current_user.id
    ).order_by(UploadedDocument.created_at.desc()).all()

    resp = []
    for d in docs:
        resp.append(DocumentResponse(
            id=d.id,
            filename=d.filename,
            file_type=d.file_type,
            file_size=d.file_size,
            parsed_status=d.parsed_status,
            created_at=d.created_at,
            metadata_summary=d.doc_metadata.structure_summary if d.doc_metadata else None
        ))
    return resp

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    d = db.query(UploadedDocument).filter(
        UploadedDocument.id == document_id,
        UploadedDocument.user_id == current_user.id
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail="Document not found.")

    return DocumentResponse(
        id=d.id,
        filename=d.filename,
        file_type=d.file_type,
        file_size=d.file_size,
        parsed_status=d.parsed_status,
        created_at=d.created_at,
        metadata_summary=d.doc_metadata.structure_summary if d.doc_metadata else None
    )

@router.get("/{document_id}/download")
def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    d = db.query(UploadedDocument).filter(
        UploadedDocument.id == document_id,
        UploadedDocument.user_id == current_user.id
    ).first()
    if not d or not os.path.exists(d.storage_path):
        raise HTTPException(status_code=404, detail="Document file not found on disk.")

    return FileResponse(
        path=d.storage_path,
        filename=d.filename,
        media_type="application/octet-stream"
    )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    d = db.query(UploadedDocument).filter(
        UploadedDocument.id == document_id,
        UploadedDocument.user_id == current_user.id
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove Chroma chunks
    vector_store.delete_document_chunks(document_id)

    # Remove file on disk if exists
    if os.path.exists(d.storage_path):
        try:
            os.remove(d.storage_path)
        except Exception:
            pass

    db.delete(d)
    db.commit()
    return None
