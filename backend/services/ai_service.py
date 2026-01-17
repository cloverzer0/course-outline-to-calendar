"""
AI Service Integration
Calls the AI event extraction pipeline
"""

from typing import List
from models.event import CalendarEvent, EventType
from pathlib import Path
import random


def extract_events_from_pdf(file_path: str) -> List[CalendarEvent]: 
    """
    Extract calendar events from PDF using AI
    
    THIS IS A MOCK - Replace with Engineer 3's actual implementation
    
    Args:
        file_path: Path to uploaded PDF file
        
    Returns: 
        List of extracted CalendarEvent objects
    """
    
    # TODO: Replace with Great's actual AI extraction
    # from ai.chains.course_outline_chain import extract_events
    # return extract_events(file_path)
    
    # MOCK DATA for testing. TODO: To be removed
    mock_events = [
        CalendarEvent(
            id="evt-1",
            title="CS 301 - Data Structures Lecture",
            startDateTime="2026-01-20T14:00:00",
            endDateTime="2026-01-20T16:20:00",
            location="Room 101, Science Building",
            description="Introduction to arrays and linked lists",
            type=EventType.LECTURE,
            recurrence={
                "frequency": "weekly",
                "interval": 1,
                "daysOfWeek": [1, 3],
                "endDate": "2026-04-30"
            },
            needsReview=False,
            confidence=0.95
        ),
        CalendarEvent(
            id="evt-2",
            title="Assignment 1 Due",
            startDateTime="2026-01-25T20:00:00",
            endDateTime="2026-01-25T23:59:00",
            location="Online Submission",
            description="Implement a linked list in Python",
            type=EventType.ASSIGNMENT,
            needsReview=False,
            confidence=0.88
        ),
        CalendarEvent(
            id="evt-3",
            title="Office Hours - Dr. Smith",
            startDateTime="2026-01-21T09:00:00",
            endDateTime="2026-01-21T12:00:00",
            location="Office 302B",
            description="Drop-in office hours",
            type=EventType.OFFICE_HOURS,
            recurrence={
                "frequency": "weekly",
                "interval": 1,
                "daysOfWeek": [2],
                "endDate": "2026-04-30"
            },
            needsReview=True,
            confidence=0.65
        )
    ]
    
    # Simulate some randomness (for testing)
    return mock_events[:random.randint(2, 3)]