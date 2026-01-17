"""
Session Management Endpoints
Handles multi-course upload sessions
"""

from fastapi import APIRouter, HTTPException
from services.event_storage import event_storage

router = APIRouter(
    prefix="/api/session",
    tags=["session"]
)


@router.post("/create")
async def create_session():
    """
    Create a new multi-course upload session
    
    Returns: 
        dict: Session information with session_id
    """
    session_id = event_storage. create_session()
    
    return {
        "status": "success",
        "message": "Session created successfully",
        "session_id": session_id,
        "next_step": "Upload course outline PDFs to this session"
    }


@router.get("/{session_id}")
async def get_session(session_id:  str):
    """
    Get session details including all courses
    
    Args: 
        session_id: Session identifier
        
    Returns:
        Session summary with course list
    """
    multi_course = event_storage.get_session(session_id)
    
    if not multi_course:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    # Build course summary
    courses_summary = []
    for course in multi_course.courses:
        courses_summary.append({
            "course_code": course.course_code,
            "course_name": course.course_name,
            "semester": course.semester,
            "instructor": course.instructor,
            "event_count": course.event_count,
            "needs_review_count": course.needs_review_count
        })
    
    return {
        "session_id": session_id,
        "total_courses": multi_course.total_courses,
        "total_events": multi_course.total_events,
        "total_needs_review": multi_course.total_needs_review,
        "courses": courses_summary
    }


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """
    Delete session and all its courses
    
    Args: 
        session_id: Session identifier
        
    Returns:
        Success message
    """
    success = event_storage.delete_session(session_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    return {
        "status": "success",
        "message": f"Session {session_id} deleted successfully"
    }