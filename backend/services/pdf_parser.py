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
from models.event import CalendarEvent, EventType, RecurrenceRule, RecurrenceFrequency, CourseCalendar, MultiCourseCalendar

# Load environment variables from root directory
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')

# Wrapper for LLM output
class CourseEventsOutput(BaseModel):
    """Schema for all events extracted from course outline."""
    course_name: str = Field(description="The full name of the course (e.g., 'Introduction to Psychology')")
    course_code: str = Field(description="The course code (e.g., 'PSYC1001F', 'CS 301')")
    semester: Optional[str] = Field(default=None, description="The semester/term (e.g., 'Winter 2026', 'Fall 2025')")
    instructor: Optional[str] = Field(default=None, description="The course instructor's name (e.g., 'Dr. Smith', 'Prof. Johnson')")
    events: List[CalendarEvent] = Field(description="List of all events (lectures, quizzes, assignments, exaidms, etc.) found in the outline")


class PDFParser:
    def __init__(self):        
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

CRITICAL DATETIME RULES:
- endDateTime MUST be AFTER startDateTime (cannot be equal or before)
- For assignments: Set startDateTime to 9:00 AM on the due date, endDateTime to 11:59 PM
- For exams/quizzes: Use the actual exam time for start, add duration for end (e.g., 2-3 hours)
- For lectures: Use the class session times (e.g., 2:00 PM - 3:20 PM)
- NEVER set start and end to the same time

IMPORTANT INSTRUCTIONS:
- For LECTURES: Create ONE recurring event with the schedule (e.g., every Tuesday 6:05-8:55 PM)
- For QUIZZES/ASSIGNMENTS/EXAMS: Create separate one-time events for each with specific due dates/times
- Use the course semester dates to determine start and end dates for recurring lectures
- Infer reasonable times if not explicitly stated (e.g., assignments start at 9:00 AM, due at 11:59 PM)
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
            print("Invoking LLM to extract events...")
            response = self.structured_llm.invoke(messages)
            
            # Return dictionary with all course data
            return {
                'course_name': response.course_name,
                'course_code': response.course_code,
                'semester': response.semester,
                'instructor': response.instructor,
                'events': response.events
            }
            
        except Exception as e:
            raise Exception(f"Error parsing events with LLM: {str(e)}")
    
    def parse_pdf_file(self, pdf_path: str) -> CourseCalendar:
        """Main method to parse PDF and return CourseCalendar object"""
        print(f"Parsing PDF file: {pdf_path}")
        
        # Step 1: Extract text from PDF
        pdf_text = self.extract_text_from_pdf(pdf_path)
        print(f"Extracted {len(pdf_text)} characters from PDF")
        print("Sample extracted text (last 500 chars):", pdf_text[-500:])  # Print last 500 characters for debugging
        
        # Step 2: Use LLM to parse events - returns course data with events
        events_data = self.parse_courses_from_text(pdf_text)
        
        # Step 3: Create CourseCalendar object
        course_calendar = CourseCalendar(
            course_name=events_data['course_name'],
            course_code=events_data['course_code'],
            semester=events_data.get('semester'),
            instructor=events_data.get('instructor'),
            events=events_data['events']
        )
        
        print(f"Extracted {len(course_calendar.events)} events for {course_calendar.course_code} - {course_calendar.course_name}")
        
        if not course_calendar.events:
            raise Exception("No valid events found in PDF")

        print("Sample extracted event:", course_calendar.events[0])
        
        return course_calendar
    
    def parse_multiple_pdfs(self, pdf_paths: List[str]) -> MultiCourseCalendar:
        """Parse multiple PDF files and return MultiCourseCalendar object"""
        print(f"Parsing {len(pdf_paths)} PDF files...\n")
        
        courses = []
        for pdf_path in pdf_paths:
            try:
                course = self.parse_pdf_file(pdf_path)
                courses.append(course)
                print(f"✓ Successfully parsed {course.course_code}\n")
            except Exception as e:
                print(f"✗ Error parsing {pdf_path}: {str(e)}\n")
                # Continue with other files
        
        multi_course_calendar = MultiCourseCalendar(courses=courses)
        print(f"\nTotal: {multi_course_calendar.total_courses} courses, {multi_course_calendar.total_events} events")
        
        return multi_course_calendar

# Example usage
if __name__ == "__main__":
    import sys
    
    # Create parser instance
    parser = PDFParser()
    
    # Check if testing single or multiple PDFs
    if len(sys.argv) > 1 and sys.argv[1] == '--single':
        # Test with single PDF
        print("Testing PDFParser with single PDF file...\n")
        pdf_path = "../../data/1200_Syllabus.pdf"

        try:
            course_calendar = parser.parse_pdf_file(pdf_path)

            print(f"\n{'='*80}")
            print(f"✓ COURSE CALENDAR SUMMARY")
            print(f"{'='*80}")
            print(f"  Course Code: {course_calendar.course_code}")
            print(f"  Course Name: {course_calendar.course_name}")
            print(f"  Semester: {course_calendar.semester or 'N/A'}")
            print(f"  Instructor: {course_calendar.instructor or 'N/A'}")
            print(f"  Total Events: {course_calendar.event_count}")
            print(f"  Needs Review: {course_calendar.needs_review_count}")
            print(f"{'='*80}\n")

            events = course_calendar.events

            # Group events by type for display
            event_types = {}
            for event in events:
                # Handle both string and enum types
                event_type = event.type.value if hasattr(event.type, 'value') else event.type
                if event_type not in event_types:
                    event_types[event_type] = []
                event_types[event_type].append(event)

            # Print summary
            print("EVENT BREAKDOWN BY TYPE:")
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
                        days_str = ', '.join([days_names[d] for d in event.recurrence.daysOfWeek]) if event.recurrence.daysOfWeek else 'N/A'
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

            # Show sample JSON outputs
            print("\n\nSAMPLE JSON OUTPUT (CourseCalendar):")
            print("-" * 80)
            print(course_calendar.model_dump_json(indent=2, exclude={'events'}))

            print("\n\nSAMPLE JSON OUTPUT (First Event):")
            print("-" * 80)
            print(events[0].model_dump_json(indent=2))

            print(f"\n{'='*80}")
            print("✓ Single-course test passed successfully!")
            print(f"{'='*80}\n")

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()

    else:
        # Test with multiple PDFs (DEFAULT)
        print("Testing PDFParser with multiple PDF files...\n")
        print("(Use --single flag to test single PDF)\n")

        pdf_paths = [
            "../../data/course-outline-psych.pdf",
            # Add more PDF paths here to test multiple courses
            "../../data/1200_Syllabus.pdf"
        ]

        try:
            print("Parsing multiple PDF files...\n")
            # Parse multiple PDFs
            multi_course = parser.parse_multiple_pdfs(pdf_paths)

            print(f"\n{'='*80}")
            print(f"✓ MULTI-COURSE CALENDAR SUMMARY")
            print(f"{'='*80}")
            print(f"  Total Courses: {multi_course.total_courses}")
            print(f"  Total Events: {multi_course.total_events}")
            print(f"  Events Needing Review: {multi_course.total_needs_review}")
            print(f"{'='*80}\n")

            # Print each course summary
            for course in multi_course.courses:
                print(f"\n{course.course_code} - {course.course_name}")
                print(f"  Semester: {course.semester or 'N/A'}")
                print(f"  Instructor: {course.instructor or 'N/A'}")
                print(f"  Events: {course.event_count}")
                print(f"  Needs Review: {course.needs_review_count}")

            # Show sample JSON output for MultiCourseCalendar
            print(f"\n\n{'='*80}")
            print("SAMPLE JSON OUTPUT (MultiCourseCalendar):")
            print("-" * 80)
            print(multi_course.model_dump_json(indent=2))

            print(f"\n{'='*80}")
            print("✓ Multi-course test passed successfully!")
            print(f"{'='*80}\n")

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()