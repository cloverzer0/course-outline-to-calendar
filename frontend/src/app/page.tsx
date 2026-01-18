"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { BackgroundPaths } from "@/components/ui/background-paths"
import FileUpload from "@/components/FileUpload"
import { uploadCourseOutlines } from "@/services/api"
import { toast } from "sonner"

export default function HomePage() {
  const router = useRouter()

  const [files, setFiles] = React.useState<File[]>([])
  const [showUploader, setShowUploader] = React.useState(false)
  const [submitting, setSubmitting] = React.useState(false)
  const fileInputRef = React.useRef<HTMLInputElement>(null)

  function openUploader() {
    // Trigger file picker directly
    fileInputRef.current?.click()
  }

  function handleFileSelection(e: React.ChangeEvent<HTMLInputElement>) {
    const selectedFiles = Array.from(e.target.files || [])
    if (selectedFiles.length > 0) {
      setFiles(selectedFiles)
      setShowUploader(true)
    }
    // Reset input so same files can be selected again if needed
    e.target.value = ''
  }

  async function handleGenerate(selected: File[]) {
    try {
      setSubmitting(true)
      const { token } = await uploadCourseOutlines(selected)

      // optional: also store locally as fallback (not required)
      // sessionStorage.setItem("upload_token", token)

      router.push(`/review?token=${encodeURIComponent(token)}`)
    } catch (err: any) {
      toast("Upload failed", { description: err?.message ?? "Unknown error" })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="relative min-h-screen">
      <BackgroundPaths
        title="Course Outline to Calendar"
        onUploadClick={openUploader}
        showUploadBox={showUploader}
      />

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        multiple
        onChange={handleFileSelection}
        className="hidden"
      />

      {/* Uploader panel */}
      {showUploader ? (
        <div className="pointer-events-auto absolute inset-x-0 bottom-6 z-50 mx-auto w-[92%] max-w-3xl">
          <FileUpload
            files={files}
            setFiles={setFiles}
            maxFiles={10}
            onSubmit={handleGenerate}
            isSubmitting={submitting}
          />
        </div>
      ) : null}
    </div>
  )
}
