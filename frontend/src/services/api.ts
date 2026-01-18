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
  MultiCourseCalendar
} from '@/types/calendar';

// Backend API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Helper function to handle API errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP ${response.status}: ${response. statusText}`
    }));
    throw new Error(error.detail || 'API request failed');
  }
  return response.json();
}


/**
 * COMBINED ENDPOINT APPROACH 
 * Upload + Extract in one call
 */
export async function upload(
  file: File,
  sessionId?:  string
): Promise<CourseExtractionResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const url = new URL(`${API_BASE_URL}/api/process/upload-and-extract`);
  
  if (sessionId) {
    url.searchParams.append('session_id', sessionId);
  }
  
  const response = await fetch(url.toString(), {
    method: 'POST',
    body: formData
  });
  
  return handleResponse<CourseExtractionResponse>(response);
}






// =================== SEPERATE ENDPOINT APPROACH ===============


// ========================================
// SESSION MANAGEMENT
// ========================================

/**
 * Create a new multi-course session
 */
export async function createSession(): Promise<SessionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/session/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  return handleResponse<SessionResponse>(response);
}

/**
 * Get session summary (all courses and events)
 */
export async function getSessionSummary(sessionId: string): Promise<SessionSummary> {
  const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}`);
  return handleResponse<SessionSummary>(response);
}

/**
 * Delete a session
 */
export async function deleteSession(sessionId: string): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}`, {
    method: 'DELETE'
  });
  return handleResponse(response);
}

// ========================================
// FILE UPLOAD
// ========================================

/**
 * Upload a course outline PDF
 */
export async function uploadPDF(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/api/upload/`, {
    method: 'POST',
    body: formData
    // Don't set Content-Type header - browser sets it automatically with boundary
  });
  
  return handleResponse<UploadResponse>(response);
}

// ========================================
// EVENT EXTRACTION
// ========================================

/**
 * Extract events from uploaded PDF using AI
 */
export async function extractEvents(
  fileId: string,
  sessionId?:  string
): Promise<CourseExtractionResponse> {
  const url = new URL(`${API_BASE_URL}/api/extract/${fileId}`);
  
  if (sessionId) {
    url.searchParams.append('session_id', sessionId);
  }
  
  const response = await fetch(url. toString(), {
    method: 'POST'
  });
  
  return handleResponse<CourseExtractionResponse>(response);
}

/**
 * Get extraction summary for a session
 */
export async function getExtractionSummary(sessionId: string): Promise<SessionSummary> {
  const response = await fetch(`${API_BASE_URL}/api/extract/session/${sessionId}/summary`);
  return handleResponse<SessionSummary>(response);
}

// ========================================
// EVENT MANAGEMENT
// ========================================

/**
 * Get all events for a session
 */
export async function getSessionEvents(sessionId: string): Promise<MultiCourseCalendar> {
  const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}`);
  const summary = await handleResponse<SessionSummary>(response);
  
  // Transform summary to MultiCourseCalendar format
  // Note: This might need adjustment based on your actual endpoint response
  return {
    courses: [],  // You might need a separate endpoint for full event details
    total_courses: summary. total_courses,
    total_events: summary.total_events,
    total_needs_review:  summary.total_needs_review
  };
}

/**
 * Update an event
 */
export async function updateEvent(
  sessionId: string,
  eventId: string,
  event: CalendarEvent
): Promise<CalendarEvent> {
  const response = await fetch(`${API_BASE_URL}/api/events/${sessionId}/${eventId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON. stringify(event)
  });
  
  return handleResponse<CalendarEvent>(response);
}

/**
 * Delete an event
 */
export async function deleteEvent(
  sessionId: string,
  eventId: string
): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/events/${sessionId}/${eventId}`, {
    method: 'DELETE'
  });
  
  return handleResponse(response);
}

// ========================================
// CALENDAR EXPORT
// ========================================

/**
 * Export session to . ics calendar file
 */
export async function exportCalendar(sessionId: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/calendar/export/session/${sessionId}`, {
    method: 'POST'
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP ${response.status}: ${response.statusText}`
    }));
    throw new Error(error. detail || 'Export failed');
  }
  
  return response.blob();
}

/**
 * Download the exported .ics file
 */
export async function downloadCalendar(sessionId: string, filename?:  string): Promise<void> {
  const blob = await exportCalendar(sessionId);
  
  // Create download link
  const url = window.URL.createObjectURL(blob);
  const a = document. createElement('a');
  a.href = url;
  a. download = filename || `my_courses_${sessionId}.ics`;
  document.body.appendChild(a);
  a.click();
  
  // Cleanup
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

/**
 * Preview calendar content (for debugging)
 */
export async function previewCalendar(sessionId: string): Promise<{
  file_id: string;
  event_count: number;
  ics_content: string;
  preview_url: string;
}> {
  const response = await fetch(`${API_BASE_URL}/api/calendar/export/session/${sessionId}/preview`, {
    method: 'POST'
  });
  
  return handleResponse(response);
}

// ========================================
// COMBINED WORKFLOWS
// ========================================

/**
 * Upload PDF and extract events in one flow
 */
export async function uploadAndExtract(
  file: File,
  sessionId?:  string
): Promise<{ upload:  UploadResponse; extraction: CourseExtractionResponse }> {
  // Step 1: Upload PDF
  const uploadResult = await uploadPDF(file);
  
  // Step 2: Extract events
  const extractionResult = await extractEvents(
    uploadResult.data.file_id,
    sessionId
  );
  
  return {
    upload: uploadResult,
    extraction: extractionResult
  };
}