from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.event import CalendarEvent, EventType

# Import routers
from api.routes import upload, extract, events, calendar, session, combined

app = FastAPI(
    title="Course Outline to Calendar API",
    description="Multi-course calendar generation from PDF outlines",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(session.router)
app.include_router(upload. router)
app.include_router(extract. router)
app.include_router(events.router)
app.include_router(calendar.router)
app.include_router(combined.router)

@app.get("/")
async def root():
    return {
        "message": "Course Outline to Calendar API v2.0 - Multi-Course Support",
        "status": "healthy",
        "features": [
            "Multi-course calendar generation",
            "AI-powered event extraction",
            "Review and edit events",
            "Export to . ics format"
        ],
        "endpoints": {
            "docs": "/docs",
            "create_session": "/api/session/create",
            "upload":  "/api/upload/",
            "extract": "/api/extract/{file_id}? session_id=XXX&course_code=CS301",
            "export_all": "/api/calendar/export/session/{session_id}",
            "session_info": "/api/session/{session_id}"
        }
    }