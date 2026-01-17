from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.event import CalendarEvent, EventType

# API Routes
from api.routes import upload, extract, events


# Create the FastAPI app instance
app = FastAPI(
    title="Course Outline to Calendar API",
    description="Backend API for converting course outlines to calendar events",
    version="1.0.0"
)

# Enable CORS - allows frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Register the upload router
app.include_router(upload.router)
app.include_router(extract.router)
app.include_router(events.router)


@app.get("/")
async def root():
    return {
        "message": "Course Outline to Calendar API is running! ",
        "status": "healthy",
         "endpoints": {
            "docs": "/docs",
            "upload": "/api/upload/",
            "extract": "/api/extract/{file_id}",
            "events": "/api/events/{file_id}",
            "stats": "/api/events/{file_id}/stats"
        }
    }


@app.get("/test/event", response_model=CalendarEvent)
async def test_event():
    """Returns a sample event to test the model"""
    return CalendarEvent(
        id="event-123",
        title="CS101 Lecture",
        startDateTime="2026-01-20T10:00:00",
        endDateTime="2026-01-20T11:30:00",
        location="Room 302",
        description="Introduction to Programming",
        type=EventType.LECTURE,
        needsReview=False
    )