export type UploadResponse = {
  token: string
}

const DEFAULT_BASE_URL = "http://localhost:8000"

function getBaseUrl(): string {
  return process.env.NEXT_PUBLIC_BACKEND_URL ?? DEFAULT_BASE_URL
}

/**
 * Upload multiple course outline PDFs to backend.
 * Backend expectation:
 *  - POST {BASE_URL}/calendar/upload
 *  - multipart/form-data with repeated field name: "files"
 *  - returns JSON: { token: "..." }
 */
export async function uploadCourseOutlines(files: File[]): Promise<UploadResponse> {
  const baseUrl = getBaseUrl()

  const form = new FormData()
  for (const f of files) form.append("files", f)

  const res = await fetch(`${baseUrl}/calendar/upload`, {
    method: "POST",
    body: form,
  })

  if (!res.ok) {
    const txt = await res.text().catch(() => "")
    throw new Error(txt || `Upload failed (${res.status})`)
  }

  const data = (await res.json()) as UploadResponse
  if (!data?.token) {
    throw new Error("Backend did not return a token.")
  }
  return data
}
