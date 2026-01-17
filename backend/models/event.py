"""
Calendar Event Data Model
Shared by Engineers 1, 2, 3, and 4

This is the unified data structure for all calendar events.
Any changes to this model impact the entire system:
- Frontend rendering (Engineer 1)
- AI extraction output (Engineer 3)
- Backend validation (Engineer 2)
- Calendar generation (Engineer 4)
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum


class EventType(str, Enum):
    """Type of academic event"""
    LECTURE = "lecture"
    EXAM = "exam"
    ASSIGNMENT = "assignment"
    PROJECT = "project"
    OFFICE_HOURS = "office_hours"
    OTHER = "other"


class RecurrenceFrequency(str, Enum):
    """Frequency for recurring events"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RecurrenceRule(BaseModel):
    """
    Recurrence rules for repeating events
    Based on iCalendar RRULE specification
    """
    frequency: RecurrenceFrequency = Field(
        ...,
        description="How often the event repeats (daily, weekly, monthly)"
    )
    interval: Optional[int] = Field(
        default=1,
        ge=1,
        description="Interval between occurrences (e.g., every 2 weeks)"
    )
    daysOfWeek: Optional[List[int]] = Field(
        default=None,
        description="Days of week for weekly recurrence (0=Sunday, 6=Saturday)"
    )
    endDate: Optional[str] = Field(
        default=None,
        description="End date for recurrence in YYYY-MM-DD format"
    )
    count: Optional[int] = Field(
        default=None,
        ge=1,
        description="Number of occurrences (alternative to endDate)"
    )

    @field_validator('daysOfWeek')
    @classmethod
    def validate_days_of_week(cls, v):
        """Ensure days of week are valid (0-6)"""
        if v is not None:
            if not all(0 <= day <= 6 for day in v):
                raise ValueError("Days of week must be between 0 (Sunday) and 6 (Saturday)")
        return v


class CalendarEvent(BaseModel):
    """
    Unified calendar event data model
    
    This schema is used across the entire application:
    - AI extraction outputs this format
    - Backend API validates against this
    - Frontend renders this structure
    - Calendar generator converts this to .ics
    """
    
    # Required fields
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Event title or course name"
    )
    
    startDateTime: str = Field(
        ...,
        description="Start date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
    )
    
    endDateTime: str = Field(
        ...,
        description="End date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
    )
    
    location: str = Field(
        ...,
        description="Physical location or virtual meeting link"
    )
    
    recurrence: Optional[RecurrenceRule] = Field(
        default=None,
        description="Recurrence rules for repeating events (None for one-time events)"
    )
    
    # Optional fields
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional event details or notes"
    )
    
    type: Optional[EventType] = Field(
        default=EventType.OTHER,
        description="Type of event (lecture, exam, assignment, etc.)"
    )
    
    # System fields (optional)
    id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the event"
    )
    
    needsReview: Optional[bool] = Field(
        default=False,
        description="Flag indicating if the event needs user review (low confidence extraction)"
    )
    
    confidence: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="AI extraction confidence score (0.0 to 1.0)"
    )

    @field_validator('startDateTime', 'endDateTime')
    @classmethod
    def validate_datetime_format(cls, v):
        """Ensure datetime strings are in valid ISO 8601 format"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Invalid datetime format: {v}. Expected ISO 8601 (YYYY-MM-DDTHH:MM:SS)")
        return v

    @field_validator('endDateTime')
    @classmethod
    def validate_end_after_start(cls, v, info):
        """Ensure end datetime is after start datetime"""
        if 'startDateTime' in info.data:
            start = datetime.fromisoformat(info.data['startDateTime'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(v.replace('Z', '+00:00'))
            if end <= start:
                raise ValueError("End datetime must be after start datetime")
        return v

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "title": "CS 301 - Data Structures",
                "startDateTime": "2026-01-20T14:00:00",
                "endDateTime": "2026-01-20T15:20:00",
                "location": "Room 101, Science Building",
                "description": "Introduction to data structures and algorithms",
                "type": "lecture",
                "recurrence": {
                    "frequency": "weekly",
                    "interval": 1,
                    "daysOfWeek": [1, 3],  # Monday and Wednesday
                    "endDate": "2026-04-30"
                },
                "needsReview": False,
                "confidence": 0.95
            }
        }
    )


class CalendarEventList(BaseModel):
    """
    Response model for multiple events
    Used by API endpoints returning event collections
    """
    events: List[CalendarEvent] = Field(
        ...,
        description="List of calendar events"
    )
    total: int = Field(
        ...,
        description="Total number of events"
    )
    needsReview: Optional[int] = Field(
        default=0,
        description="Number of events flagged for review"
    )


# Legacy format support for backward compatibility
# This maps to the simplified format used in tests
def from_simple_format(event_dict: dict) -> CalendarEvent:
    """
    Convert simplified event format to CalendarEvent model
    
    Simple format (used in tests):
    {
        'title': 'Event Title',
        'date': '2026-02-15',
        'time': '10:00',
        'duration': 50,
        'type': 'lecture',
        'location': 'Room 101',
        'description': 'Description',
        'recurrence': {...}
    }
    
    Args:
        event_dict: Event in simple format
        
    Returns:
        CalendarEvent instance
    """
    from datetime import datetime, timedelta
    
    # Parse date and time
    date_str = event_dict['date']
    time_str = event_dict.get('time', '00:00')
    start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    
    # Calculate end time
    duration = event_dict.get('duration', 60)
    end_dt = start_dt + timedelta(minutes=duration)
    
    # Convert to ISO format
    return CalendarEvent(
        title=event_dict['title'],
        startDateTime=start_dt.isoformat(),
        endDateTime=end_dt.isoformat(),
        location=event_dict.get('location', 'TBD'),
        description=event_dict.get('description'),
        type=event_dict.get('type', 'other'),
        recurrence=event_dict.get('recurrence'),
        id=event_dict.get('id'),
        needsReview=event_dict.get('needsReview', False),
        confidence=event_dict.get('confidence', 1.0)
    )
