"""
Event Extraction Endpoint - Multi-Course Support
"""

from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
from models.event import CalendarEvent, CalendarEventList, CourseCalendar
from services.ai_service import extract_events_from_pdf
from services.event_storage import event_storage
from config import UPLOAD_DIR

router = APIRouter(
    prefix="/api/extract",
    tags=["extraction"]
)


@router.post("/{file_id}", response_model=CalendarEventList)
async def extract_events(
    file_id: str,
    session_id: Optional[str] = Query(None, description="Session ID for multi-course upload"),
    course_code: Optional[str] = Query(None, description="Course code (e.g., 'CS301')"),
    course_name: Optional[str] = Query(None, description="Course name"),
    semester: Optional[str] = Query(None, description="Semester (e.g., 'Winter 2026')"),
    instructor: Optional[str] = Query(None, description="Instructor name")
):
    """
    Extract calendar events from uploaded PDF using AI
    
    Supports both single-course and multi-course workflows: 
    - Without session_id: Creates automatic session (backward compatible)
    - With session_id: Adds to existing multi-course session
    
    Args:
        file_id:  Unique identifier from upload endpoint
        session_id: (Optional) Session for grouping multiple courses
        course_code: (Optional) Course code for organization
        course_name: (Optional) Course name
        semester: (Optional) Semester/term
        instructor: (Optional) Instructor name
        
    Returns: 
        CalendarEventList:  Extracted events with metadata
    """
    
    # Find the uploaded file
    matching_files = list(UPLOAD_DIR. glob(f"{file_id}_*"))
    
    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID {file_id} not found"
        )
    
    file_path = str(matching_files[0])
    
    # Extract events using AI
    try:
        events = extract_events_from_pdf(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract events: {str(e)}"
        )
    
    # Create session if not provided 
    if not session_id:
        session_id = event_storage.create_session()
    
    # Create CourseCalendar
    course = CourseCalendar(
        course_code=course_code or f"COURSE-{file_id[: 8]}",
        course_name=course_name or "Untitled Course",
        semester=semester,
        instructor=instructor,
        events=events
    )
    
    # Add to session
    success = event_storage.add_course_to_session(session_id, file_id, course)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    # Count events needing review
    needs_review_count = sum(1 for event in events if event.needsReview)
    
    return CalendarEventList(
        events=events,
        total=len(events),
        needsReview=needs_review_count
    )