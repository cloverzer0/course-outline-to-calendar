/**
 * Backend API Service
 * Handles all communication with FastAPI backend
 */

import {
  UploadResponse,
  CourseExtractionResponse,
  SessionResponse,
  SessionSummary,
  CalendarEvent,
  MultiCourseCalendar,
  CourseCalendar
} from '@/types/calendar';

// Backend API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Helper function to handle API errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP ${response.status}:  ${response.statusText}`
    }));
    throw new Error(error.detail || 'API request failed');
  }
  return response.json();
}

// ========================================
// MAIN FUNCTION FOR YOUR FRONTEND
// ========================================

/**
 * Upload multiple course outline PDFs and extract all events
 * 
 * This function: 
 * 1. Creates a session
 * 2. Uploads each PDF one by one
 * 3. Extracts events from each PDF
 * 4. Returns session_id (token) for review page
 */
export async function uploadCourseOutlines(
  files: File[]
): Promise<{ token: string; courses: CourseExtractionResponse[] }> {
  
  if (files.length === 0) {
    throw new Error('No files provided');
  }

  // Step 1: Create session
  const sessionResponse = await createSession();
  const sessionId = sessionResponse.session_id;
  
  console.log('[Upload] Created session:', sessionId);

  // Step 2: Upload and extract each PDF
  const courses: CourseExtractionResponse[] = [];
  
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    console.log(`[Upload] Processing ${i + 1}/${files.length}:  ${file.name}`);
    
    try {
      // Upload + Extract in one call
      const result = await uploadAndExtractCombined(file, sessionId);
      courses.push(result);
      
      console.log(`[Upload] ✓ Extracted ${result.total_events} events from ${result.course_code}`);
      
    } catch (error) {
      console.error(`[Upload] ✗ Failed to process ${file.name}: `, error);
      // Continue with other files
    }
  }

  if (courses.length === 0) {
    throw new Error('Failed to extract events from any PDF');
  }

  console.log(`[Upload] Success! ${courses.length} courses, session:  ${sessionId}`);

  // Return session_id as "token"
  return {
    token: sessionId,  // ← This is what your frontend expects
    courses
  };
}

// ========================================
// SESSION MANAGEMENT
// ========================================

export async function createSession(): Promise<SessionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/session/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  return handleResponse<SessionResponse>(response);
}

export async function getSessionSummary(sessionId: string): Promise<SessionSummary> {
  const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}`);
  return handleResponse<SessionSummary>(response);
}

// ========================================
// COMBINED UPLOAD + EXTRACT
// ========================================

/**
 * Upload PDF + Extract events in ONE call
 */
export async function uploadAndExtractCombined(
  file: File,
  sessionId: string
): Promise<CourseExtractionResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const url = new URL(`${API_BASE_URL}/api/process/upload-and-extract`);
  url.searchParams.append('session_id', sessionId);
  
  const response = await fetch(url. toString(), {
    method: 'POST',
    body: formData
  });
  
  return handleResponse<CourseExtractionResponse>(response);
}

// ========================================
// CALENDAR EXPORT
// ========================================


/**
 * Get all events for a session (for calendar preview)
 */
export async function getSessionEvents(sessionId: string): Promise<CalendarEvent[]> {
  const response = await fetch(`${API_BASE_URL}/api/events/session/${sessionId}/all`);
  return handleResponse<CalendarEvent[]>(response);
}

/**
 * Export session to .ics file and download
 */
export async function downloadCalendar(sessionId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/calendar/export/session/${sessionId}`, {
    method: 'POST'
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP ${response.status}: ${response.statusText}`
    }));
    throw new Error(error. detail || 'Export failed');
  }
  
  // Get the .ics file as blob
  const blob = await response. blob();
  
  // Create download link
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `my_courses_${sessionId}.ics`;
  document.body.appendChild(a);
  a.click();
  
  // Cleanup
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}