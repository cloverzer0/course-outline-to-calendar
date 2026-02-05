"""
Combined Upload + Extract Endpoint
Simpler workflow for hackathon
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pathlib import Path
from typing import Optional
import uuid
import shutil
from datetime import datetime

from models.event import CourseCalendar, MultiCourseCalendar
from services.event_storage import event_storage
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE,   UPLOAD_DIR


router = APIRouter(
    prefix="/api/process",
    tags=["combined"]
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload-and-extract")
async def upload_and_extract(
    file: UploadFile = File(..., description="Course outline PDF file"),
    session_id: Optional[str] = Query(None, description="Session ID for multi-course upload")
):
    """
    COMBINED ENDPOINT:  Upload PDF + Extract Events + Return JSON
    
    This endpoint does EVERYTHING in one call:
    1. Validate and save PDF file
    2. Call Engineer 3's AI to extract events
    3. Store in session
    4. Return course metadata + events as JSON
    
    Perfect for simple frontend integration!
    
    Args:
        file: Course outline PDF
        session_id:  (Optional) Session for grouping multiple courses
        
    Returns:
        dict: Contains session_id and MultiCourseCalendar data with all courses in session
        
    Raises:
        HTTPException: If upload, extraction, or storage fails
    """
    
    # ========================================
    # STEP 1: VALIDATE FILE
    # ========================================
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS: 
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only PDF files allowed. Got: {file. filename}"
        )
    
    # Validate file size
    file_content = await file.read()
    file_size = len(file_content)
    
    if not (0 < file_size <= MAX_FILE_SIZE):
        raise HTTPException(
            status_code=400,
            detail=f"File size must be between 0 and {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # ========================================
    # STEP 2: SAVE PDF TO DISK
    # ========================================
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        print(f"[Combined] Saved file: {file_path}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # ========================================
    # STEP 3: EXTRACT EVENTS WITH AI
    # ========================================
    
    try: 
        print(f"[Combined] Starting AI extraction for:  {file.filename}")
        # Lazy import to avoid loading heavy AI libraries at startup
        from services.ai_service import ai_service
        course_calendar = ai_service.extract_course_from_pdf(str(file_path))
        print(f"[Combined] ✓ Extracted {course_calendar.event_count} events for {course_calendar.course_code}")
        
    except Exception as e:
        print(f"[Combined] ✗ AI extraction failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract events from PDF: {str(e)}"
        )
    
    # ========================================
    # STEP 4: CREATE/USE SESSION
    # ========================================
    
    if not session_id:
        session_id = event_storage.create_session()
        print(f"[Combined] Created new session: {session_id}")
    
    # ========================================
    # STEP 5: STORE IN SESSION
    # ========================================
    
    success = event_storage.add_course_to_session(session_id, file_id, course_calendar)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    print(f"[Combined] Stored course in session {session_id}")
    
    # ========================================
    # STEP 6: GET ALL COURSES IN SESSION
    # ========================================
    
    multi_course = event_storage.get_session(session_id)
    
    if not multi_course:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve session after adding course"
        )
    
    # ========================================
    # STEP 7: RETURN JSON RESPONSE
    # ========================================
    
    return {
        "session_id": session_id,
        **multi_course.model_dump()
    }