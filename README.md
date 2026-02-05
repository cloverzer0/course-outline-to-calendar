# Course Outline to Calendar

An AI-powered web application that automatically converts course outline PDFs into calendar events, eliminating the tedious manual process of setting up academic calendars.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

## Overview

Many students rely on digital calendars to keep their academic lives organized—tracking classes, assignment deadlines, tests, office hours, and locations. While this system is effective, setting it up is unnecessarily tedious.

All of this critical information is provided by professors in a course outline, typically as a PDF document. Although course outlines are essential, they are static, text-heavy, and difficult to navigate. Students must repeatedly open and scan these PDFs to find small but important details, such as upcoming deadlines or office hours, until the information is fully memorized.

This application solves this problem by automatically converting course outlines into calendar events. Simply upload a course outline PDF, review the extracted events, and download an .ics calendar file that can be imported into Google Calendar, Apple Calendar, or Outlook.

## Features

- 📄 **PDF Upload & Text Extraction**: Upload course outline PDFs and extract text content
- 🤖 **AI-Powered Event Detection**: Automatically identify lectures, assignments, exams, and office hours using LangChain and OpenAI
- ✏️ **Interactive Event Editor**: Review and edit extracted events before export
- 📅 **Calendar Preview**: Visualize events in a calendar view using FullCalendar
- 📥 **ICS Export**: Generate .ics files compatible with major calendar applications
- 🔄 **Recurring Events Support**: Handle recurring lectures and events using RRULE

## Tech Stack

### Frontend
- **Framework**: Next.js 15 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI, shadcn/ui
- **Calendar**: FullCalendar
- **ICS Handling**: ical.js
- **Animations**: Framer Motion
- **Notifications**: Sonner

### Backend
- **Framework**: FastAPI (Python)
- **AI/LLM**: LangChain, OpenAI API
- **PDF Processing**: PyMuPDF
- **Calendar Generation**: icalendar
- **Data Validation**: Pydantic
- **Date Parsing**: dateutil

### Infrastructure
- **Package Manager (Frontend)**: npm
- **Package Manager (Backend)**: pip/conda
- **Development**: Docker Compose (optional)

## Prerequisites

Before running this project, ensure you have the following installed:

- **Node.js** (v18 or higher) and npm
- **Python** (v3.9 or higher)
- **OpenAI API Key** (for AI-powered event extraction)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd course-outline-to-calendar
```

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## Running the Project

### Development Mode

You need to run both the backend and frontend servers:

#### Terminal 1: Start Backend Server

```bash
cd backend
source venv/bin/activate  # If using virtual environment
uvicorn main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`

#### Terminal 2: Start Frontend Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Using the Development Script (Optional)

```bash
# Make the script executable
chmod +x scripts/dev_start.sh

# Run both servers
./scripts/dev_start.sh
```

### Production Build

#### Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run build
npm start
```

## Usage

1. **Navigate** to `http://localhost:3000`
2. **Upload** a course outline PDF using the file upload interface
3. **Review** the automatically extracted events in the preview section
4. **Edit** any events that need adjustments (dates, times, titles, locations)
5. **Preview** events in the calendar view
6. **Download** the generated .ics file
7. **Import** the .ics file into your preferred calendar application

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/upload` - Upload course outline PDF
- `POST /api/extract` - Extract text from PDF
- `POST /api/events` - Process text and extract events
- `POST /api/calendar/generate` - Generate .ics file
- `GET /api/calendar/{session_id}` - Download generated calendar

## Project Structure

```
course-outline-to-calendar/
│
├── README.md
├── docker-compose.yml
├── scripts/
│   ├── dev_start.sh              # Development startup script
│   └── cleanup_uploads.py
│
├── docs/                         # Documentation
│   ├── background.md
│   ├── problem-statement.md
│   ├── solution.md
│   ├── functional-requirements.md
│   ├── implementation-plan.md
│   └── demo-flow.md
│
├── frontend/                     # Next.js React application
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   └── src/
│       ├── app/                  # Next.js app routes
│       │   ├── page.tsx         # Main upload page
│       │   ├── layout.tsx
│       │   └── review/          # Event review page
│       ├── components/          # React components
│       │   ├── FileUpload.tsx
│       │   ├── EventEditor.tsx
│       │   ├── EventPreview.tsx
│       │   ├── CalendarPreview.tsx
│       │   └── ui/             # shadcn/ui components
│       ├── services/           # API integration
│       │   └── api.ts
│       ├── types/              # TypeScript types
│       └── styles/             # Global styles
│
├── backend/                     # FastAPI Python application
│   ├── requirements.txt
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Configuration
│   ├── api/
│   │   ├── routes/            # API endpoints
│   │   │   ├── upload.py
│   │   │   ├── extract.py
│   │   │   ├── events.py
│   │   │   ├── calendar.py
│   │   │   └── combined.py
│   │   └── dependencies.py
│   ├── services/              # Business logic
│   │   ├── pdf_parser.py
│   │   ├── text_cleaner.py
│   │   ├── ai_service.py
│   │   ├── event_validator.py
│   │   ├── event_storage.py
│   │   └── ics_generator.py
│   ├── models/                # Data models
│   │   └── event.py
│   └── utils/                 # Helper functions
│       ├── date_parser.py
│       ├── recurrence_helper.py
│       └── error_handler.py
│
├── ai/                        # AI processing pipeline
│   ├── prompts/
│   │   └── extract_events.txt
│   ├── chains/
│   │   └── course_outline_chain.py
│   └── schemas/
│       └── event_schema.json
│
└── data/                      # Runtime data
    ├── uploads/              # Uploaded PDFs (temporary)
    ├── calendars/            # Generated .ics files
    └── sample_outlines/      # Sample course outlines
```

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Model configuration
OPENAI_MODEL=gpt-4

# Optional: Server configuration
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
```

## Troubleshooting

### Backend Issues

**ImportError or ModuleNotFoundError**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**OpenAI API Errors**
- Verify your API key is set in `.env`
- Check API key validity and credits at platform.openai.com

### Frontend Issues

**Module not found errors**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Port already in use**
```bash
# Use a different port
npm run dev -- -p 3001
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/)
- AI integration using [LangChain](https://www.langchain.com/) and [OpenAI](https://openai.com/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)

---

**Made with ❤️ for students tired of manual calendar setup**


**Deliverable:** Stable, demo-ready MVP

---

## Team Work Assignment, Responsibilities & Dependencies

**Team Size:** 4 Engineers

### Global Dependency (Applies to Everyone)

#### Event Data Model & API Contract (Highest Priority)

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

**Changing this late causes widespread rework and integration risk.**

---

### Engineer 1 — Frontend & User Experience

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

### Engineer 2 — Backend API & File Processing

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

### Engineer 3 — AI / NLP Event Extraction

**Focus:** Intelligence and automation

#### Responsibilities

- Design AI extraction pipeline using LangChain
- Create prompts to detect:
  - Lectures
  - Assignment deadlines
  - Quizzes
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

### Engineer 4 — Calendar Generation, Validation & QA

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

### Collaboration & Integration Points

| Area | Engineers Involved |
|------|-------------------|
| Event Data Model | Eng 2, 3, 4 |
| API Contracts | Eng 1, 2 |
| AI Output Schema | Eng 2, 3 |
| Calendar Compatibility | Eng 1, 4 |
| Demo Flow | All |

### Critical Integration Points (High Risk)

#### Event Schema Lock (Highest Priority)
- **Engineers:** Eng 2 + 3 + 4
- Must be finalized before Phase 4
- Affects AI output, backend validation, frontend UI, and calendar generation

#### API Contract Freeze
- **Engineers:** Eng 1 + 2
- Upload, extract, and export endpoints
- Frontend may mock early, but contracts must freeze before demo

#### Recurring Event Logic
- **Engineers:** Eng 3 + 4
- AI detects recurrence
- Calendar generator encodes RRULE
- Requires shared interpretation of lectures and office hours

### Parallel Execution Strategy

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

