import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import pypdf
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from root directory
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')

class EventInfo(BaseModel):
    """Schema for a single event extracted from course outline."""
    title: str = Field(description="Event title (e.g., 'PSYC1001F - Lecture', 'PSYC1001F - Quiz 1', 'PSYC1001F - Assignment 2')")
    event_type: str = Field(description="Type of event: 'lecture', 'exam', 'quiz', 'assignment', 'project', 'office_hours', or 'other'")
    start_datetime: str = Field(description="Start date and time in ISO format (e.g., 2022-09-13T18:05:00)")
    end_datetime: str = Field(description="End date and time in ISO format (e.g., 2022-09-13T20:55:00)")
    location: str = Field(description="Location (e.g., 'University Centre 231', 'Online', 'TBD')")
    description: Optional[str] = Field(default="", description="Brief description or additional notes")
    recurrence: Optional[str] = Field(default=None, description="Recurrence pattern if repeating (e.g., 'WEEKLY', 'None' for one-time events)")
    days_of_week: Optional[str] = Field(default=None, description="Days of week for recurring events (e.g., 'TU', 'MO,WE', or None)")
    recurrence_end_date: Optional[str] = Field(default=None, description="End date for recurring events in ISO format (e.g., 2022-12-07)")


class CourseEventsOutput(BaseModel):
    """Schema for all events extracted from course outline."""
    course_name: str = Field(description="The name or code of the course (e.g., 'PSYC1001F')")
    events: List[EventInfo] = Field(description="List of all events (lectures, quizzes, assignments, exams, etc.) found in the outline")


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
- title: Format as "CourseName - EventType" or "CourseName - EventType #" (e.g., "PSYC1001F - Lecture", "PSYC1001F - Quiz 1", "PSYC1001F - Assignment 2")
- event_type: One of: lecture, exam, quiz, assignment, project, office_hours, other
- start_datetime: Start date and time in ISO format (YYYY-MM-DDTHH:MM:SS)
- end_datetime: End date and time in ISO format (YYYY-MM-DDTHH:MM:SS)
- location: Physical location or "Online" or "TBD"
- description: Brief description (optional)
- recurrence: "WEEKLY" for recurring events, null for one-time events
- days_of_week: For recurring events, day codes like "TU", "MO,WE,FR", etc. (null for one-time)
- recurrence_end_date: For recurring events, the last occurrence date in ISO format (null for one-time)

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
            
            # Convert Pydantic model to dictionary
            result = {
                'course_name': response.course_name,
                'events': [event.model_dump() for event in response.events]
            }

            # print(f"Extracted {len(result['events'])} events for course: {result['course_name']}")
            # if result['events']:
            #     print("Sample extracted event:", result['events'][0])  # Print first event for debugging
            
            return result
            
        except Exception as e:
            raise Exception(f"Error parsing events with LLM: {str(e)}")
    
    def convert_to_standard_format(self, events_data: Dict) -> List[Dict]:
        """Convert parsed events to standard format expected by calendar"""
        standardized = []
        course_name = events_data.get('course_name', 'Unknown Course')
        events = events_data.get('events', [])
        
        for idx, event in enumerate(events):
            try:
                # Parse dates
                start_date_str = event.get('start_datetime', '')
                end_date_str = event.get('end_datetime', '')
                
                try:
                    start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                except:
                    start_date = datetime.now()
                
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                except:
                    end_date = datetime.now()
                
                # Build recurrence rules
                recurrence_rules = ""
                if event.get('recurrence') == 'WEEKLY' and event.get('days_of_week'):
                    recurrence_rules = f"FREQ=WEEKLY;BYDAY={event['days_of_week']}"
                    if event.get('recurrence_end_date'):
                        # Convert date to RRULE format (YYYYMMDD)
                        try:
                            end_dt = datetime.fromisoformat(event['recurrence_end_date'])
                            recurrence_rules += f";UNTIL={end_dt.strftime('%Y%m%d')}"
                        except:
                            pass
                
                standardized_event = {
                    'title': event.get('title', f'{course_name} - Event {idx + 1}'),
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'location': event.get('location', 'TBD'),
                    'description': event.get('description', ''),
                    'event_type': event.get('event_type', 'other'),
                    'recurrence_rules': recurrence_rules,
                    'original_data': event
                }
                
                standardized.append(standardized_event)
                
            except Exception as e:
                print(f"Warning: Skipping event {idx + 1}: {str(e)}")
                continue
        
        return standardized
    
    def parse_pdf_file(self, pdf_path: str) -> List[Dict]:
        """Main method to parse PDF and return standardized events"""
        print(f"Parsing PDF file: {pdf_path}")
        
        # Step 1: Extract text from PDF
        pdf_text = self.extract_text_from_pdf(pdf_path)
        print(f"Extracted {len(pdf_text)} characters from PDF")
        
        # Step 2: Use LLM to parse events
        events_data = self.parse_courses_from_text(pdf_text)
        print(f"Extracted {len(events_data.get('events', []))} events for course: {events_data.get('course_name', 'Unknown')}")
        
        # Step 3: Convert to standard format
        standardized_events = self.convert_to_standard_format(events_data)
        print(f"Standardized {len(standardized_events)} events")
        
        if not standardized_events:
            raise Exception("No valid events found in PDF")
        
        return standardized_events

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
        
        print(f"\n✓ Successfully extracted {len(events)} events!\n")
        print("=" * 80)
        
        # Group events by type for display
        event_types = {}
        for event in events:
            event_type = event.get('event_type', 'other')
            if event_type not in event_types:
                event_types[event_type] = []
            event_types[event_type].append(event)
        
        # Print each event type group
        for event_type, events_list in event_types.items():
            print(f"\n{event_type.upper()} ({len(events_list)} event{'s' if len(events_list) > 1 else ''}):")
            print("-" * 80)
            
            for event in events_list:
                print(f"\n  Title: {event.get('title', 'N/A')}")
                print(f"  Start: {event.get('start_date', 'N/A')}")
                print(f"  End: {event.get('end_date', 'N/A')}")
                print(f"  Location: {event.get('location', 'N/A')}")
                if event.get('recurrence_rules'):
                    print(f"  Recurrence: {event.get('recurrence_rules', 'N/A')}")
                description = event.get('description', '')
                if description:
                    print(f"  Description: {description[:100]}{'...' if len(description) > 100 else ''}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()