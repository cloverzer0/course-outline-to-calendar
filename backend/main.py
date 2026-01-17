from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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


@app.get("/")
async def root():
    """
    Root endpoint - confirms API is running
    """
    return {
        "message": "Course Outline to Calendar API is running!",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {"status": "ok"}