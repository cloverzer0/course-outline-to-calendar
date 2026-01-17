"""
Event Storage Service
In-memory storage for extracted calendar events

TODO:
For hackathon purposes - stores events in memory. 
In production, replace with database (PostgreSQL, MongoDB, etc.)
"""

from typing import Dict, List, Optional
from models.event import CalendarEvent
import uuid


class EventStorage:
    """
    In-memory event storage
    
    Stores events by upload session (file_id)
    Each file upload gets a unique session with its extracted events
    """
    
    def __init__(self):
        # Storage structure: 
        # {
        #   "file_id_123": {
        #       "evt-1": CalendarEvent(... ),
        #       "evt-2": CalendarEvent(...),
        #   }
        # }
        self._storage:  Dict[str, Dict[str, CalendarEvent]] = {}
    
    def store_events(self, file_id: str, events: List[CalendarEvent]) -> int:
        """
        Store events for a file upload session
        
        Args: 
            file_id: Upload session identifier
            events: List of events to store
            
        Returns: 
            Number of events stored
        """
        # Initialize storage for this file if not exists
        if file_id not in self._storage:
            self._storage[file_id] = {}
        
        # Generate IDs for events that don't have one
        for event in events:
            if not event.id:
                event. id = f"evt-{uuid.uuid4().hex[:8]}"
            
            # Store event by its ID
            self._storage[file_id][event.id] = event
        
        return len(events)
    
    def get_events(self, file_id: str) -> List[CalendarEvent]:
        """
        Get all events for a file upload session
        
        Args:
            file_id: Upload session identifier
            
        Returns:
            List of events (empty if file_id not found)
        """
        if file_id not in self._storage:
            return []
        
        return list(self._storage[file_id].values())
    
    def get_event(self, file_id: str, event_id: str) -> Optional[CalendarEvent]:
        """
        Get a specific event
        
        Args:
            file_id: Upload session identifier
            event_id: Event identifier
            
        Returns:
            CalendarEvent if found, None otherwise
        """
        if file_id not in self._storage:
            return None
        
        return self._storage[file_id].get(event_id)
    
    def update_event(self, file_id: str, event_id: str, updated_event: CalendarEvent) -> bool:
        """
        Update an existing event
        
        Args:
            file_id: Upload session identifier
            event_id:  Event identifier
            updated_event:  Updated event data
            
        Returns:
            True if updated, False if event not found
        """
        if file_id not in self._storage:
            return False
        
        if event_id not in self._storage[file_id]: 
            return False
        
        # Preserve the original ID
        updated_event.id = event_id
        self._storage[file_id][event_id] = updated_event
        
        return True
    
    def delete_event(self, file_id: str, event_id:  str) -> bool:
        """
        Delete an event
        
        Args:
            file_id: Upload session identifier
            event_id: Event identifier
            
        Returns:
            True if deleted, False if event not found
        """
        if file_id not in self._storage:
            return False
        
        if event_id not in self._storage[file_id]:
            return False
        
        del self._storage[file_id][event_id]
        return True
    
    def delete_session(self, file_id: str) -> bool:
        """
        Delete entire upload session and all its events
        
        Args: 
            file_id: Upload session identifier
            
        Returns:
            True if deleted, False if session not found
        """
        if file_id not in self._storage:
            return False
        
        del self._storage[file_id]
        return True
    
    def get_stats(self, file_id: str) -> dict:
        """
        Get statistics about events in a session
        
        Args: 
            file_id: Upload session identifier
            
        Returns:
            Dictionary with event statistics
        """
        events = self.get_events(file_id)
        
        if not events:
            return {
                "total": 0,
                "needs_review": 0,
                "by_type": {}
            }
        
        needs_review = sum(1 for e in events if e.needsReview)
        
        # Count by type
        by_type = {}
        for event in events:
            event_type = event.type or "other"
            by_type[event_type] = by_type.get(event_type, 0) + 1
        
        return {
            "total": len(events),
            "needs_review": needs_review,
            "by_type": by_type
        }


# Global singleton instance
# TODO: In production, use dependency injection instead
event_storage = EventStorage()