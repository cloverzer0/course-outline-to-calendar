"""
Event Validator
Engineer 4 - Calendar Generation, Validation & QA

Responsibilities:
- Validate event data before calendar generation
- Check date/time formats and time zones
- Deduplicate events
- Handle edge cases
- Provide consistent error messages
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import pytz
import re


class ValidationError:
    """Represents a validation error or warning"""
    
    def __init__(self, field: str, message: str, severity: str = 'error'):
        self.field = field
        self.message = message
        self.severity = severity  # 'error' or 'warning'
    
    def to_dict(self) -> dict:
        return {
            'field': self.field,
            'message': self.message,
            'severity': self.severity
        }


class ValidationResult:
    """Result of event validation"""
    
    def __init__(self):
        self.is_valid = True
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def add_error(self, field: str, message: str):
        """Add a validation error"""
        self.errors.append(ValidationError(field, message, 'error'))
        self.is_valid = False
    
    def add_warning(self, field: str, message: str):
        """Add a validation warning"""
        self.warnings.append(ValidationError(field, message, 'warning'))
    
    def to_dict(self) -> dict:
        return {
            'is_valid': self.is_valid,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': [w.to_dict() for w in self.warnings]
        }


class EventValidator:
    """Validates calendar events for correctness and consistency"""
    
    # Supported event types
    VALID_EVENT_TYPES = {'lecture', 'exam', 'assignment', 'project', 'other'}
    
    # Date/time format patterns
    DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'  # YYYY-MM-DD
    TIME_PATTERN = r'^([01]\d|2[0-3]):([0-5]\d)$'  # HH:MM (24-hour)
    ISO_DATETIME_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$'  # ISO 8601
    
    def __init__(self, timezone: str = "America/Toronto"):
        """
        Initialize Event Validator
        
        Args:
            timezone: Default timezone for validation
        """
        self.timezone = pytz.timezone(timezone)
    
    def validate_event(self, event_data: dict) -> ValidationResult:
        """
        Validate a single event
        Supports both old format (date/time/duration) and new format (startDateTime/endDateTime)
        
        Args:
            event_data: Dictionary containing event information
            
        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult()
        
        # Determine format (old or new)
        is_new_format = 'startDateTime' in event_data
        
        # Validate required fields
        self._validate_required_fields(event_data, result, is_new_format)
        
        # Validate field formats
        self._validate_title(event_data, result)
        
        if is_new_format:
            # New unified model format
            self._validate_start_datetime(event_data, result)
            self._validate_end_datetime(event_data, result)
            self._validate_location(event_data, result, required=True)
        else:
            # Old format (backward compatibility)
            self._validate_date(event_data, result)
            self._validate_time(event_data, result)
            self._validate_duration(event_data, result)
            self._validate_location(event_data, result, required=False)
        
        self._validate_type(event_data, result)
        
        # Validate optional fields, is_new_format: bool = False):
        """Check that all required fields are present"""
        if is_new_format:
            # New unified model format
            required_fields = ['title', 'startDateTime', 'endDateTime', 'location']
        else:
            # Old format (backward compatibility)
            required_fields = ['title', 'dat
        # Validate recurrence if present
        if event_data.get('recurrence'):
            self._validate_recurrence(event_data, result, is_new_format)
        
        # Check for logical consistency
        self._validate_date_not_too_far_past(event_data, result, is_new_format)
        self._validate_date_not_too_far_future(event_data, result, is_new_format)
        
        return result
    
    def _validate_required_fields(self, event_data: dict, result: ValidationResult):
        """Check that all required fields are present"""
        required_fields = ['title', 'date', 'time', 'type']
        
        for field in required_fields:
            if field not in event_data or not event_data[field]:
                result.add_error(field, f'{field.capitalize()} is required')
    
    def _validate_title(self, event_data: dict, result: ValidationResult):
        """Validate event title"""
        if 'title' not in event_data:
            return
        
        title = event_data['title']
        
        if not isinstance(title, str):
            result.add_error('title', 'Title must be a string')
            return
        
        if len(title.strip()) < 3:
            resultstart_datetime(self, event_data: dict, result: ValidationResult):
        """Validate startDateTime in ISO 8601 format"""
        if 'startDateTime' not in event_data:
            return
        
        datetime_str = event_data['startDateTime']
        
        if not isinstance(datetime_str, str):
            result.add_error('startDateTime', 'Start datetime must be a string')
            return
        
        # Check format and parse
        try:
            start_dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            event_data['_parsed_start_dt'] = start_dt
        except ValueError:
            result.add_error('startDateTime', 'Start datetime must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)')
    
    def _validate_end_datetime(self, event_data: dict, result: ValidationResult):
        """Validate endDateTime in ISO 8601 format"""
        if 'endDateTime' not in event_data:
            return
        
        datetime_str = event_data['endDateTime']
        
        if not isinstance(datetime_str, str):
            result.add_error('endDateTime', 'End datetime must be a string')
            return
        
        # Check format and parse
        try:
            end_dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            event_data['_parsed_end_dt'] = end_dt
            
            # Check that end is after start
            start_dt = event_data.get('_parsed_start_dt')
            if start_dt and end_dt <= start_dt:
                result.add_error('endDateTime', 'End datetime must be after start datetime')
                
        except ValueError:
            result.add_error('endDateTime', 'End datetime must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)')
    
    def _validate_.add_error('title', 'Title must be at least 3 characters')
        
        if len(title) > 200:
            result.add_warning('title', 'Title exceeds 200 characters, may be truncated')
    
    def _validate_date(self, event_data: dict, result: ValidationResult):
        """Validate date format and value"""
        if 'date' not in event_data:
            return
        
        date_str = event_data['date']
        
        # Check format
        if not re.match(self.DATE_PATTERN, date_str):
            result.add_error('date', 'Date must be in YYYY-MM-DD format')
            return
        
        # Try to parse
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Store parsed date for other validations
            event_data['_parsed_date'] = event_date
            
        except ValueError:
            result.add_error('date', 'Invalid date value')
    
    def _validate_time(self, event_data: dict, result: ValidationResult):
        """Validate time format"""
        if 'time' not in event_data:
            return
        
        time_str = event_data['time']
        
        # Check format
        if not re.match(self.TIME_PATTERN, time_str):, required: bool = False):
        """Validate location field"""
        location = event_data.get('location')
        
        if required and not location:
            result.add_error('location', 'Location is required')
            return
        
        # Try to parse
        try:
            event_time = datetime.strptime(time_str, "%H:%M").time()
            event_data['_parsed_time'] = event_time
        except ValueError:
            result.add_error('time', 'Invalid time value')
    
    def _validate_duration(self, event_data: dict, result: ValidationResult):
        """Validate event duration"""
        duration = event_data.get('duration')
        
        if duration is None:, is_new_format: bool = False):
        """Validate recurrence configuration"""
        recurrence = event_data['recurrence']
        
        # Handle dict or Pydantic model
        if hasattr(recurrence, 'dict'):
            recurrence = recurrence.dict()
        
        # Check frequency
        valid_frequencies = {'daily', 'weekly', 'monthly'}
        frequency = recurrence.get('frequency', '').lower()
        
        if frequency not in valid_frequencies:
            result.add_error(
                'recurrence.frequency',
                f'Invalid frequency. Must be one of: {", ".join(valid_frequencies)}'
            )
        
        # Check interval
        interval = recurrence.get('interval', 1)
        if not isinstance(interval, int) or interval < 1:
            result.add_error('recurrence.interval', 'Interval must be a positive integer')
        
        # Check end date if present
        if recurrence.get('endDate'):
            end_date_str = recurrence['endDate']
            if not re.match(self.DATE_PATTERN, end_date_str):
                result.add_error('recurrence.endDate', 'End date must be in YYYY-MM-DD format')
            else:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                    
                    # Get start date from appropriate format
                    if is_new_format:
                        start_dt = event_data.get('_parsed_start_dt')
                        start_date = start_dt.date() if start_dt else None
                    else:
                result.add_error(
                'type', 
                f'Invalid event type. Must be one of: {", ".join(self.VALID_EVENT_TYPES)}'
            ), is_new_format: bool = False):
        """Warn if event date is in the distant past"""
        if is_new_format:
            start_dt = event_data.get('_parsed_start_dt')
            parsed_date = start_dt.date() if start_dt else None
        else:
            parsed_date = event_data.get('_parsed_date')
        
        if not parsed_date:
            return
        
        today = date.today()
        days_ago = (today - parsed_date).days
        
        if days_ago > 365:  # More than a year ago
            field = 'startDateTime' if is_new_format else 'date'
            result.add_warning(field, f'Event is {days_ago} days in the past')
    
    def _validate_date_not_too_far_future(self, event_data: dict, result: ValidationResult, is_new_format: bool = False):
        """Warn if event date is in the distant future"""
        if is_new_format:
            start_dt = event_data.get('_parsed_start_dt')
            parsed_date = start_dt.date() if start_dt else None
        else:
            parsed_date = event_data.get('_parsed_date')
        
        if not parsed_date:
            return
        
        today = date.today()
        days_ahead = (parsed_date - today).days
        
        if days_ahead > 730:  # More than 2 years ahead
            field = 'startDateTime' if is_new_format else 'date'
            result.add_warning(fieldrequency', '').lower()
        
        if frequency not in valid_frequencies:
            result.add_error(
                'recurrence.frequency',
                f'Invalid frequency. Must be one of: {", ".join(valid_frequencies)}'
            )
        
        # Check interval
        interval = recurrence.get('interval', 1)
        if not isinstance(interval, int) or interval < 1:
            result.add_error('recurrence.interval', 'Interval must be a positive integer')
        
        # Check end date if present
        if recurrence.get('endDate'):
            end_date_str = recurrence['endDate']
            if not re.match(self.DATE_PATTERN, end_date_str):
                result.add_error('recurrence.endDate', 'End date must be in YYYY-MM-DD format')
            else:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                    start_date = event_data.get('_parsed_date')
                    
                    if start_date and end_date < start_date:
                        result.add_error('recurrence.endDate', 'End date must be after start date')
                except ValueError:
                    result.add_error('recurrence.endDate', 'Invalid end date value')
        
        # Check days of week
        if recurrence.get('daysOfWeek'):
            days = recurrence['daysOfWeek']
            if not isinstance(days, list) or not all(isinstance(d, int) and 0 <= d <= 6 for d in days):
                result.add_error('recurrence.daysOfWeList[ValidationResult]:
        """
        Validate multiple events
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        
        for event in events:
            results.append(self.validate_event(event)a: dict, result: ValidationResult):
        """Warn if event date is in the distant future"""
        parsed_date = event_data.get('_parsed_date')
        if not parsed_date:
            return
        
        today = date.today()
        days_ahead = (parsed_date - today).days
        
        if days_ahead > 730:  # More than 2 years aheadList[dict]:
        """
        Remove duplicate events
        Supports both old format (date/time) and new format (startDateTime/endDateTime)
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of unique events (preserves first occurrence)
        """
        unique_events = []
        seen = set()
        
        for event in events:
            # Determine format and create signature
            if 'startDateTime' in event:
                # New format
                signature = (
                    event.get('title', '').lower().strip(),
                    event.get('startDateTime'),
                    event.get('endDateTime'),
                    event.get('type')
                )
            else:
                # Old format
                signature = (
                    event.get('title', '').lower().strip(),
                    event.get('date'),
                    event.get('time'),
                    event.get('type')
                )
            
            if signature not in seen:
                seen.add(signature)
                unique_events.append(event)
        
        return unique_eventplicates)
        """
        unique_events = []
        duplicates = []
        seen = set()
        
        for event in events:
            # Create a signature for the event
            signature = (
                event.get('title', '').lower().strip(),
                event.get('date'),
                event.get('time'),
                event.get('type')
            )
            
            if signature in seen:
                duplicates.append(event)
            else:
                seen.add(signature)
                unique_events.append(event)
        
        return unique_events, duplicates
