"use client"

import * as React from "react"
import { BackgroundPaths } from "@/components/ui/background-paths"
import { ModeToggle } from "@/components/mode-toggle"

export default function HomePage() {
  const fileInputRef = React.useRef<HTMLInputElement | null>(null)
  const [fileName, setFileName] = React.useState<string>("")

  return (
    <div className="relative">

      {/* Hidden PDF input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0]
          setFileName(file?.name ?? "")
        }}
      />

      <BackgroundPaths
        title="Course Outline to Calendar"
        onUploadClick={() => fileInputRef.current?.click()}
      />

      {/* tiny file name indicator */}
      {fileName ? (
        <div className="absolute left-1/2 bottom-6 -translate-x-1/2 z-50 rounded-full border bg-background/80 px-4 py-2 text-sm backdrop-blur">
          Selected: <span className="font-medium">{fileName}</span>
        </div>
      ) : null}
    </div>
  )
}