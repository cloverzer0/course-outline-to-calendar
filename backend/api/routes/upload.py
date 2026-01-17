"""
PDF Upload Endpoint
Handles course outline PDF uploads with validation
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from datetime import datetime

# Create a router. All routes start with /api/upload
# Tag with "upload" to group endpoints in API docs
router = APIRouter(
    prefix="/api/upload",  
    tags=["upload"]  
)

# Ensure the directory exists
UPLOAD_DIR. mkdir(parents=True, exist_ok=True)


def validate_file_extension(filename: str) -> bool:
    """
    Check if file has allowed extension
    
    Args:
        filename: Name of uploaded file
        
    Returns:
        True if extension is allowed, False otherwise
    """
    file_ext = Path(filename).suffix.lower()
    return file_ext in ALLOWED_EXTENSIONS


def validate_file_size(file_size: int) -> bool:
    """
    Check if file size is within limits
    
    Args: 
        file_size: Size of file in bytes
        
    Returns: 
        True if size is acceptable, False otherwise
    """
    return 0 < file_size <= MAX_FILE_SIZE


@router.post("/")
async def upload_pdf(
    file: UploadFile = File(..., description="Course outline PDF file")
):
    """
    Upload a course outline PDF for processing
    
    Validates file type and size, saves to temporary storage,
    and returns upload confirmation with unique ID
    
    Args:
        file: PDF file from frontend
        
    Returns: 
        dict: Upload confirmation with file ID and metadata
        
    Raises:
        HTTPException: If validation fails
    """
    
    # Validation 1: Check file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only PDF files are allowed.  Got: {file.filename}"
        )
    
    # Validation 2: Read file content and check size
    file_content = await file.read()
    file_size = len(file_content)
    
    if not validate_file_size(file_size):
        raise HTTPException(
            status_code=400,
            detail=f"File size must be between 0 and {MAX_FILE_SIZE / (1024*1024)}MB. Got: {file_size / (1024*1024):.2f}MB"
        )
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    
    # Create filename:  <uuid>_<original_name>
    safe_filename = f"{file_id}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            buffer. write(file_content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Return success response
    return {
        "status": "success",
        "message": "File uploaded successfully",
        "data": {
            "file_id": file_id,
            "original_filename": file.filename,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024*1024), 2),
            "upload_timestamp": datetime.utcnow().isoformat(),
            "file_path": str(file_path)
        }
    }