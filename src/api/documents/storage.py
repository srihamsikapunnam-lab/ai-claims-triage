import os
import shutil
from pathlib import Path
from typing import Optional
import uuid
from fastapi import UploadFile

UPLOAD_DIR = Path("uploads/documents")
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def ensure_upload_directory():
    """Create upload directory if it doesn't exist"""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def validate_file(file: UploadFile) -> tuple[bool, Optional[str]]:
    """Validate uploaded file"""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    return True, None

def save_upload_file(file: UploadFile, claim_id: str) -> tuple[str, str, int]:
    """
    Save uploaded file to disk
    Returns: (filepath, filename, file_size)
    """
    ensure_upload_directory()
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    unique_filename = f"{claim_id}_{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = file_path.stat().st_size
    
    return str(file_path), unique_filename, file_size

def delete_file(filepath: str) -> bool:
    """Delete file from disk"""
    try:
        Path(filepath).unlink(missing_ok=True)
        return True
    except Exception:
        return False

def get_file_path(filename: str) -> Path:
    """Get full path for a file"""
    return UPLOAD_DIR / filename
