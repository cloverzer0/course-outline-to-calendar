"""
ICS (iCalendar) File Generator
Engineer 4 - Calendar Generation, Validation & QA

Responsibilities:
- Generate .ics files from event data
- Support one-time and recurring events (RRULE)
- Ensure compatibility with Google Calendar, Apple Calendar, Outlook
- Handle time zones correctly
"""

from icalendar import Calendar, Event as ICalEvent, Alarm
from datetime import datetime, timedelta
from typing import List, Optional
import pytz


class ICSGenerator:
    """Generate iCalendar (.ics) format files from event data"""
    
    def __init__(self, timezone: str = "America/Toronto"):
        """
        Initialize ICS Generator
        
        Args:
            timezone: Default timezone for events (default: America/Toronto)
        """
        self.default_timezone = pytz.timezone(timezone)
    
    def generate_ics(
        self, 
        events: List, 
        calendar_name: str = "Course Calendar"
    ) -> str:
        """
        Generate .ics file content from list of events
        
        Args:
            events: List of event dictionaries or Pydantic models
            calendar_name: Name for the calendar
            
        Returns:
            String containing .ics file content
            
        Raises:
            ValueError: If events list is empty or invalid
        """
        if not events:
            raise ValueError("Cannot generate calendar from empty events list")
        
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//Course Outline to Calendar//EN')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', calendar_name)
        cal.add('x-wr-timezone', str(self.default_timezone))
        
        # Add each event
        for event_data in events:
            try:
                # Convert Pydantic model to dict if needed
                if hasattr(event_data, 'model_dump'):
                    event_dict = event_data.model_dump()
                else:
                    event_dict = event_data
                    
                ical_event = self._create_event(event_dict)
                cal.add_component(ical_event)
            except Exception as e:
                # Log error but continue processing other events
                title = event_data.title if hasattr(event_data, 'title') else event_data.get('title', 'Unknown')
                print(f"Warning: Failed to add event {title}: {str(e)}")
        
        return cal.to_ical().decode('utf-8')
    
    def _create_event(self, event_data: dict) -> ICalEvent:
        """
        Create an iCalendar event from event data
        
        Args:
            event_data: Dictionary containing event information with startDateTime and endDateTime
            
        Returns:
            ICalEvent object
        """
        event = ICalEvent()
        
        # Required fields
        event.add('summary', event_data['title'])
        event.add('uid', event_data.get('id', self._generate_uid(event_data)))
        
        # Parse startDateTime and endDateTime in ISO format
        start_dt = datetime.fromisoformat(event_data['startDateTime'])
        end_dt = datetime.fromisoformat(event_data['endDateTime'])
        
        # Make timezone aware if not already
        if start_dt.tzinfo is None:
            start_dt = self.default_timezone.localize(start_dt)
        if end_dt.tzinfo is None:
            end_dt = self.default_timezone.localize(end_dt)
        
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        
        # Required location field
        event.add('location', event_data['location'])
        
        # Optional description
        if event_data.get('description'):
            event.add('description', event_data['description'])
        
        # Event type as category
        event_type = event_data.get('type', 'other')
        event.add('categories', [event_type.upper()])
        
        # Add recurrence rule if present
        if event_data.get('recurrence'):
            rrule = self._create_recurrence_rule(event_data['recurrence'])
            event.add('rrule', rrule)
        
        # Add alarm/reminder
        if not event_data.get('recurrence'):  # Only add alarms to non-recurring events
            alarm = self._create_alarm(event_type)
            event.add_component(alarm)
        
        return event
    
    def _parse_datetime(self, date_str: str, time_str: str) -> datetime:
        """
        Parse date and time strings into timezone-aware datetime (legacy format support)
        
        Args:
            date_str: Date in YYYY-MM-DD format
            time_str: Time in HH:MM format
            
        Returns:
            Timezone-aware datetime object
        """
        # Combine date and time
        dt_str = f"{date_str} {time_str}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        
        # Make timezone aware
        dt = self.default_timezone.localize(dt)
        
        return dt
    
    def _create_recurrence_rule(self, recurrence: dict) -> dict:
        """
        Create RRULE for recurring events
        
        Args:
            recurrence: Dictionary with recurrence configuration
            
        Returns:
            RRULE dictionary
        """
        rule = {}
        
        # Frequency mapping
        freq_map = {
            'daily': 'DAILY',
            'weekly': 'WEEKLY',
            'monthly': 'MONTHLY'
        }
        frequency = recurrence.get('frequency', 'weekly').lower()
        rule['FREQ'] = [freq_map.get(frequency, 'WEEKLY')]
        
        # Interval
        if recurrence.get('interval'):
            rule['INTERVAL'] = [recurrence['interval']]
        
        # End date
        if recurrence.get('endDate'):
            end_dt = datetime.strptime(recurrence['endDate'], "%Y-%m-%d")
            end_dt = self.default_timezone.localize(end_dt.replace(hour=23, minute=59))
            rule['UNTIL'] = [end_dt]
        
        # Days of week (for weekly recurrence)
        if recurrence.get('daysOfWeek'):
            days_map = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA']
            byday = [days_map[day] for day in recurrence['daysOfWeek']]
            rule['BYDAY'] = byday
        
        return rule
    
    def _create_alarm(self, event_type: str) -> Alarm:
        """
        Create reminder alarm based on event type
        
        Args:
            event_type: Type of event (exam, assignment, lecture, etc.)
            
        Returns:
            Alarm component
        """
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        
        # Set reminder time based on event type
        reminder_config = {
            'exam': (timedelta(days=-1), 'Exam tomorrow!'),
            'assignment': (timedelta(days=-2), 'Assignment due in 2 days'),
            'lecture': (timedelta(minutes=-30), 'Class starts in 30 minutes'),
            'project': (timedelta(days=-3), 'Project deadline in 3 days'),
            'other': (timedelta(hours=-1), 'Event starting soon')
        }
        
        trigger, description = reminder_config.get(
            event_type, 
            reminder_config['other']
        )
        
        alarm.add('trigger', trigger)
        alarm.add('description', description)
        
        return alarm
    
    def _generate_uid(self, event_data: dict) -> str:
        """
        Generate a unique identifier for an event
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            UID string
        """
        import uuid
        # Use UUID4 for unique ID
        return str(uuid.uuid4())
    
    def validate_compatibility(self, ics_content: str) -> dict:
        """
        Validate .ics content for compatibility with major calendar applications
        
        Args:
            ics_content: Generated .ics file content
            
        Returns:
            Dictionary with compatibility results
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Parse the calendar to validate
            Calendar.from_ical(ics_content)
            
            # Check for required components
            if 'BEGIN:VCALENDAR' not in ics_content:
                results['errors'].append('Missing VCALENDAR component')
                results['is_valid'] = False
            
            if 'VERSION:2.0' not in ics_content:
                results['errors'].append('Missing or incorrect VERSION')
                results['is_valid'] = False
            
            # Warnings for best practices
            if 'PRODID' not in ics_content:
                results['warnings'].append('Missing PRODID (recommended)')
            
        except Exception as e:
            results['is_valid'] = False
            results['errors'].append(f'Parse error: {str(e)}')
        
        return results   
     
    def save_calendar_to_file(self, cal: Calendar, filename: str):
        """
        Save calendar to .ics file
        
        Args:
            cal: Calendar object to save
            filename: Path to save the .ics file
        """
        with open(filename, 'wb') as f:
            f.write(cal.to_ical())
        print(f"Calendar saved to {filename}")