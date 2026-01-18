"""
AI Service Integration
Calls Engineer 3's PDF parsing and event extraction
"""

from typing import List
from models.event import CalendarEvent, CourseCalendar
from pathlib import Path
import sys
from services.pdf_parser import PDFParser

# Add ai module to path
ai_path = Path(__file__).parent.parent. parent / "ai"
sys. path.insert(0, str(ai_path))



class AIService:
    """
    Wrapper for Engineer 3's AI extraction pipeline
    """
    
    def __init__(self):
        """Initialize PDF parser"""
        self.parser = PDFParser()
    
    def extract_course_from_pdf(self, file_path: str) -> CourseCalendar:
        """
        Extract course calendar from PDF using Engineer 3's parser
        
        Args:
            file_path: Path to uploaded PDF file
            
        Returns: 
            CourseCalendar:  Parsed course with all events
            
        Raises:
            Exception: If parsing fails
        """
        try:
            print(f"[AIService] Extracting events from: {file_path}")
            
            # Call Engineer 3's parser
            course_calendar = self. parser.parse_pdf_file(file_path)
            
            print(f"[AIService] Successfully extracted {course_calendar.event_count} events")
            print(f"[AIService] Course:  {course_calendar.course_code} - {course_calendar.course_name}")
            
            return course_calendar
            
        except Exception as e:
            print(f"[AIService] Error extracting events: {str(e)}")
            raise Exception(f"Failed to extract events from PDF: {str(e)}")


# Global singleton instance
ai_service = AIService()

# Legacy function for backward compatibility
def extract_events_from_pdf(file_path: str) -> List[CalendarEvent]:
    """
    Legacy function - returns just the events list
    
    Args:
        file_path: Path to PDF file
        
    Returns: 
        List of CalendarEvent objects
    """
    course_calendar = ai_service.extract_course_from_pdf(file_path)
    return course_calendar.events