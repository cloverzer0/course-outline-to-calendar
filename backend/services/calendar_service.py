"""
Calendar Generation Service
Integration with ICS Generator
"""

from typing import List
from models.event import CalendarEvent, MultiCourseCalendar
from services. ics_generator import ICSGenerator
import os


def generate_multi_course_ics(multi_course:  MultiCourseCalendar, session_id: str) -> str:
    """
    Generate . ics file from multiple courses using generator
    
    Args:
        multi_course: MultiCourseCalendar with all courses
        session_id:  Session identifier (used for filename)
        
    Returns: 
        Path to generated .ics file
    """
    # Create ics generator
    generator = ICSGenerator(timezone="America/Toronto")
    
    # Get all events from all courses
    all_events = multi_course.get_all_events()
    
    if not all_events:
        raise ValueError("No events to export")
    
    # Generate .ics content
    calendar_name = f"Course Schedule - {multi_course.total_courses} Courses"
    ics_content = generator.generate_ics(all_events, calendar_name)
    
    # Save to file
    output_dir = "data/calendars"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"multi_course_{session_id}.ics"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(ics_content)
    
    return filepath


def generate_single_course_ics(events: List[CalendarEvent], file_id: str) -> str:
    """
    Generate .ics file from single course (backward compatibility)
    
    Args:
        events: List of calendar events
        file_id: File identifier (used for filename)
        
    Returns:
        Path to generated .ics file
    """
    generator = ICSGenerator(timezone="America/Toronto")
    
    ics_content = generator.generate_ics(events, "Course Calendar")
    
    # Save to file
    output_dir = "data/calendars"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"course_{file_id}.ics"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(ics_content)
    
    return filepath