"""
Event Extraction Endpoint
Processes uploaded PDFs and extracts calendar events using AI
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List
from models.event import CalendarEvent, CalendarEventList
from services.ai_service import extract_events_from_pdf
from config import UPLOAD_DIR
from services.event_storage import event_storage

router = APIRouter(
    prefix="/api/extract",
    tags=["extraction"]
)


@router.post("/{file_id}", response_model=CalendarEventList)
async def extract_events(file_id: str):
    """
    Extract calendar events from uploaded PDF using AI
    
    This endpoint: 
    1. Finds the uploaded PDF by file_id
    2. Calls AI extraction service
    3. Returns structured calendar events
    
    Args:
        file_id: Unique identifier from upload endpoint
        
    Returns:
        CalendarEventList:  Extracted events with metadata
        
    Raises:
        HTTPException: If file not found or extraction fails
    """
    
    # Find the file
    matching_files = list(UPLOAD_DIR.glob(f"{file_id}_*"))
    
    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID {file_id} not found.  Please upload the file first."
        )
    
    file_path = str(matching_files[0])
    
    # Extract events using ai service
    try:
        events = extract_events_from_pdf(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract events:  {str(e)}"
        )
    
    # Store events in memory for later retrieval
    event_storage.store_events(file_id, events)

    # Count events needing review
    needs_review_count = sum(1 for event in events if event.needsReview)
    
    # Return structured response
    return CalendarEventList(
        events=events,
        total=len(events),
        needsReview=needs_review_count
    )