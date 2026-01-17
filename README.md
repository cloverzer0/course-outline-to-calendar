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

## Team Work Assignment, Responsibilities & Dependencies

**Team Size:** 4 Engineers

### 🔑 Global Dependency (Applies to Everyone)

#### Event Data Model & API Contract (🚨 Highest Priority)

- **Must be defined and locked early in Phase 1**
- **Shared by Engineers 1, 2, 3, and 4**

Any late change impacts:
- Frontend rendering
- AI extraction
- Backend validation
- Calendar generation

**Locked Fields:**
- `title`
- `startDateTime`
- `endDateTime`
- `location`
- `description`
- `recurrence`
- `needsReview` (optional / confidence flag)

⚠️ **Changing this late causes widespread rework and integration risk.**

---

### 👨‍💻 Engineer 1 — Frontend & User Experience

**Focus:** User interaction, review flow, and usability

#### Responsibilities

- Design and implement frontend UI using React / Next.js
- Build course outline input flow:
  - PDF upload interface
  - Input validation and feedback
- Implement event preview and review UI:
  - Clear display of extracted events
  - Highlight ambiguous or incomplete events
- Enable user controls to:
  - Edit event details
  - Add or delete events
- Implement final export interaction:
  - Trigger .ics file generation
  - Handle file download
- (Optional) Calendar visualization UI

#### Project Structure Ownership
```
frontend/
├── app/
├── components/
├── services/
├── types/
└── styles/
```

#### Phases Covered
- Phase 2: Course Outline Input & Validation
- Phase 6: User Review & Editing
- Phase 7 (UI): Calendar Download & UX
- Phase 8: Demo Flow Polish

#### Parallel Work & Dependencies

| Dependency | Provided By | Why It Matters |
|------------|-------------|----------------|
| Event data schema | Eng 2 + Eng 3 | Determines how events are rendered |
| API endpoints | Eng 2 | Required to wire upload & export |
| Validation flags | Eng 4 | Needed to highlight ambiguous events |

**Blocking Risks:**
- Full integration blocked until API contracts stabilize
- Can work early using mock event data

---

### 👨‍💻 Engineer 2 — Backend API & File Processing

**Focus:** Core backend pipeline and data flow

#### Responsibilities

- Set up FastAPI backend and routing
- Implement secure PDF file upload
  - Validate uploaded files (format, size)
- Extract text from PDFs:
  - Multi-page support
  - Basic structure preservation
- Clean and normalize extracted text
- Define and maintain the core event data model
- Expose API endpoints for:
  - File upload
  - Event extraction
  - Returning structured events
  - Generating .ics files

#### Project Structure Ownership
```
backend/
├── main.py
├── api/
├── services/pdf_parser.py
├── services/text_cleaner.py
├── models/
└── utils/
```

#### Phases Covered
- Phase 1: Architecture Setup
- Phase 2: File Upload & Validation
- Phase 3: PDF Text Extraction
- Phase 5: Event Structuring & Validation
- Phase 7: Calendar Generation (API side)

#### Parallel Work & Dependencies

| Dependency | Provided By | Why It Matters |
|------------|-------------|----------------|
| AI output format | Eng 3 | Needed to convert AI results into events |
| Calendar generator interface | Eng 4 | Required for export endpoint |
| Frontend needs | Eng 1 | Shapes response formats |

**Blocking Risks:**
- Event schema must align with Eng 3 early
- Late schema changes cause API refactors

---

### 👨‍💻 Engineer 3 — AI / NLP Event Extraction

**Focus:** Intelligence and automation

#### Responsibilities

- Design AI extraction pipeline using LangChain
- Create prompts to detect:
  - Lectures
  - Assignment deadlines
  - Exams and quizzes
  - Instructor and TA office hours
- Identify dates, times, and recurring patterns
- Ignore non-calendar-relevant content
- Flag ambiguous or incomplete information
- Convert AI outputs into structured event components
- Optimize extraction accuracy
- Test against multiple real course outlines

#### Project Structure Ownership
```
ai/
├── prompts/
├── chains/
└── schemas/
```

#### Phases Covered
- Phase 4: Information Extraction
- Phase 5: Event Structuring (AI output)
- Phase 8: Accuracy Testing & Refinement

#### Parallel Work & Dependencies

| Dependency | Provided By | Why It Matters |
|------------|-------------|----------------|
| Clean text format | Eng 2 | AI accuracy depends on text quality |
| Event schema | Eng 2 + Eng 4 | Output must match calendar requirements |

**Blocking Risks:**
- Schema mismatches cause integration failures
- Required vs optional fields must be agreed early

---

### 👨‍💻 Engineer 4 — Calendar Generation, Validation & QA

**Focus:** Output correctness, reliability, and testing

#### Responsibilities

- Implement .ics file generation using iCalendar
- Support:
  - One-time events
  - Recurring events (RRULE)
- Ensure compatibility with:
  - Google Calendar
  - Apple Calendar
  - Outlook
- Validate date/time formats and time zones
- Deduplicate events and handle edge cases
- Write automated tests for:
  - Event validation
  - Calendar generation
- Lead error handling and feedback consistency

#### Project Structure Ownership
```
backend/services/ics_generator.py
backend/services/event_validator.py
backend/tests/
```

#### Phases Covered
- Phase 5: Event Validation
- Phase 7: Calendar File Generation
- Phase 8: Error Handling, Testing & Demo Readiness

#### Parallel Work & Dependencies

| Dependency | Provided By | Why It Matters |
|------------|-------------|----------------|
| Final event model | Eng 2 + Eng 3 | Required to generate valid calendars |
| Frontend UX expectations | Eng 1 | Ensures consistent error messaging |

**Blocking Risks:**
- .ics generation blocked until event schema is stable
- Time zone handling must be agreed early

---

### 🔄 Collaboration & Integration Points

| Area | Engineers Involved |
|------|-------------------|
| Event Data Model | Eng 2, 3, 4 |
| API Contracts | Eng 1, 2 |
| AI Output Schema | Eng 2, 3 |
| Calendar Compatibility | Eng 1, 4 |
| Demo Flow | All |

### 🚨 Critical Integration Points (High Risk)

#### 1️⃣ Event Schema Lock (Highest Priority)
- **Engineers:** Eng 2 + 3 + 4
- Must be finalized before Phase 4
- Affects AI output, backend validation, frontend UI, and calendar generation

#### 2️⃣ API Contract Freeze
- **Engineers:** Eng 1 + 2
- Upload, extract, and export endpoints
- Frontend may mock early, but contracts must freeze before demo

#### 3️⃣ Recurring Event Logic
- **Engineers:** Eng 3 + 4
- AI detects recurrence
- Calendar generator encodes RRULE
- Requires shared interpretation of lectures and office hours

### 🧭 Parallel Execution Strategy

#### Early Parallel Work
- **Eng 1:** UI mockups
- **Eng 2:** API + PDF parsing
- **Eng 3:** AI extraction logic
- **Eng 4:** .ics generation

#### Midpoint
- Lock schema (ALL)
- Integrate AI → backend
- Connect frontend to API

#### Final Stage
- Error handling
- Review UI
- Cross-platform calendar testing
- Demo prep & polish

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

