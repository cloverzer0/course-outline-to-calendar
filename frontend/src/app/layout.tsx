import type { Metadata, Viewport } from "next"


// FullCalendar global styles (pick ONE set: index.css OR main.css)
import "@/styles/fullcalendar.css"
import { SiteHeader } from "@/components/site-header"

import "@/styles/globals.css"
import { ThemeProvider } from "@/components/theme-provider"

export const metadata: Metadata = {
  title: "Course Outline → Calendar",
  description: "Upload a course outline PDF and generate an editable calendar.",
}

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <SiteHeader />
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
