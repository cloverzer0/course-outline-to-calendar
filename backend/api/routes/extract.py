"""
Event Extraction Endpoint - Real AI Integration
"""

from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
from typing import Optional
from models.event import CalendarEventList, CourseCalendar, CourseExtractionResponse
from services. ai_service import ai_service
from services.event_storage import event_storage

router = APIRouter(
    prefix="/api/extract",
    tags=["extraction"]
)

UPLOAD_DIR = Path("data/uploads")


@router.post("/{file_id}", response_model=CourseExtractionResponse)
async def extract_events(
    file_id: str,
    session_id: Optional[str] = Query(None, description="Session ID for multi-course upload")
):
    """
    Extract calendar events from uploaded PDF using AI
    
    AI automatically detects: 
    - Course code (e.g., "PSYC1001F")
    - Course name (e.g., "Introduction to Psychology")
    - Semester (e.g., "Winter 2026")
    - Instructor name
    - All events
    
    Args:
        file_id: Unique identifier from upload endpoint
        session_id: (Optional) Session for grouping multiple courses
        
    Returns:
        CourseExtractionResponse: Course metadata + extracted events
    """
    
    # Find uploaded PDF
    matching_files = list(UPLOAD_DIR.glob(f"{file_id}_*"))
    
    if not matching_files: 
        raise HTTPException(
            status_code=404,
            detail=f"File with ID {file_id} not found"
        )
    
    file_path = str(matching_files[0])
    
    # Extract using Engineer 3's AI parser
    try:
        print(f"[Extract] Processing file: {file_path}")
        course_calendar = ai_service.extract_course_from_pdf(file_path)
        print(f"[Extract] Extracted {course_calendar.event_count} events for {course_calendar.course_code}")
        
    except Exception as e:
        print(f"[Extract] Extraction failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract events:  {str(e)}"
        )
    
    # Create session if not provided
    if not session_id: 
        session_id = event_storage.create_session()
        print(f"[Extract] Created new session: {session_id}")
    
    # Add course to session
    success = event_storage.add_course_to_session(session_id, file_id, course_calendar)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    # Return response
    return CourseExtractionResponse(
        session_id=session_id,
        course_code=course_calendar.course_code,
        course_name=course_calendar.course_name,
        semester=course_calendar.semester,
        instructor=course_calendar.instructor,
        events=course_calendar.events,
        total_events=course_calendar.event_count,
        needs_review_count=course_calendar.needs_review_count
    )


@router.get("/session/{session_id}/summary")
async def get_extraction_summary(session_id: str):
    """
    Get summary of all extracted courses in a session
    
    Args:
        session_id: Session identifier
        
    Returns:
        Summary of all courses and events
    """
    multi_course = event_storage.get_session(session_id)
    
    if not multi_course:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    # Build detailed summary
    courses_summary = []
    for course in multi_course.courses:
        # Group events by type
        event_types = {}
        for event in course.events:
            event_type = event.type.value if hasattr(event.type, 'value') else event.type
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        courses_summary.append({
            "course_code": course.course_code,
            "course_name": course.course_name,
            "semester": course.semester,
            "instructor": course.instructor,
            "event_count": course.event_count,
            "needs_review_count": course. needs_review_count,
            "event_breakdown": event_types
        })
    
    return {
        "session_id": session_id,
        "total_courses": multi_course.total_courses,
        "total_events": multi_course.total_events,
        "total_needs_review": multi_course.total_needs_review,
        "courses":  courses_summary
    }