/**
 * TypeScript types matching backend Pydantic models
 */

export enum EventType {
  LECTURE = "lecture",
  EXAM = "exam",
  ASSIGNMENT = "assignment",
  PROJECT = "project",
  OFFICE_HOURS = "office_hours",
  OTHER = "other"
}

export enum RecurrenceFrequency {
  DAILY = "daily",
  WEEKLY = "weekly",
  MONTHLY = "monthly"
}

export interface RecurrenceRule {
  frequency: RecurrenceFrequency;
  interval?:  number;
  daysOfWeek?: number[];  // 0=Sunday, 6=Saturday
  endDate?: string;       // YYYY-MM-DD
  count?: number;
}

export interface CalendarEvent {
  id?:  string;
  title: string;
  startDateTime: string;  // ISO 8601 format
  endDateTime:  string;    // ISO 8601 format
  location:  string;
  description?: string;
  type?:  EventType;
  recurrence?: RecurrenceRule;
  needsReview?: boolean;
  confidence?: number;
}

export interface CourseCalendar {
  course_code: string;
  course_name: string;
  semester?:  string;
  instructor?: string;
  events: CalendarEvent[];
  event_count?:  number;
  needs_review_count?: number;
}

export interface MultiCourseCalendar {
  courses: CourseCalendar[];
  total_courses: number;
  total_events: number;
  total_needs_review: number;
}

// API Response Types
export interface UploadResponse {
  status: string;
  message:  string;
  data:  {
    file_id: string;
    original_filename: string;
    file_size_bytes: number;
    file_size_mb: number;
    upload_timestamp: string;
    file_path: string;
  };
}

export interface CourseExtractionResponse {
  session_id: string;
  courses: CourseCalendar[];
  total_courses: number;
  total_events: number;
  total_needs_review: number;
}

export interface SessionResponse {
  status: string;
  message: string;
  session_id: string;
  next_step?: string;
}

export interface SessionSummary {
  session_id: string;
  total_courses: number;
  total_events: number;
  total_needs_review: number;
  courses:  {
    course_code: string;
    course_name: string;
    semester?: string;
    instructor?: string;
    event_count: number;
    needs_review_count: number;
    event_breakdown: Record<string, number>;
  }[];
}