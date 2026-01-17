"""
Event Management Endpoints
CRUD operations for calendar events
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models.event import CalendarEvent, CalendarEventList
from services.event_storage import event_storage

router = APIRouter(
    prefix="/api/events",
    tags=["events"]
)


@router.get("/{file_id}", response_model=CalendarEventList)
async def get_events(file_id: str):
    """
    Get all events for a file upload session
    
    Used by frontend to display events for review/editing
    
    Args: 
        file_id: Upload session identifier
        
    Returns:
        CalendarEventList: All events for this session
    """
    events = event_storage.get_events(file_id)
    
    if not events: 
        # Not necessarily an error - might just be no events extracted
        return CalendarEventList(
            events=[],
            total=0,
            needsReview=0
        )
    
    needs_review_count = sum(1 for e in events if e. needsReview)
    
    return CalendarEventList(
        events=events,
        total=len(events),
        needsReview=needs_review_count
    )


@router.get("/{file_id}/{event_id}", response_model=CalendarEvent)
async def get_event(file_id: str, event_id: str):
    """
    Get a specific event
    
    Args:
        file_id: Upload session identifier
        event_id:  Event identifier
        
    Returns: 
        CalendarEvent: The requested event
        
    Raises:
        HTTPException: If event not found
    """
    event = event_storage.get_event(file_id, event_id)
    
    if not event:
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} not found in session {file_id}"
        )
    
    return event


@router.put("/{file_id}/{event_id}", response_model=CalendarEvent)
async def update_event(file_id: str, event_id: str, updated_event: CalendarEvent):
    """
    Update an existing event
    
    Used when user edits event details in the review UI
    
    Args:
        file_id: Upload session identifier
        event_id: Event identifier
        updated_event: Updated event data
        
    Returns:
        CalendarEvent: The updated event
        
    Raises:
        HTTPException: If event not found
    """
    success = event_storage.update_event(file_id, event_id, updated_event)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} not found in session {file_id}"
        )
    
    return updated_event


@router.delete("/{file_id}/{event_id}")
async def delete_event(file_id: str, event_id: str):
    """
    Delete an event
    
    Used when user removes incorrect events
    
    Args:
        file_id: Upload session identifier
        event_id: Event identifier
        
    Returns:
        Success message
        
    Raises: 
        HTTPException: If event not found
    """
    success = event_storage.delete_event(file_id, event_id)
    
    if not success: 
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} not found in session {file_id}"
        )
    
    return {
        "status": "success",
        "message": f"Event {event_id} deleted successfully"
    }


@router. get("/{file_id}/stats")
async def get_event_stats(file_id: str):
    """
    Get statistics about events in a session
    
    Useful for showing summary info in frontend
    
    Args:
        file_id: Upload session identifier
        
    Returns:
        Event statistics
    """
    stats = event_storage.get_stats(file_id)
    
    return {
        "file_id": file_id,
        "stats": stats
    }