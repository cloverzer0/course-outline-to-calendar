import ICAL from "ical.js"

export type ParsedEvent = {
  uid: string
  title: string
  location?: string
  start: Date
  end?: Date
}

export function parseIcs(icsText: string): ParsedEvent[] {
  const jcalData = ICAL.parse(icsText)
  const comp = new ICAL.Component(jcalData)
  const vevents = comp.getAllSubcomponents("vevent")

  const events: ParsedEvent[] = vevents.map((v) => {
    const ev = new ICAL.Event(v)

    const start = ev.startDate?.toJSDate()
    const end = ev.endDate?.toJSDate()

    return {
      uid: ev.uid || crypto.randomUUID(),
      title: ev.summary || "Untitled event",
      location: ev.location || "",
      start,
      end,
    }
  })

  return events
    .filter((e) => e.start instanceof Date && !isNaN(e.start.getTime()))
    .sort((a, b) => a.start.getTime() - b.start.getTime())
}
