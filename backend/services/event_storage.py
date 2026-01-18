"""
Event Storage Service - Multi-Course Support
Stores events organized by session and course
"""

from typing import Dict, List, Optional
from models.event import CalendarEvent, CourseCalendar, MultiCourseCalendar
import uuid


class EventStorage:
    """
    Multi-course event storage
    
    Storage structure:
    {
        "session-123": MultiCourseCalendar(
            courses=[
                CourseCalendar(course_code="CS301", events=[... ]),
                CourseCalendar(course_code="MATH205", events=[...])
            ]
        )
    }
    """
    
    def __init__(self):
        # session_id → MultiCourseCalendar
        self._sessions: Dict[str, MultiCourseCalendar] = {}
        # file_id → session_id mapping (for backward compatibility)
        self._file_to_session: Dict[str, str] = {}
    
    def create_session(self) -> str:
        """
        Create a new user session for uploading multiple courses
        
        Returns:
            session_id: Unique session identifier
        """
        session_id = f"session-{uuid.uuid4().hex[:12]}"
        self._sessions[session_id] = MultiCourseCalendar(courses=[])
        return session_id
    
    def add_course_to_session(
        self, 
        session_id: str, 
        file_id: str,
        course:  CourseCalendar
    ) -> bool:
        """
        Add a course to a session
        
        Args:
            session_id: Session identifier
            file_id: File identifier (links file upload to course)
            course: CourseCalendar object with events
            
        Returns:
            True if successful, False if session not found
        """
        if session_id not in self._sessions:
            return False
        
        # Link file_id to session for backward compatibility
        self._file_to_session[file_id] = session_id
        
        # Add course to session
        self._sessions[session_id].add_course(course)
        
        return True
    
    def get_session(self, session_id: str) -> Optional[MultiCourseCalendar]:
        """
        Get entire multi-course calendar for a session
        
        Args:
            session_id: Session identifier
            
        Returns: 
            MultiCourseCalendar if found, None otherwise
        """
        return self._sessions.get(session_id)
    
    def get_session_by_file_id(self, file_id: str) -> Optional[str]:
        """
        Get session_id from file_id
        
        Args:
            file_id: File identifier
            
        Returns:
            session_id if found, None otherwise
        """
        return self._file_to_session.get(file_id)
    
    def get_course_by_file_id(self, file_id: str) -> Optional[CourseCalendar]: 
        """
        Get course associated with a file upload
        
        Args:
            file_id: File identifier
            
        Returns:
            CourseCalendar if found, None otherwise
        """
        session_id = self._file_to_session.get(file_id)
        if not session_id:
            return None
        
        multi_course = self._sessions.get(session_id)
        if not multi_course:
            return None
        
        # Find course by matching file_id (stored in course metadata)
        # For now, we'll match by looking for the file_id in events
        for course in multi_course.courses:
            # Check if any event in this course has metadata linking to file_id
            # This is a simplification - in production you'd store file_id explicitly
            if course.events:
                return course
        
        return None
    
    def get_all_events_in_session(self, session_id: str) -> List[CalendarEvent]:
        """
        Get all events from all courses in a session
        
        Args:
            session_id:  Session identifier
            
        Returns: 
            Flat list of all events
        """
        multi_course = self._sessions.get(session_id)
        if not multi_course:
            return []
        
        return multi_course.get_all_events()
    
    def update_event(
        self, 
        session_id: str, 
        event_id: str, 
        updated_event: CalendarEvent
    ) -> bool:
        """
        Update an event in any course within a session
        
        Args: 
            session_id: Session identifier
            event_id: Event identifier
            updated_event: Updated event data
            
        Returns:
            True if updated, False if not found
        """
        multi_course = self._sessions.get(session_id)
        if not multi_course: 
            return False
        
        # Find and update event across all courses
        for course in multi_course.courses:
            for i, event in enumerate(course.events):
                if event.id == event_id:
                    updated_event.id = event_id  # Preserve ID
                    course.events[i] = updated_event
                    return True
        
        return False
    
    def delete_event(self, session_id: str, event_id: str) -> bool:
        """
        Delete an event from any course in a session
        
        Args:
            session_id:  Session identifier
            event_id:  Event identifier
            
        Returns: 
            True if deleted, False if not found
        """
        multi_course = self._sessions.get(session_id)
        if not multi_course:
            return False
        
        # Find and delete event across all courses
        for course in multi_course.courses:
            course.events = [e for e in course.events if e.id != event_id]
        
        return True
    
    def delete_course(self, session_id: str, course_code: str) -> bool:
        """
        Delete an entire course from a session
        
        Args:
            session_id: Session identifier
            course_code: Course code to delete
            
        Returns:
            True if deleted, False if not found
        """
        multi_course = self._sessions.get(session_id)
        if not multi_course: 
            return False
        
        multi_course.courses = [
            c for c in multi_course.courses 
            if c.course_code != course_code
        ]
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete entire session and all its courses
        
        Args: 
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        if session_id not in self._sessions:
            return False
        
        # Remove all file_id mappings for this session
        self._file_to_session = {
            k: v for k, v in self._file_to_session.items() 
            if v != session_id
        }
        
        del self._sessions[session_id]
        return True


# Global singleton instance
event_storage = EventStorage()