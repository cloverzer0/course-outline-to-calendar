"""
Calendar Export Endpoint - Multi-Course Support
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.event_storage import event_storage
from services.calendar_service import generate_multi_course_ics, generate_single_course_ics
import os

router = APIRouter(
    prefix="/api/calendar",
    tags=["calendar"]
)


@router.post("/export/session/{session_id}")
async def export_multi_course_calendar(session_id: str):
    """
    Export ALL courses in a session to single .ics file
    
    This is the main export endpoint for multi-course workflow.
    Generates one calendar file containing all uploaded courses.
    
    Args:
        session_id: Session identifier
        
    Returns:
        FileResponse:  Downloadable . ics file with all courses
    """
    # Get session
    multi_course = event_storage.get_session(session_id)
    
    if not multi_course:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    if multi_course.total_events == 0:
        raise HTTPException(
            status_code=400,
            detail="No events to export.  Please upload and extract course outlines first."
        )
    
    # Generate . ics file using Engineer 4's generator
    try:
        ics_filepath = generate_multi_course_ics(multi_course, session_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate calendar: {str(e)}"
        )
    
    # Check file exists
    if not os.path.exists(ics_filepath):
        raise HTTPException(
            status_code=500,
            detail="Calendar generation failed"
        )
    
    # Return file for download
    return FileResponse(
        path=ics_filepath,
        media_type="text/calendar",
        filename=f"my_courses_{session_id}.ics",
        headers={
            "Content-Disposition":  f'attachment; filename="my_courses_{session_id}. ics"'
        }
    )


@router.post("/export/file/{file_id}")
async def export_single_course_calendar(file_id: str):
    """
    Export single course to . ics file (backward compatibility)
    
    Args:
        file_id: File identifier
        
    Returns: 
        FileResponse: Downloadable . ics file
    """
    # Get session from file_id
    session_id = event_storage.get_session_by_file_id(file_id)
    
    if not session_id:
        raise HTTPException(
            status_code=404,
            detail=f"No session found for file {file_id}"
        )
    
    # Get course
    course = event_storage.get_course_by_file_id(file_id)
    
    if not course or not course.events:
        raise HTTPException(
            status_code=404,
            detail="No events found for this file"
        )
    
    # Generate .ics file
    try:
        ics_filepath = generate_single_course_ics(course.events, file_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate calendar: {str(e)}"
        )
    
    # Return file
    return FileResponse(
        path=ics_filepath,
        media_type="text/calendar",
        filename=f"{course.course_code}_calendar.ics",
        headers={
            "Content-Disposition":  f'attachment; filename="{course.course_code}_calendar. ics"'
        }
    )


@router.get("/preview/session/{session_id}")
async def preview_multi_course_calendar(session_id: str):
    """
    Preview multi-course calendar content
    
    Args:
        session_id: Session identifier
        
    Returns:
        Calendar summary
    """
    multi_course = event_storage.get_session(session_id)
    
    if not multi_course:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    return {
        "session_id":  session_id,
        "total_courses": multi_course.total_courses,
        "total_events": multi_course.total_events,
        "courses": [
            {
                "course_code": c.course_code,
                "course_name": c.course_name,
                "event_count": c.event_count
            }
            for c in multi_course.courses
        ]
    }