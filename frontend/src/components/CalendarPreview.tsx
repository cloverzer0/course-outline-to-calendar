"use client"

import * as React from "react"
import FullCalendar from "@fullcalendar/react"
import dayGridPlugin from "@fullcalendar/daygrid"
import timeGridPlugin from "@fullcalendar/timegrid"
import interactionPlugin from "@fullcalendar/interaction"

export type CalendarPreviewEvent = {
  id: string
  title: string
  start: Date
  end?: Date
  location?: string
}

export function CalendarPreview({ events }: { events: CalendarPreviewEvent[] }) {
  const fcEvents = React.useMemo(
    () =>
      events.map((e) => ({
        id: e.id,
        title: e.title,
        start: e.start,
        end: e.end,
        extendedProps: { location: e.location },
      })),
    [events],
  )

  return (
    <div className="rounded-xl border bg-card p-3">
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        headerToolbar={{
          left: "prev,next today",
          center: "title",
          right: "dayGridMonth,timeGridWeek,timeGridDay",
        }}
        height="auto"
        events={fcEvents}
        eventTimeFormat={{ hour: "2-digit", minute: "2-digit", meridiem: "short" }}
        eventDidMount={(info) => {
          const loc = info.event.extendedProps["location"]
          if (loc) info.el.title = `${info.event.title}\n${loc}`
        }}
        selectable={false}
        editable={false}
        eventStartEditable={false}
        eventDurationEditable={false}
      />
    </div>
  )
}
