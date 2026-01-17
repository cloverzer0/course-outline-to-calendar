"use client"

import { ModeToggle } from "@/components/mode-toggle"

export function SiteHeader() {
  return (
    <div className="fixed right-4 top-4 z-50">
      <ModeToggle />
    </div>
  )
}
