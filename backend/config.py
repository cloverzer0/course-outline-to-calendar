"""
Application Configuration
Centralized settings for the backend
"""

from pathlib import Path
import os

# Get the backend root directory
BACKEND_ROOT = Path(__file__).parent

# Directory paths
DATA_DIR = BACKEND_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
EXTRACTED_TEXT_DIR = DATA_DIR / "extracted_text"

# File constraints
ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10 GB in bytes