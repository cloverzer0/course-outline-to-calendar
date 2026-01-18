# Course Outline to Calendar

## Overview

Course Outline to Calendar is an AI-powered web application that automatically converts course outline PDFs into structured calendar events. The application removes the need for students to manually extract dates, times, and schedules from academic documents and recreate them in digital calendars.

By uploading a course outline, users can generate a fully populated, importable `.ics` calendar file containing lectures, assignments, exams, office hours, and other academic events.

---

## Problem Statement

Students rely on digital calendars to manage lectures, assignments, tests, exams, and office hours. Although all of this information is provided by instructors in course outlines, these documents are typically distributed as static PDF files that are difficult to navigate efficiently.

Students must repeatedly scan course outlines to locate important dates and times, then manually create individual calendar events. This process is time-consuming, repetitive, and prone to error, especially when managing multiple courses.

---

## Solution

Course Outline to Calendar automates the conversion of course outlines into digital calendar events. The system extracts scheduling information from uploaded PDFs, validates and structures the data, and generates a standards-compliant `.ics` file compatible with common calendar platforms.

Users are provided with a review interface that allows them to inspect, edit, or remove events before exporting the final calendar.

---

## Features

- Upload course outline PDFs for automated processing
- Extract lectures, assignments, exams, and office hours
- Detect recurring events and deadlines
- Flag ambiguous or incomplete information for user review
- Preview and edit events before export
- Generate `.ics` files compatible with Google Calendar, Apple Calendar, and Outlook

---

## System Architecture

The application consists of three main layers:

- **Frontend**: A Next.js (React) application responsible for file upload, event review, editing, and calendar export
- **Backend**: A FastAPI server that handles PDF parsing, data validation, event structuring, and calendar generation
- **AI Pipeline**: A LangChain-based extraction pipeline that identifies calendar-relevant information from cleaned course outline text

---

## Project Structure
```
course-outline-to-calendar/
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── services/
│   │   ├── types/
│   │   └── styles/
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── utils/
│   └── tests/
│
├── ai/
│   ├── prompts/
│   ├── chains/
│   └── schemas/
│
├── docs/
├── scripts/
└── data/
```

---

## Event Data Model

The application uses a unified calendar event schema shared across the frontend, backend, and AI pipeline.

### Required Fields
- `title`
- `startDateTime`
- `endDateTime`
- `location`

### Optional Fields
- `description`
- `recurrence`
- `needsReview`

This schema is defined early and treated as stable to avoid integration issues.

---

## Technology Stack

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- Python
- Pydantic

### AI / NLP
- LangChain
- OpenAI API

### Calendar Generation
- iCalendar (.ics) standard

---

## Getting Started

### Prerequisites

- Node.js 18 or later
- Python 3.10 or later
- Git
- OpenAI API key (or compatible provider)

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/course-outline-to-calendar.git
cd course-outline-to-calendar
```

### 2. Environment Configuration

Create environment files for both the backend and frontend.

#### Backend Environment Variables

Create a `.env` file inside the `backend/` directory with the following contents:
```env
OPENAI_API_KEY=your_api_key_here
```

If additional environment variables are required, refer to `.env.example`.

#### Frontend Environment Variables

Create a `.env.local` file inside the `frontend/` directory with the following contents:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Backend Setup

It is strongly recommended to use a Python virtual environment.

Create and activate the virtual environment:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:
```bash
pip install -r requirements.txt
```

Run the backend server:
```bash
uvicorn main:app --reload --port 8000
```

Verify that the backend is running by visiting:
```
http://127.0.0.1:8000/docs
```

### 4. Frontend Setup

In a new terminal window, install frontend dependencies:
```bash
cd frontend
npm install
```

Start the frontend development server:
```bash
npm run dev
```

The application will be available at:
```
http://localhost:3000
```

---

## Usage

1. Open the application in your browser
2. Upload a course outline PDF
3. Review the extracted calendar events
4. Edit, add, or remove events as needed
5. Export the final calendar as a `.ics` file
6. Import the file into your preferred calendar application

---

## Testing

Backend tests are located in the `backend/tests/` directory.

Run tests with:
```bash
cd backend
pytest
```

---

## Demo Flow

Upload → Review → Edit → Export → Import

---

## License

MIT License
