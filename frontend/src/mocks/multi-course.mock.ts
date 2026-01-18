export type MockEvent = {
  id: string
  title: string
  start: string
  end: string
  location?: string
}

export type MockCourse = {
  course_code: string
  course_name: string
  events: MockEvent[]
}

export type MultiCourseMock = {
  courses: MockCourse[]
}

export const MULTI_COURSE_MOCK: MultiCourseMock = {
  courses: [
    {
      course_code: "CS 301",
      course_name: "Data Structures",
      events: [
        {
          id: "cs301-lecture-1",
          title: "CS 301 - Data Structures",
          start: "2026-01-20T14:00:00",
          end: "2026-01-20T15:20:00",
          location: "Room 101, Science Building",
        },
        {
          id: "cs301-midterm",
          title: "CS 301 - Midterm Exam",
          start: "2026-03-05T10:00:00",
          end: "2026-03-05T12:00:00",
          location: "Exam Hall A",
        },
      ],
    },
    {
      course_code: "MATH 205",
      course_name: "Calculus II",
      events: [
        {
          id: "math205-lecture-1",
          title: "MATH 205 - Calculus II",
          start: "2026-01-21T10:00:00",
          end: "2026-01-21T11:30:00",
          location: "Math Building, Room 205",
        },
        {
          id: "math205-midterm",
          title: "MATH 205 - Midterm Test",
          start: "2026-02-25T14:00:00",
          end: "2026-02-25T16:00:00",
          location: "Math Building, Room 100",
        },
      ],
    },
  ],
}
