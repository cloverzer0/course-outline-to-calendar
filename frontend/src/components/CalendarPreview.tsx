"use client"

import * as React from "react"
import FullCalendar from "@fullcalendar/react"
import dayGridPlugin from "@fullcalendar/daygrid"
import timeGridPlugin from "@fullcalendar/timegrid"
import interactionPlugin from "@fullcalendar/interaction"
import { Clock, MapPin, Calendar as CalendarIcon } from "lucide-react"

export type CalendarPreviewEvent = {
  id: string
  title: string
  start: Date
  end?: Date
  location?: string
}

export function CalendarPreview({ events }: { events: CalendarPreviewEvent[] }) {
  const [tooltip, setTooltip] = React.useState<{
    x: number
    y: number
    event: CalendarPreviewEvent
  } | null>(null)
  const tooltipRef = React.useRef<HTMLDivElement>(null)

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

  function formatTime(date: Date): string {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
  }

  function formatDate(date: Date): string {
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
    })
  }

  function formatFullDateTime(date: Date): string {
    return date.toLocaleString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
  }

  function getDuration(start: Date, end?: Date): string {
    if (!end) return "No end time"
    const ms = end.getTime() - start.getTime()
    const hours = Math.floor(ms / (1000 * 60 * 60))
    const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60))
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  function isToday(date: Date): boolean {
    const today = new Date()
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    )
  }

  function isPast(date: Date): boolean {
    return date < new Date()
  }

  return (
    <div className="relative rounded-xl border bg-card p-3">
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
        eventTimeFormat={{ hour: "2-digit", minute: "2-digit", hour12: true }}
        eventDidMount={(info) => {
          const loc = info.event.extendedProps["location"]
          if (loc) info.el.title = `${info.event.title}\n${loc}`

          // Add hover handlers
          info.el.addEventListener("mouseenter", () => {
            const event = events.find((ev) => ev.id === info.event.id)
            if (event) {
              const rect = info.el.getBoundingClientRect()
              setTooltip({
                x: rect.left + window.scrollX,
                y: rect.top + window.scrollY - 10,
                event,
              })
            }
          })

          info.el.addEventListener("mouseleave", () => {
            // Delay hiding to allow moving to tooltip
            setTimeout(() => {
              if (!tooltipRef.current?.matches(":hover")) {
                setTooltip(null)
              }
            }, 100)
          })

          // Add hover styles
          info.el.classList.add(
            "cursor-pointer",
            "transition-all",
            "hover:shadow-md",
            "hover:scale-105",
          )
        }}
        selectable={false}
        editable={false}
        eventStartEditable={false}
        eventDurationEditable={false}
      />

      {/* Enhanced Tooltip */}
      {tooltip && (
        <div
          ref={tooltipRef}
          className="pointer-events-auto fixed z-50 w-96 rounded-lg border border-border bg-card p-5 shadow-xl"
          style={{
            left: `${tooltip.x}px`,
            top: `${tooltip.y}px`,
            transform: "translateY(-100%)",
          }}
          onMouseLeave={() => setTooltip(null)}
        >
          <div className="space-y-4">
            {/* Title */}
            <div>
              <h3 className="line-clamp-2 text-lg font-bold text-foreground">
                {tooltip.event.title}
              </h3>
              {isPast(tooltip.event.start) && (
                <p className="mt-1 text-xs text-muted-foreground">📌 Past Event</p>
              )}
              {isToday(tooltip.event.start) && (
                <p className="mt-1 inline-block rounded bg-accent px-2 py-0.5 text-xs text-accent-foreground">
                  🔴 Today
                </p>
              )}
            </div>

            {/* Date */}
            <div className="flex items-start gap-3 border-b border-border pb-2">
              <CalendarIcon className="mt-0.5 h-4 w-4 flex-shrink-0 text-muted-foreground" />
              <div className="text-sm">
                <p className="font-medium text-foreground">
                  {formatDate(tooltip.event.start)}
                </p>
                {tooltip.event.end &&
                  tooltip.event.start.toDateString() !==
                    tooltip.event.end.toDateString() && (
                    <p className="mt-1 text-xs text-muted-foreground">
                      → {formatDate(tooltip.event.end)}
                    </p>
                  )}
              </div>
            </div>

            {/* Time */}
            <div className="flex items-start gap-3 border-b border-border pb-2">
              <Clock className="mt-0.5 h-4 w-4 flex-shrink-0 text-muted-foreground" />
              <div className="text-sm">
                <p className="font-medium text-foreground">
                  {formatTime(tooltip.event.start)}
                </p>
                {tooltip.event.end && (
                  <>
                    <p className="mt-1 text-xs text-muted-foreground">
                      → {formatTime(tooltip.event.end)}
                    </p>
                    <p className="mt-2 text-xs text-muted-foreground">
                      Duration:{" "}
                      <span className="font-semibold">
                        {getDuration(tooltip.event.start, tooltip.event.end)}
                      </span>
                    </p>
                  </>
                )}
              </div>
            </div>

            {/* Location */}
            {tooltip.event.location && (
              <div className="flex items-start gap-3">
                <MapPin className="mt-0.5 h-4 w-4 flex-shrink-0 text-muted-foreground" />
                <div className="text-sm">
                  <p className="line-clamp-2 font-medium text-foreground">
                    {tooltip.event.location}
                  </p>
                </div>
              </div>
            )}

            {/* Full details footer */}
            <div className="mt-2 border-t border-border pt-2 text-xs text-muted-foreground">
              <p>Full: {formatFullDateTime(tooltip.event.start)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
