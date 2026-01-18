"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

type FileUploadProps = {
  files: File[]
  setFiles: (files: File[]) => void
  accept?: string
  maxFiles?: number
  onSubmit: (files: File[]) => Promise<void>
  isSubmitting?: boolean
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  const mb = kb / 1024
  return `${mb.toFixed(1)} MB`
}

export default function FileUpload({
  files,
  setFiles,
  accept = "application/pdf",
  maxFiles = 10,
  onSubmit,
  isSubmitting = false,
}: FileUploadProps) {
  const inputRef = React.useRef<HTMLInputElement | null>(null)
  const [error, setError] = React.useState<string | null>(null)

  function openPicker() {
    setError(null)
    inputRef.current?.click()
  }

  function addFiles(newFiles: File[]) {
    setError(null)

    const onlyPdfs = newFiles.filter(
      (f) =>
        f.type === "application/pdf" ||
        f.name.toLowerCase().endsWith(".pdf"),
    )

    if (onlyPdfs.length !== newFiles.length) {
      setError("Only PDF files are allowed.")
    }

    // de-dupe by (name + size + lastModified)
    const existingKey = new Set(files.map((f) => `${f.name}-${f.size}-${f.lastModified}`))
    const merged = [...files]

    for (const f of onlyPdfs) {
      const key = `${f.name}-${f.size}-${f.lastModified}`
      if (!existingKey.has(key)) merged.push(f)
    }

    if (merged.length > maxFiles) {
      setError(`You can upload up to ${maxFiles} PDFs.`)
      setFiles(merged.slice(0, maxFiles))
      return
    }

    setFiles(merged)
  }

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const list = Array.from(e.target.files ?? [])
    addFiles(list)

    // allow re-selecting the same file later
    e.target.value = ""
  }

  function removeAt(idx: number) {
    const next = files.filter((_, i) => i !== idx)
    setFiles(next)
  }

  function clearAll() {
    setFiles([])
    setError(null)
  }

  async function handleSubmit() {
    setError(null)
    if (files.length === 0) {
      setError("Please select at least 1 PDF.")
      return
    }
    await onSubmit(files)
  }

  return (
    <Card className="w-full rounded-2xl border bg-card text-card-foreground shadow-sm">
      <div className="p-5 sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium">Upload course outline PDFs</p>
            <p className="text-xs text-muted-foreground">
              Select multiple PDFs (one per course outline).
            </p>
          </div>

          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={openPicker} disabled={isSubmitting}>
              Add PDFs
            </Button>
            <Button type="button" variant="outline" onClick={clearAll} disabled={isSubmitting || files.length === 0}>
              Clear
            </Button>
          </div>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple
          className="hidden"
          onChange={onInputChange}
        />

        {error ? (
          <div className="mt-3 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {error}
          </div>
        ) : null}

        <div className="mt-4">
          {files.length === 0 ? (
            <div className="rounded-xl border border-dashed p-6 text-center text-sm text-muted-foreground">
              No PDFs selected yet.
            </div>
          ) : (
            <div className="rounded-xl border">
              <div className="flex items-center justify-between border-b px-4 py-3">
                <p className="text-sm font-medium">
                  Selected ({files.length})
                </p>
                <p className="text-xs text-muted-foreground">
                  Max {maxFiles}
                </p>
              </div>

              <ul className="divide-y">
                {files.map((f, idx) => (
                  <li key={`${f.name}-${f.size}-${f.lastModified}`} className="flex items-center justify-between px-4 py-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{f.name}</p>
                      <p className="text-xs text-muted-foreground">{formatBytes(f.size)}</p>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      className="ml-3"
                      onClick={() => removeAt(idx)}
                      disabled={isSubmitting}
                    >
                      Remove
                    </Button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="mt-5 flex justify-end">
          <Button type="button" onClick={handleSubmit} disabled={isSubmitting || files.length === 0}>
            {isSubmitting ? "Generating…" : "Generate Calendar"}
          </Button>
        </div>
      </div>
    </Card>
  )
}

