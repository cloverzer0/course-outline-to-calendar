// src/app/review/page.tsx
"use client"

import * as React from "react"
import { parseIcs, type ParsedEvent } from "@/lib/ics"
import { CalendarPreview, type CalendarPreviewEvent } from "@/components/CalendarPreview"

const SAMPLE_ICS = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Course Outline to Calendar//EN
BEGIN:VEVENT
UID:demo-1
DTSTAMP:20260101T000000Z
SUMMARY:COMP 2404 Lecture
DTSTART:20260110T140000Z
DTEND:20260110T153000Z
LOCATION:Herzberg 4150
END:VEVENT
END:VCALENDAR
`

export default function ReviewPage() {
  const [icsText] = React.useState(SAMPLE_ICS)
  const [events, setEvents] = React.useState<CalendarPreviewEvent[]>([])

  React.useEffect(() => {
    const parsed: ParsedEvent[] = parseIcs(icsText)
    setEvents(
      parsed.map((e: ParsedEvent) => ({
        id: e.uid,
        title: e.title,
        start: e.start,
        end: e.end,
        location: e.location,
      })),
    )
  }, [icsText])

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <h1 className="text-2xl font-semibold">Calendar Preview</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Read-only preview generated from your ICS.
        </p>

        <div className="mt-6">
          <CalendarPreview events={events} />
        </div>
      </div>
    </main>
  )
}
