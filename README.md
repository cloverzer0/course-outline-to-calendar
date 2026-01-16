# Course Outline to Calendar

## Overview

An AI-powered web application that automatically converts course outline PDFs into calendar events, eliminating the tedious manual process of setting up academic calendars.

## Problem Statement

Many students rely on digital calendars to keep their academic lives organized—tracking classes, assignment deadlines, tests, office hours, and locations. While this system is effective, setting it up is unnecessarily tedious.

All of this critical information is provided by professors in a course outline, typically as a PDF document. Although course outlines are essential, they are static, text-heavy, and difficult to navigate. Students must repeatedly open and scan these PDFs to find small but important details, such as upcoming deadlines or office hours, until the information is fully memorized.

As a result, students are forced to manually extract information from course outlines and create individual calendar events themselves—a time-consuming, repetitive, and error-prone process.

## Solution

This project addresses that problem by converting course outlines directly into calendar events. By uploading a course outline to the application, students can automatically generate an importable .ics calendar file containing all relevant academic events, eliminating manual setup and making course information immediately accessible.

## Project Structure

```
course-outline-to-calendar/
│
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
│
├── docs/
│   ├── background.md
│   ├── problem-statement.md
│   ├── solution.md
│   ├── functional-requirements.md
│   ├── implementation-plan.md
│   ├── architecture-diagram.png
│   └── demo-flow.md
│
├── frontend/                           # Next.js React application
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   │
│   ├── public/
│   │   └── favicon.ico
│   │
│   └── src/
│       ├── app/
│       │   ├── page.tsx               # Landing / upload page
│       │   ├── layout.tsx
│       │   └── review/
│       │       └── page.tsx           # Event review & edit UI
│       │
│       ├── components/
│       │   ├── FileUpload.tsx
│       │   ├── EventPreview.tsx
│       │   ├── EventEditor.tsx
│       │   ├── CalendarPreview.tsx
│       │   └── FeedbackMessage.tsx
│       │
│       ├── services/
│       │   └── api.ts                 # Backend API calls
│       │
│       ├── types/
│       │   └── calendarEvent.ts
│       │
│       └── styles/
│           └── globals.css
│
├── backend/                            # FastAPI Python application
│   ├── requirements.txt
│   ├── main.py                        # FastAPI entry point
│   ├── config.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── upload.py              # PDF upload endpoint
│   │   │   ├── extract.py             # Text + event extraction
│   │   │   └── calendar.py            # .ics generation
│   │   └── dependencies.py
│   │
│   ├── services/
│   │   ├── pdf_parser.py              # PDF → text
│   │   ├── text_cleaner.py
│   │   ├── event_extractor.py         # AI / LangChain logic
│   │   ├── event_validator.py
│   │   └── ics_generator.py           # iCalendar logic
│   │
│   ├── models/
│   │   └── event.py                   # Core event data model
│   │
│   ├── utils/
│   │   ├── date_parser.py
│   │   ├── recurrence_helper.py
│   │   └── error_handler.py
│   │
│   └── tests/
│       ├── test_pdf_parser.py
│       ├── test_event_extraction.py
│       └── test_ics_generation.py
│
├── ai/                                 # AI processing pipeline
│   ├── prompts/
│   │   └── extract_events.txt
│   │
│   ├── chains/
│   │   └── course_outline_chain.py    # LangChain pipeline
│   │
│   └── schemas/
│       └── event_schema.json
│
├── data/
│   ├── uploads/                       # Temporary PDF storage
│   ├── extracted_text/
│   └── sample_outlines/
│
└── scripts/
    ├── dev_start.sh
    └── cleanup_uploads.py
```

## High-Level Implementation Plan

### Phase 1: Project Setup & System Architecture
**Goal:** Establish a clean foundation for development

- Define system architecture (frontend, backend, AI processing pipeline)
- Select core technologies:
  - Frontend: React / Next.js
  - Backend API: FastAPI (Python)
  - PDF text extraction library
  - AI/NLP processing (LangChain or similar)
  - Calendar generation using iCalendar (.ics) standard
- Define a unified calendar event data model:
  - Title
  - Start date/time
  - End date/time
  - Location
  - Description
  - Recurrence rules
- Set up repository structure, environment configuration, and basic CI workflow

**Deliverable:** Running skeleton app with frontend ↔ backend communication

---

### Phase 2: Course Outline Input & Validation
**Goal:** Allow users to submit course outlines safely and reliably

- Implement user interface for:
  - PDF file upload
  - (Optional) pasted text input
- Enforce file constraints:
  - Accepted formats (PDF)
  - File size limits
- Validate uploads before processing
- Provide immediate user feedback on upload success or failure

**Deliverable:** Validated course outline successfully accepted by the system

---

### Phase 3: PDF Text Extraction & Cleaning
**Goal:** Convert static PDFs into usable text

- Extract text from uploaded PDFs
  - Support multi-page documents
  - Preserve basic structure where possible (headings, lists, tables)
- Clean extracted text by:
  - Removing headers and footers
  - Normalizing whitespace
  - Fixing common PDF extraction artifacts

**Deliverable:** Clean, readable text representation of the course outline

---

### Phase 4: AI-Assisted Information Extraction
**Goal:** Identify calendar-relevant information automatically

- Analyze cleaned text to extract:
  - Lecture schedules (days, times, locations)
  - Assignment deadlines
  - Tests, quizzes, and exams
  - Instructor and TA office hours
- Detect dates, times, and recurring patterns from unstructured text
- Ignore non-calendar-relevant sections (grading policies, descriptions)
- Flag ambiguous or incomplete data for user review

**Deliverable:** Raw list of detected academic events

---

### Phase 5: Event Structuring & Validation
**Goal:** Convert extracted data into clean, structured events

- Transform extracted information into standardized event objects
- Validate date and time formats
- Infer reasonable defaults when information is missing (e.g., lecture duration)
- Deduplicate repeated events
- Apply consistent naming and descriptions

**Deliverable:** Validated list of structured calendar events

---

### Phase 6: User Review & Editing
**Goal:** Give users control before calendar export

- Display a preview of all generated events
- Highlight events with missing or uncertain information
- Allow users to:
  - Edit event details
  - Add new events manually
  - Delete incorrect events
- Require user confirmation before final export

**Deliverable:** User-approved list of final events

---

### Phase 7: Calendar File (.ics) Generation
**Goal:** Produce an importable calendar file

- Generate a valid .ics file containing all approved events
- Support:
  - One-time events
  - Recurring events using RRULE
- Ensure compatibility with:
  - Google Calendar
  - Apple Calendar
  - Outlook
- Provide one-click download

**Deliverable:** Downloadable .ics calendar file

---

### Phase 8: Error Handling, Testing & Demo Readiness
**Goal:** Make the system reliable and presentation-ready

- Handle failure cases:
  - No events detected
  - PDF parsing errors
  - Invalid or missing data
- Provide clear error and success messages
- Test with multiple real course outlines
- Verify calendar imports across platforms
- Prepare a clean demo workflow: **Upload → Review → Download → Import**

**Deliverable:** Stable, demo-ready MVP

---

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- OpenAI API key or Anthropic API key

### Installation

1. Clone the repository
2. Set up environment variables (copy `.env.example` to `.env`)
3. Install dependencies:

```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt
```

### Running the Application

```bash
# Use the dev start script
./scripts/dev_start.sh
```

Or run separately:

```bash
# Frontend (port 3000)
cd frontend
npm run dev

# Backend (port 8000)
cd backend
uvicorn main:app --reload
```

## Documentation

- [Background](docs/background.md)
- [Problem Statement](docs/problem-statement.md)
- [Solution](docs/solution.md)
- [Functional Requirements](docs/functional-requirements.md)
- [Implementation Plan](docs/implementation-plan.md)
- [Demo Flow](docs/demo-flow.md)

## License

MIT

