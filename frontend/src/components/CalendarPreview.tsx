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
  const hoverTimeoutRef = React.useRef<NodeJS.Timeout | null>(null)

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
          // Add hover handlers
          info.el.addEventListener("mouseenter", () => {
            const event = events.find((ev) => ev.id === info.event.id)
            if (event) {
              const rect = info.el.getBoundingClientRect()
              
              // Clear any existing timeout
              if (hoverTimeoutRef.current) {
                clearTimeout(hoverTimeoutRef.current)
              }
              
              // Set 3-second delay before showing tooltip
              hoverTimeoutRef.current = setTimeout(() => {
                setTooltip({
                  x: rect.left + window.scrollX,
                  y: rect.top + window.scrollY - 10,
                  event,
                })
              }, 1000)
            }
          })

          info.el.addEventListener("mouseleave", () => {
            // Clear the timeout if user stops hovering before 5 seconds
            if (hoverTimeoutRef.current) {
              clearTimeout(hoverTimeoutRef.current)
              hoverTimeoutRef.current = null
            }
            
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
          className="pointer-events-auto fixed z-50 w-64 rounded-md border border-border bg-card p-3 shadow-lg"
          style={{
            left: `${tooltip.x}px`,
            top: `${tooltip.y}px`,
            transform: "translateY(-100%)",
          }}
          onMouseLeave={() => setTooltip(null)}
        >
          <div className="space-y-2">
            {/* Title */}
            <div>
              <h3 className="line-clamp-2 text-sm font-semibold text-foreground">
                {tooltip.event.title}
              </h3>
            </div>

            {/* Date & Time */}
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <CalendarIcon className="h-3 w-3 flex-shrink-0" />
              <span>{formatDate(tooltip.event.start)}</span>
            </div>
            
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3 flex-shrink-0" />
              <span>
                {formatTime(tooltip.event.start)}
                {tooltip.event.end && ` - ${formatTime(tooltip.event.end)}`}
              </span>
            </div>

            {/* Location */}
            {tooltip.event.location && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <MapPin className="h-3 w-3 flex-shrink-0" />
                <span className="line-clamp-1">{tooltip.event.location}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
