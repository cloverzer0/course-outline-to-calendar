import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import pypdf
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from root directory
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')

class CourseInfo(BaseModel):
    """Schema for a single course extracted from course outline."""
    title: str = Field(description="The title or name of the course")
    start_date: str = Field(description="The start date and time in ISO format (e.g., 2026-01-20T09:00:00)")
    end_date: str = Field(description="The end date and time in ISO format (e.g., 2026-05-15T17:00:00)")
    location: str = Field(description="The location where the course takes place")
    description: str = Field(default="", description="Brief description of the course")
    recurrence_rules: str = Field(description="Recurrence rules in iCalendar format (e.g., FREQ=WEEKLY;BYDAY=MO,WE,FR)")


class CoursesOutput(BaseModel):
    """Schema for all courses extracted from course outline."""
    courses: List[CourseInfo] = Field(description="List of all courses found in the outline")


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
            CoursesOutput,
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
    
    def parse_courses_from_text(self, pdf_text: str) -> List[Dict]:
        """Use LLM to extract structured course data from PDF text"""
        
        # Create prompt template
        extraction_template = """\
You are a course outline data extraction assistant. Extract ALL courses from the following course outline text.

For each course, extract:
- title: The title or name of the course
- start_date: The start date and time in ISO format (e.g., 2026-01-20T09:00:00)
- end_date: The end date and time in ISO format (e.g., 2026-05-15T17:00:00)
- location: The location where the course takes place
- description: Brief description of the course (optional)
- recurrence_rules: Recurrence rules in iCalendar format (e.g., FREQ=WEEKLY;BYDAY=MO,WE,FR)

IMPORTANT: 
- Extract EVERY course you find in the text
- Return a list of courses as JSON array
- Use ISO format for dates: YYYY-MM-DDTHH:MM:SS
- If recurrence is not specified, infer from the date range
- If a field is not found, use empty string for optional fields
- Make reasonable inferences for required fields based on context

Course outline text:
{text}

Return all courses in the specified format.
"""
        
        prompt = ChatPromptTemplate.from_template(template=extraction_template)

        
        # Format the prompt with the PDF text
        messages = prompt.format_messages(
            text=pdf_text
        )

        # print("Invoking LLM to extract courses...")
        # print("Sample prompt message:", messages[0].content[:500])  # Print first 500 characters of prompt for debugging
        
        try:
            # Call the LLM with structured output
            response = self.structured_llm.invoke(messages)
            
            # Convert Pydantic models to dictionaries
            courses = [course.model_dump() for course in response.courses]

            # print(f"Extracted {len(courses)} courses using LLM")
            # print("Sample extracted course:", courses[0] if courses else "No courses extracted")  # Print first course for debugging
            
            return courses
            
        except Exception as e:
            raise Exception(f"Error parsing courses with LLM: {str(e)}")
    
    def convert_to_standard_format(self, courses: List[Dict]) -> List[Dict]:
        """Convert parsed courses to standard format expected by calendar"""
        standardized = []
        
        for idx, course in enumerate(courses):
            try:
                # Parse dates
                start_date_str = course.get('start_date', '')
                end_date_str = course.get('end_date', '')
                
                try:
                    start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                except:
                    start_date = datetime.now()
                
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                except:
                    end_date = datetime.now()
                
                standardized_course = {
                    'title': course.get('title', 'Untitled Course'),
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'location': course.get('location', 'TBD'),
                    'description': course.get('description', ''),
                    'recurrence_rules': course.get('recurrence_rules', ''),
                    'original_data': course
                }
                
                standardized.append(standardized_course)
                
            except Exception as e:
                print(f"Warning: Skipping course {idx + 1}: {str(e)}")
                continue
        
        return standardized
    
    def parse_pdf_file(self, pdf_path: str) -> List[Dict]:
        """Main method to parse PDF and return standardized courses"""
        print(f"Parsing PDF file: {pdf_path}")
        
        # Step 1: Extract text from PDF
        pdf_text = self.extract_text_from_pdf(pdf_path)
        print(f"Extracted {len(pdf_text)} characters from PDF")
        
        # Step 2: Use LLM to parse courses
        raw_courses = self.parse_courses_from_text(pdf_text)
        print(f"Extracted {len(raw_courses)} courses using LLM")
        
        # Step 3: Convert to standard format
        standardized_courses = self.convert_to_standard_format(raw_courses)
        print(f"Standardized {len(standardized_courses)} courses")
        
        if not standardized_courses:
            raise Exception("No valid courses found in PDF")
        
        return standardized_courses

# Example usage
if __name__ == "__main__":
    print("Testing PDFParser with actual PDF file...\n")
    
    # Create parser instance
    parser = PDFParser()
    
    # Path to the PDF file in data folder
    pdf_path = "../../data/course-outline-psych.pdf"
    
    try:
        # Parse the PDF file
        courses = parser.parse_pdf_file(pdf_path)
        
        print(f"\n✓ Successfully extracted {len(courses)} courses!\n")
        print("=" * 80)
        
        # Print each course in detail
        for idx, course in enumerate(courses, 1):
            print(f"\nCourse {idx}:")
            print(f"  Title: {course.get('title', 'N/A')}")
            print(f"  Start Date: {course.get('start_date', 'N/A')}")
            print(f"  End Date: {course.get('end_date', 'N/A')}")
            print(f"  Location: {course.get('location', 'N/A')}")
            print(f"  Recurrence: {course.get('recurrence_rules', 'N/A')}")
            description = course.get('description', '')
            if description:
                print(f"  Description: {description[:100]}{'...' if len(description) > 100 else ''}")
            print("-" * 80)
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()