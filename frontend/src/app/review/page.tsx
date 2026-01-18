"use client"

import * as React from "react"
import { useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { CalendarPreview, type CalendarPreviewEvent } from "@/components/CalendarPreview"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ChevronDown } from "lucide-react"
import { toast } from "sonner"
import { getSessionSummary, downloadCalendar, getSessionEvents } from "@/services/api"
import { SessionSummary, CalendarEvent } from "@/types/calendar"

function GoogleIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" aria-hidden="true" {...props}>
      <path fill="#FFC107" d="M43. 6 20.5H42V20H24v8h11.3C33.7 32. 1 29.2 35 24 35c-6.1 0-11-4.9-11-11s4.9-11 11-11c2.8 0 5.4 1.1 7.4 2.9l5.7-5.7C34.1 7.1 29.3 5 24 5 13.5 5 5 13.5 5 24s8.5 19 19 19 19-8.5 19-19c0-1.2-.1-2.3-.4-3.5z" />
      <path fill="#FF3D00" d="M6. 3 14.7l6.6 4.8C14.7 16.1 18.9 13 24 13c2.8 0 5.4 1.1 7.4 2.9l5.7-5.7C34.1 7.1 29.3 5 24 5 16.7 5 10.4 9.1 6.3 14.7z" />
      <path fill="#4CAF50" d="M24 43c5.1 0 9.8-2 13.3-5.2l-6.1-5.2C29.3 34.4 26.8 35 24 35c-5.2 0-9.7-2.9-11.3-7.1l-6.5 5C10.3 39 16.6 43 24 43z" />
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-. 7 2-2 3.7-3.7 4.9l6.1 5.2C40.7 35.4 43 30 43 24c0-1.2-. 1-2.3-.4-3.5z" />
    </svg>
  )
}

function AppleIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" {...props}>
      <path
        fill="currentColor"
        d="M16. 365 1.43c0 1.14-.46 2.24-1.26 3.1-. 82.9-2.18 1.6-3.31 1.5-. 12-1.13. 43-2.3 1.2-3.15. 85-. 95 2.29-1.64 3.37-1.45ZM20.5 17.2c-. 5 1.15-.74 1.67-1.38 2.69-.9 1.42-2.16 3.18-3.74 3.2-1.4. 01-1.76-. 92-3.67-. 91-1.9. 01-2.32. 93-3.72. 92-1.58-. 02-2.79-1.62-3.69-3.04-2.52-3.98-2.78-8.64-1.23-11.03 1.1-1.72 2.84-2.72 4.47-2.72 1.7 0 2.78.93 4.2. 93 1.38 0 2.22-.94 4.18-. 94 1.45 0 2.98. 8 4.08 2.18-3.59 1.97-3.01 7.13. 5 8.72Z"
      />
    </svg>
  )
}

function OutlookIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" {...props}>
      <path fill="#0078D4" d="M3 5. 5 12 4v16l-9-1.5V5.5Z" />
      <path fill="#0A5CBD" d="M12 6h9v12h-9V6Z" />
      <path fill="#1A86E8" d="M12 6l9 6-9 6V6Z" />
      <path
        fill="#FFFFFF"
        d="M7. 3 10.3c.6 0 1.1.2 1.5.6. 4. 4.6 1 .6 1.7s-.2 1.3-.6 1.7c-. 4.4-.9. 6-1.5.6-. 6 0-1.1-. 2-1.5-.6-. 4-.4-.6-1-. 6-1.7s.2-1.3.6-1.7c.4-.4.9-.6 1.5-. 6Zm0 1c-.3 0-.5. 1-.7.3-.2.2-.3.5-.3 1s.1.8.3 1c.2.2.4.3.7.3.3 0 .5-.1.7-.3.2-.2.3-.5.3-1s-.1-. 8-.3-1c-.2-.2-.4-.3-.7-.3Z"
      />
    </svg>
  )
}

export default function ReviewPage() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('token')

  const [loading, setLoading] = React. useState(true)
  const [summary, setSummary] = React. useState<SessionSummary | null>(null)
  const [events, setEvents] = React.useState<CalendarPreviewEvent[]>([])
  const [error, setError] = React.useState<string | null>(null)

  // Fetch session data on mount
  React.useEffect(() => {
    if (!sessionId) {
      setError('No session ID provided')
      setLoading(false)
      return
    }

    async function loadSession() {
      try {
        setLoading(true)
        
        // 1. Fetch session summary (metadata)
        const summaryData = await getSessionSummary(sessionId!)
        setSummary(summaryData)
        
        // 2. Fetch actual events for calendar preview ✅ NEW! 
        const eventsData = await getSessionEvents(sessionId!)
        
        // 3. Transform to CalendarPreviewEvent format
        const previewEvents:  CalendarPreviewEvent[] = eventsData.map(event => ({
          id: event.id || '',
          title: event.title,
          start: new Date(event.startDateTime),
          end: new Date(event.endDateTime),
          location: event.location,
          recurrence: event.recurrence ? {
            frequency: event.recurrence.frequency,
            daysOfWeek: event.recurrence.daysOfWeek,
            endDate: event.recurrence.endDate
          } : undefined
        }))
        
        setEvents(previewEvents)
        setLoading(false)
        
      } catch (err:  any) {
        setError(err.message || 'Failed to load session')
        setLoading(false)
      }
    }

    loadSession()
  }, [sessionId])

  async function exportFor(provider: "google" | "apple" | "outlook") {
    if (!sessionId) {
      toast.error("No session ID")
      return
    }

    try {
      // Download . ics file from backend
      await downloadCalendar(sessionId)

      if (provider === "google") {
        toast.success("Downloaded . ics for Google Calendar", {
          description: 
            "Google Calendar → Settings → Import & export → Import → upload the .ics file you downloaded.",
        })
        return
      }

      if (provider === "apple") {
        toast.success("Downloaded .ics for Apple Calendar", {
          description:  "Open the downloaded .ics file and Calendar will import it.",
        })
        return
      }

      toast.success("Downloaded .ics for Outlook", {
        description:  "Open the downloaded .ics file or import it in Outlook Calendar.",
      })
    } catch (err: any) {
      toast.error("Export failed", {
        description: err.message || "Unknown error"
      })
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-background text-foreground">
        <div className="mx-auto max-w-6xl px-6 py-10">
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">Loading your courses...</p>
            </div>
          </div>
        </div>
      </main>
    )
  }

  if (error || !summary) {
    return (
      <main className="min-h-screen bg-background text-foreground">
        <div className="mx-auto max-w-6xl px-6 py-10">
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-6 text-center">
            <p className="text-destructive font-medium">Error loading session</p>
            <p className="text-sm text-muted-foreground mt-2">{error || 'Unknown error'}</p>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Calendar Preview</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {summary.total_courses} course(s), {summary.total_events} event(s)
            </p>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="flex items-center gap-2">
                Export
                <ChevronDown className="h-4 w-4 opacity-70" />
              </Button>
            </DropdownMenuTrigger>

            <DropdownMenuContent align="end" className="w-64 p-1">
              <DropdownMenuItem
                onClick={() => exportFor("google")}
                className="h-11 w-full gap-3 rounded-md"
              >
                <span className="grid h-8 w-8 place-items-center rounded-md border bg-background/60">
                  <GoogleIcon className="h-5 w-5" />
                </span>
                <div className="flex flex-col leading-tight">
                  <span className="text-sm font-medium">Google Calendar</span>
                  <span className="text-xs text-muted-foreground">Download . ics and import</span>
                </div>
              </DropdownMenuItem>

              <DropdownMenuItem
                onClick={() => exportFor("apple")}
                className="h-11 w-full gap-3 rounded-md"
              >
                <span className="grid h-8 w-8 place-items-center rounded-md border bg-background/60 text-foreground">
                  <AppleIcon className="h-5 w-5" />
                </span>
                <div className="flex flex-col leading-tight">
                  <span className="text-sm font-medium">Apple Calendar</span>
                  <span className="text-xs text-muted-foreground">Opens in Calendar app</span>
                </div>
              </DropdownMenuItem>

              <DropdownMenuItem
                onClick={() => exportFor("outlook")}
                className="h-11 w-full gap-3 rounded-md"
              >
                <span className="grid h-8 w-8 place-items-center rounded-md border bg-background/60">
                  <OutlookIcon className="h-5 w-5" />
                </span>
                <div className="flex flex-col leading-tight">
                  <span className="text-sm font-medium">Outlook</span>
                  <span className="text-xs text-muted-foreground">Open or import the .ics</span>
                </div>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Course Summary Cards */}
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {summary.courses.map((course, idx) => (
            <div key={idx} className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold">{course.course_code}</h3>
              <p className="text-sm text-muted-foreground">{course.course_name}</p>
              {course.semester && (
                <p className="text-xs text-muted-foreground mt-1">{course.semester}</p>
              )}
              {course.instructor && (
                <p className="text-xs text-muted-foreground">{course.instructor}</p>
              )}
              <div className="mt-3 flex items-center justify-between text-sm">
                <span className="text-muted-foreground">{course.event_count} events</span>
                {course.needs_review_count > 0 && (
                  <span className="text-yellow-600">⚠️ {course.needs_review_count} to review</span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Calendar Preview */}
        <div className="mt-6 rounded-xl bg-card text-card-foreground p-4">
          <CalendarPreview events={events} />
        </div>
      </div>
    </main>
  )
}