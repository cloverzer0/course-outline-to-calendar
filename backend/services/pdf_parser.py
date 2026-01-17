import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import pypdf
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Add parent directory to path to import models
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.event import CalendarEvent, EventType, RecurrenceRule, RecurrenceFrequency

# Load environment variables from root directory
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')

# Wrapper for LLM output
class CourseEventsOutput(BaseModel):
    """Schema for all events extracted from course outline."""
    course_name: str = Field(description="The name or code of the course (e.g., 'PSYC1001F')")
    events: List[CalendarEvent] = Field(description="List of all events (lectures, quizzes, assignments, exams, etc.) found in the outline")


class PDFParser:
    def __init__(self):
        # Account for deprecation of LLM model
        current_date = datetime.now().date()
        target_date = datetime(2024, 6, 12).date()
        
        # Set the model variable based on the current date
        if current_date > target_date:
            llm_model = "gpt-3.5-turbo"
        else:
            llm_model = "gpt-3.5-turbo-0301"
        
        api_key = os.getenv('OPENAI_API_KEY')
        
        # Using OpenRouter - use gpt-4o-mini which supports structured output
        self.llm = ChatOpenAI(
            temperature=0.0,
            model="openai/gpt-4o-mini",  # Use newer model that supports structured output
            openai_api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Use with_structured_output with function_calling method
        self.structured_llm = self.llm.with_structured_output(
            CourseEventsOutput,
            method="function_calling"  # Use function calling instead of json_schema
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            pdf_reader = pypdf.PdfReader(pdf_path)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            if not text.strip():
                raise Exception("No text could be extracted from PDF")
            
            # print(f"Extracted {len(text)} characters from PDF")
            # print("Sample extracted text:", text[:500])  # Print first 500 characters for debugging

            return text
        
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def parse_courses_from_text(self, pdf_text: str) -> Dict:
        """Use LLM to extract structured event data from PDF text"""
        
        # Create prompt template
        extraction_template = """\
You are a course outline data extraction assistant. Extract ALL events from the following course outline text.

Extract these types of events:
1. **LECTURES**: Regular class sessions (recurring weekly)
2. **QUIZZES**: In-class or online quizzes with specific dates
3. **ASSIGNMENTS**: Homework assignments with due dates
4. **EXAMS**: Midterms, finals, or other exams
5. **PROJECTS**: Course projects with due dates
6. **OFFICE HOURS**: Instructor/TA office hours if mentioned
7. **OTHER**: Any other course-related events

For each event, extract:
- title: Format as "CourseName - EventType" or "CourseName - EventType #" (e.g., "PSYC1001F - Lecture", "PSYC1001F - Quiz 1")
- startDateTime: Start date and time in ISO format (YYYY-MM-DDTHH:MM:SS)
- endDateTime: End date and time in ISO format (YYYY-MM-DDTHH:MM:SS)
- type: One of: "lecture", "exam", "assignment", "project", "office_hours", "other"
- location: Physical location or "Online" or "TBD" (optional, defaults to "TBD")
- description: Brief description (optional)
- recurrence: For recurring events, provide an object with:
  - frequency: "weekly", "daily", or "monthly"
  - daysOfWeek: Array of integers [0-6] where 0=Sunday, 1=Monday, 2=Tuesday, etc.
  - endDate: Last occurrence date in ISO format (optional)
  For one-time events, set recurrence to null

IMPORTANT INSTRUCTIONS:
- For LECTURES: Create ONE recurring event with the schedule (e.g., every Tuesday 6:05-8:55 PM)
- For QUIZZES/ASSIGNMENTS/EXAMS: Create separate one-time events for each with specific due dates/times
- Use the course semester dates to determine start and end dates for recurring lectures
- Infer reasonable times if not explicitly stated (e.g., assignments due at 11:59 PM)
- Extract the course code/name and include it in every event title

Course outline text:
{text}

Return the course name and all events found in the outline.
"""
        
        prompt = ChatPromptTemplate.from_template(template=extraction_template)

        
        # Format the prompt with the PDF text
        messages = prompt.format_messages(
            text=pdf_text
        )

        # print("Invoking LLM to extract events...")
        # print("Sample prompt message:", messages[0].content[:500])  # Print first 500 characters of prompt for debugging
        
        try:
            # Call the LLM with structured output
            response = self.structured_llm.invoke(messages)
            
            # Convert Pydantic model to dictionary for inspection if needed
            result = {
                'course_name': response.course_name,
                'events': response.events  # Already CalendarEvent objects
            }

            # print(f"Extracted {len(result['events'])} events for course: {result['course_name']}")
            # if result['events']:
            #     print("Sample extracted event:", result['events'][0])  # Print first event for debugging
            
            return result
            
        except Exception as e:
            raise Exception(f"Error parsing events with LLM: {str(e)}")
    
    def parse_pdf_file(self, pdf_path: str) -> List[CalendarEvent]:
        """Main method to parse PDF and return CalendarEvent objects"""
        print(f"Parsing PDF file: {pdf_path}")
        
        # Step 1: Extract text from PDF
        pdf_text = self.extract_text_from_pdf(pdf_path)
        print(f"Extracted {len(pdf_text)} characters from PDF")
        
        # Step 2: Use LLM to parse events - returns CalendarEvent objects directly
        events_data = self.parse_courses_from_text(pdf_text)
        calendar_events = events_data['events']
        print(f"Extracted {len(calendar_events)} CalendarEvent objects for course: {events_data.get('course_name', 'Unknown')}")
        
        if not calendar_events:
            raise Exception("No valid events found in PDF")
        
        return calendar_events

# Example usage
if __name__ == "__main__":
    print("Testing PDFParser with actual PDF file...\n")
    
    # Create parser instance
    parser = PDFParser()
    
    # Path to the PDF file in data folder
    pdf_path = "../../data/course-outline-psych.pdf"
    
    try:
        # Parse the PDF file
        events = parser.parse_pdf_file(pdf_path)
        
        print(f"\n{'='*80}")
        print(f"✓ Successfully extracted {len(events)} CalendarEvent objects!")
        print(f"{'='*80}\n")
        
        # Group events by type for display
        event_types = {}
        for event in events:
            # Handle both string and enum types
            event_type = event.type.value if hasattr(event.type, 'value') else event.type
            if event_type not in event_types:
                event_types[event_type] = []
            event_types[event_type].append(event)
        
        # Print summary
        print("EVENT SUMMARY:")
        print("-" * 80)
        for event_type, events_list in event_types.items():
            print(f"  {event_type.upper()}: {len(events_list)} event(s)")
        print()
        
        # Print each event type group with details
        for event_type, events_list in event_types.items():
            print(f"\n{event_type.upper()} EVENTS ({len(events_list)}):")
            print("=" * 80)
            
            for idx, event in enumerate(events_list, 1):
                print(f"\n  [{idx}] {event.title}")
                
                # Use helper properties from CalendarEvent
                print(f"      Start:      {event.startDateTime} ({event.start_dt.strftime('%a, %b %d, %Y at %I:%M %p')})")
                print(f"      End:        {event.endDateTime} ({event.end_dt.strftime('%a, %b %d, %Y at %I:%M %p')})")
                print(f"      Duration:   {event.duration_minutes} minutes")
                print(f"      Location:   {event.location}")
                # Handle both string and enum types
                type_value = event.type.value if hasattr(event.type, 'value') else event.type
                print(f"      Type:       {type_value}")
                
                if event.recurrence:
                    days_names = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'}
                    days_str = ', '.join([days_names[d] for d in event.recurrence.daysOfWeek])
                    # Handle both string and enum frequency
                    freq_value = event.recurrence.frequency.value if hasattr(event.recurrence.frequency, 'value') else event.recurrence.frequency
                    print(f"      Recurrence: {freq_value.upper()} on {days_str}")
                    if event.recurrence.endDate:
                        print(f"      Until:      {event.recurrence.endDate}")
                
                if event.description:
                    desc_preview = event.description[:80] + '...' if len(event.description) > 80 else event.description
                    print(f"      Description: {desc_preview}")
                
                print(f"      Confidence: {event.confidence}")
                print(f"      Needs Review: {event.needsReview}")
        
        print(f"\n{'='*80}")
        
        # Show sample JSON output
        print("\n\nSAMPLE JSON OUTPUT (first event):")
        print("-" * 80)
        print(events[0].model_dump_json(indent=2))
        
        print(f"\n{'='*80}")
        print("✓ All tests passed successfully!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()