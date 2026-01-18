import { CalendarPreviewEvent } from "@/components/CalendarPreview"

type MockEvent = {
  id: string
  title: string
  start: string
  end: string
  location?: string
}

type MockCourse = {
  course_code: string
  course_name: string
  events: MockEvent[]
}

export function mockToCalendarEvents(
  courses: MockCourse[]
): CalendarPreviewEvent[] {
  return courses.flatMap((course) =>
    course.events.map((e) => ({
      id: e.id,
      title: `${course.course_code} — ${e.title}`,
      start: new Date(e.start), // ✅ FIX
      end: new Date(e.end),     // ✅ FIX
      location: e.location,
    }))
  )
}
