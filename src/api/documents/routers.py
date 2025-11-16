from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List
import sqlite3
from datetime import datetime

from .models import DocumentResponse, DocumentType
from .storage import save_upload_file, validate_file, delete_file, get_file_path
from ..auth.routers import get_current_user
from ..auth.models import TokenData
from ..database import get_db_connection

router = APIRouter()

@router.post("/claims/{claim_id}/documents", response_model=DocumentResponse)
async def upload_document(
    claim_id: str,
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    description: str = Form(None),
    current_user: TokenData = Depends(get_current_user)
):
    """Upload a document for a claim"""
    
    # Validate file
    is_valid, error_msg = validate_file(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if claim exists and belongs to user (or user is admin)
        cursor.execute("""
            SELECT user_id FROM claims WHERE id = ?
        """, (claim_id,))
        
        claim = cursor.fetchone()
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found"
            )
        
        # Check ownership (customers can only upload to their own claims)
        if current_user.role == "customer" and claim[0] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to upload documents for this claim"
            )
        
        # Save file to disk
        filepath, filename, file_size = save_upload_file(file, claim_id)
        
        # Save document metadata to database
        cursor.execute("""
            INSERT INTO documents (
                claim_id, filename, filepath, document_type, file_size,
                uploaded_by, uploaded_at, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim_id, filename, filepath, document_type.value,
            file_size, current_user.user_id, datetime.utcnow(), description
        ))
        
        conn.commit()
        doc_id = cursor.lastrowid
        
        # Fetch created document
        cursor.execute("""
            SELECT id, claim_id, filename, document_type, file_size,
                   uploaded_at, uploaded_by, description
            FROM documents WHERE id = ?
        """, (doc_id,))
        
        doc = cursor.fetchone()
        
        return DocumentResponse(
            id=doc[0],
            claim_id=doc[1],
            filename=doc[2],
            document_type=doc[3],
            file_size=doc[4],
            uploaded_at=doc[5],
            uploaded_by=doc[6],
            description=doc[7]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )
    finally:
        conn.close()

@router.get("/claims/{claim_id}/documents", response_model=List[DocumentResponse])
async def get_claim_documents(
    claim_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get all documents for a claim"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if claim exists and user has access
        cursor.execute("""
            SELECT user_id FROM claims WHERE id = ?
        """, (claim_id,))
        
        claim = cursor.fetchone()
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found"
            )
        
        # Check access (customers can only see their own claims)
        if current_user.role == "customer" and claim[0] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view documents for this claim"
            )
        
        # Fetch documents
        cursor.execute("""
            SELECT id, claim_id, filename, document_type, file_size,
                   uploaded_at, uploaded_by, description
            FROM documents
            WHERE claim_id = ?
            ORDER BY uploaded_at DESC
        """, (claim_id,))
        
        documents = cursor.fetchall()
        
        return [
            DocumentResponse(
                id=doc[0],
                claim_id=doc[1],
                filename=doc[2],
                document_type=doc[3],
                file_size=doc[4],
                uploaded_at=doc[5],
                uploaded_by=doc[6],
                description=doc[7]
            )
            for doc in documents
        ]
        
    finally:
        conn.close()

@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Download a document"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Fetch document
        cursor.execute("""
            SELECT d.filepath, d.filename, d.claim_id, c.user_id
            FROM documents d
            JOIN claims c ON d.claim_id = c.id
            WHERE d.id = ?
        """, (document_id,))
        
        doc = cursor.fetchone()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check access
        if current_user.role == "customer" and doc[3] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to download this document"
            )
        
        file_path = get_file_path(doc[1])
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on server"
            )
        
        return FileResponse(
            path=file_path,
            filename=doc[1],
            media_type="application/octet-stream"
        )
        
    finally:
        conn.close()

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a document"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Fetch document
        cursor.execute("""
            SELECT d.filepath, d.filename, d.claim_id, c.user_id
            FROM documents d
            JOIN claims c ON d.claim_id = c.id
            WHERE d.id = ?
        """, (document_id,))
        
        doc = cursor.fetchone()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check access (only document owner or admin can delete)
        if current_user.role == "customer" and doc[3] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this document"
            )
        
        # Delete file from disk
        delete_file(doc[0])
        
        # Delete from database
        cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        conn.commit()
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
    finally:
        conn.close()
